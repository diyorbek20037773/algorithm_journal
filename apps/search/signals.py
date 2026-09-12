"""Keep ``Article.search_vector`` current as its source data changes.

Every model that feeds the search document is watched: the article itself,
its authors, its references, and the keyword many-to-many. Each handler only
schedules a refresh for after the transaction commits, since the rows the
document reads are not all visible until then.
"""

from __future__ import annotations

from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.journal.models import Article, Author, Reference
from apps.search.indexing import schedule_update


@receiver(post_save, sender=Article)
def _article_saved(sender, instance: Article, update_fields=None, **kwargs) -> None:
    # The indexer itself writes search_vector through .update(), which does
    # not fire post_save — but guard anyway so a future save() cannot loop.
    if update_fields and set(update_fields) == {"search_vector"}:
        return
    schedule_update(instance.pk)


@receiver(post_save, sender=Author)
@receiver(post_delete, sender=Author)
def _author_changed(sender, instance: Author, **kwargs) -> None:
    schedule_update(instance.article_id)


@receiver(post_save, sender=Reference)
@receiver(post_delete, sender=Reference)
def _reference_changed(sender, instance: Reference, **kwargs) -> None:
    schedule_update(instance.article_id)


@receiver(m2m_changed, sender=Article.keywords.through)
def _keywords_changed(sender, instance, action: str, reverse: bool, pk_set, **kwargs) -> None:
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    if reverse:
        # Changed from the Keyword side: every article it was attached to.
        for article_id in pk_set or ():
            schedule_update(article_id)
    else:
        schedule_update(instance.pk)
