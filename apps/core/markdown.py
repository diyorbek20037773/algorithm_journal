"""Markdown rendering with HTML sanitisation for editor-authored content."""

from __future__ import annotations

import functools
import html
import re

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
    # ``rel`` is intentionally absent: nh3 sets it itself via ``link_rel``.
    "a": {"href", "title", "target", "id"},
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
    return sanitize_html(_parser().render(text))


def sanitize_html(html: str | None) -> str:
    """Strip everything outside the allow-list from ``html``.

    Used for Markdown output and for HTML full-text galleys alike. A galley is
    editorial output rather than reader input, but a typesetting tool that
    emits a stray ``<script>`` still must not be able to put it on a published
    page.
    """
    if not html:
        return ""
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


_LINK_RE = re.compile(r'<a\s[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
_BLOCK_END_RE = re.compile(r"</(p|h[1-6]|li|blockquote|tr|div)>|<br\s*/?>", re.IGNORECASE)


def markdown_to_text(text: str | None) -> str:
    """Render Markdown as the plain-text part of an e-mail.

    Unlike :func:`strip_markdown` (one line, for meta descriptions) this keeps
    paragraph breaks, writes every link as ``label: URL`` so that a reader in a
    text-only mail client can still act on it, and decodes HTML entities.
    """
    if not text:
        return ""
    rendered = _parser().render(text)

    def _link(match: re.Match[str]) -> str:
        href = html.unescape(match.group(1))
        label = nh3.clean(match.group(2), tags=set()).strip()
        if not label or html.unescape(label) == href:
            return href
        return f"{label}: {href}"

    rendered = _LINK_RE.sub(_link, rendered)
    rendered = re.sub(r"<li[^>]*>", "- ", rendered, flags=re.IGNORECASE)
    rendered = _BLOCK_END_RE.sub("\n", rendered)
    plain = html.unescape(nh3.clean(rendered, tags=set()))
    lines = [" ".join(line.split()) for line in plain.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
