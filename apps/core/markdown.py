"""Markdown rendering with HTML sanitisation for editor-authored content."""

from __future__ import annotations

import functools

import nh3
from markdown_it import MarkdownIt

#: Tags an editor may use in CMS pages, announcements and abstracts.
ALLOWED_TAGS: set[str] = {
    "a",
    "abbr",
    "b",
    "blockquote",
    "br",
    "caption",
    "code",
    "dd",
    "del",
    "div",
    "dl",
    "dt",
    "em",
    "figcaption",
    "figure",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "q",
    "s",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}

ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    "a": {"href", "title", "rel", "target", "id"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align", "scope"},
    "div": {"class", "id"},
    "span": {"class"},
    "h2": {"id"},
    "h3": {"id"},
    "h4": {"id"},
    "table": {"class"},
    "ol": {"start"},
}


@functools.lru_cache(maxsize=1)
def _parser() -> MarkdownIt:
    """Return a configured CommonMark parser with tables and typography."""
    md = MarkdownIt("commonmark", {"typographer": True, "linkify": True})
    md.enable(["table", "strikethrough", "linkify", "replacements", "smartquotes"])
    return md


def render_markdown(text: str | None) -> str:
    """Render ``text`` as Markdown and sanitise the resulting HTML.

    The output is safe to insert with ``|safe`` in templates: every tag and
    attribute outside :data:`ALLOWED_TAGS` / :data:`ALLOWED_ATTRIBUTES` is
    removed, and links get ``rel="noopener noreferrer"``.
    """
    if not text:
        return ""
    html = _parser().render(text)
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
    )


def strip_markdown(text: str | None, limit: int | None = None) -> str:
    """Return plain text from Markdown, useful for meta descriptions."""
    if not text:
        return ""
    plain = nh3.clean(_parser().render(text), tags=set()).strip()
    plain = " ".join(plain.split())
    if limit and len(plain) > limit:
        plain = plain[: limit - 1].rsplit(" ", 1)[0] + "…"
    return plain
