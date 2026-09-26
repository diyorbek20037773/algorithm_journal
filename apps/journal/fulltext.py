"""Reading helpers built on top of an article's sanitised HTML full text.

Two things the article page needs and the stored HTML already contains: the
section headings, which become the "In this article" contents rail, and the
figures and tables, which the "Figures & data" tab lists on their own.

Both work on the output of ``Article.full_text_html()``, which is already
sanitised, so nothing here has to defend against hostile markup.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from lxml import html as lxml_html
from lxml.etree import ParserError


@dataclass(slots=True)
class Heading:
    """One entry of the contents rail."""

    anchor: str
    text: str
    level: int
    children: list[Heading] = field(default_factory=list)


@dataclass(slots=True)
class FloatItem:
    """A figure or a table lifted out of the full text."""

    kind: str  # "figure" | "table"
    anchor: str
    label: str
    caption: str
    html: str


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str, fallback: str) -> str:
    """A short, stable anchor for a heading or a float."""
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:60] or fallback


def _parse(html: str):
    """Parse a fragment, or return None when there is nothing to parse."""
    if not html or not html.strip():
        return None
    try:
        return lxml_html.fragment_fromstring(html, create_parent="div")
    except (ParserError, ValueError):
        return None


def outline(html: str) -> list[Heading]:
    """The h2/h3 outline of the full text, with anchors written into the HTML.

    Returns the top-level headings; h3s hang off the h2 above them.
    """
    root = _parse(html)
    if root is None:
        return []
    out: list[Heading] = []
    for index, node in enumerate(root.iter("h2", "h3")):
        text = " ".join(node.text_content().split())
        if not text:
            continue
        anchor = node.get("id") or _slugify(text, f"section-{index}")
        level = 2 if node.tag == "h2" else 3
        heading = Heading(anchor=anchor, text=text, level=level)
        if level == 3 and out:
            out[-1].children.append(heading)
        else:
            out.append(heading)
    return out


def with_anchors(html: str) -> str:
    """The same HTML, with an ``id`` on every heading the rail links to."""
    root = _parse(html)
    if root is None:
        return html
    for index, node in enumerate(root.iter("h2", "h3")):
        if node.get("id"):
            continue
        text = " ".join(node.text_content().split())
        if text:
            node.set("id", _slugify(text, f"section-{index}"))
    inner = root.text or ""
    return inner + "".join(lxml_html.tostring(child, encoding="unicode") for child in root)


def floats(html: str) -> list[FloatItem]:
    """Every figure and table in the full text, in document order."""
    root = _parse(html)
    if root is None:
        return []
    out: list[FloatItem] = []
    figures = tables = 0
    for node in root.iter("figure", "table"):
        if node.tag == "figure":
            figures += 1
            number = figures
            caption_node = node.find("figcaption")
        else:
            # a table wrapped in a <figure> is already counted above
            if any(parent.tag == "figure" for parent in node.iterancestors()):
                continue
            tables += 1
            number = tables
            caption_node = node.find("caption")
        caption = " ".join(caption_node.text_content().split()) if caption_node is not None else ""
        kind = "figure" if node.tag == "figure" else "table"
        label = f"{kind.title()} {number}"
        out.append(
            FloatItem(
                kind=kind,
                anchor=node.get("id") or f"{kind}-{number}",
                label=label,
                caption=caption,
                html=lxml_html.tostring(node, encoding="unicode"),
            )
        )
    return out
