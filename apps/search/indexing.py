"""Maintain the stored, indexed search document for each article.

Why this exists
---------------
The first search implementation built its ``SearchVector`` inline, joining
``keywords``, ``authors`` and ``references`` in one query. That is a Cartesian
product: with fourteen articles, six keywords, three authors and thirty
references each, Postgres computed ``to_tsvector`` over roughly a hundred
thousand rows on every search and took eight seconds — under load, one search
held a gunicorn worker for eight seconds and everything behind it queued. At
five hundred articles it would have been minutes.

The document is now built once per article, stored in ``Article.search_vector``
and covered by a GIN index, so a search is an index lookup whatever the size of
the archive. Everything that feeds the document — the article itself, its
authors, keywords and references — refreshes it through the signals below.

The vector uses the ``simple`` configuration across every language variant of
title, abstract and keywords, because one column has to serve four interface
languages and Uzbek has no stemmer in Postgres anyway. The cost is that English
stemming is lost ("policies" does not match "policy"); the ``websearch`` query
parser still handles phrases, ``OR`` and ``-exclusion``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.postgres.search import SearchVector
from django.db.models import Value

if TYPE_CHECKING:
    from apps.journal.models import Article

#: One text search configuration for every language; see the module docstring.
SEARCH_CONFIG = "simple"

#: Translated fields folded into the document, in weight order.
TITLE_FIELDS = ("title_en", "title_uz", "title_uz_cyrl", "title_ru", "subtitle")
ABSTRACT_FIELDS = ("abstract_en", "abstract_uz", "abstract_uz_cyrl", "abstract_ru")


def _join(values) -> str:
    return " ".join(str(v).strip() for v in values if v)


def build_document(article: Article) -> dict[str, str]:
    """Collect the text that goes into each weight band of the vector."""
    keywords = article.keywords.all()
    authors = article.authors.all()
    references = article.references.all()
    return {
        "A": _join(getattr(article, f, "") for f in TITLE_FIELDS),
        "B": _join(
            [getattr(article, f, "") for f in ABSTRACT_FIELDS]
            + [k.name for k in keywords]
            + [getattr(k, "name_uz", "") for k in keywords]
            + [getattr(k, "name_ru", "") for k in keywords]
        ),
        "C": _join(
            [a.family_name for a in authors]
            + [a.given_name for a in authors]
            + [a.affiliation for a in authors]
            + [article.doi or ""]
        ),
        "D": _join(r.raw_text for r in references),
    }


def update_article_vector(article_id: int) -> None:
    """Recompute and store the search vector for one article.

    Runs as a single ``UPDATE`` with ``Value()`` operands, so no relation is
    joined at query time — that join is exactly what this module replaces.
    """
    from apps.journal.models import Article

    article = (
        Article.objects.filter(pk=article_id)
        .prefetch_related("keywords", "authors", "references")
        .first()
    )
    if article is None:
        return
    document = build_document(article)
    vector = None
    for weight, text in document.items():
        if not text:
            continue
        part = SearchVector(Value(text), weight=weight, config=SEARCH_CONFIG)
        vector = part if vector is None else vector + part
    Article.objects.filter(pk=article_id).update(search_vector=vector)


def schedule_update(article_id: int | None) -> None:
    """Refresh the vector now, inside the caller's transaction.

    Synchronous on purpose. The rows the document reads were written on this
    same connection, so they are visible even before commit; and if the
    transaction rolls back, the vector rolls back with it, which is exactly
    right. ``transaction.on_commit`` would be neater for a batch of edits, but
    it never fires inside a test transaction, and behaviour that cannot be
    tested is behaviour that quietly breaks.
    """
    if article_id is None:
        return
    update_article_vector(article_id)


def rebuild_all() -> int:
    """Recompute every article's vector; returns how many were updated."""
    from apps.journal.models import Article

    count = 0
    for article_id in Article.objects.values_list("pk", flat=True).iterator():
        update_article_vector(article_id)
        count += 1
    return count
