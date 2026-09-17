"""Journal print layout: the typeset issue and the author offprint.

The layout follows the editorial office's InDesign sample (cover, imprint and
editorial board, an optional information page, the multilingual contents,
article pages with a running head and a page-number tab, back cover) in the
MEZON brand colours.

Artwork
    * **Cover / back cover** — an uploaded full-page picture
      (``SiteSettings.print_cover_background`` / ``print_back_cover_background``),
      darkened for legibility, or the built-in "algorithm network" artwork:
      night-ink ground, mint glow, a faint grid and a constellation of nodes.
      The front cover carries a white band with the indexing services and a QR
      code to the issue; the back cover a contact band and a QR code.
    * **Inner pages** — an uploaded pale page background
      (``print_page_background``), or a built-in decoration kept strictly in the
      outer margin so it never collides with the article text.

Article bodies are not re-typeset: each article's final PDF galley — the file
the typesetter approved — is placed page by page into the journal frame.  The
galley page is trimmed by ``PRINT_SOURCE_TRIM`` points and scaled to fit the
text area below the running head.

Everything here is pure rendering: it takes plain data classes and returns
PDF bytes.  Collecting data from the database, pagination bookkeeping and
storage live in :mod:`apps.production.issue_print`.
"""

from __future__ import annotations

import io
import math
import random
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAGE_WIDTH, PAGE_HEIGHT = A4

# Brand colours — the print twins of the site tokens in static/src/css/input.css.
INK = HexColor("#01141a")
INK_DEEP = HexColor("#000c10")
INK_2 = HexColor("#46565a")
INK_3 = HexColor("#6b7a7e")
MINT = HexColor("#3ddc97")
MINT_BRIGHT = HexColor("#84ffc1")
MINT_TEXT = HexColor("#047a4f")
MINT_INK = HexColor("#04241a")
MINT_PALE = HexColor("#e3f6ec")
MINT_LINE = HexColor("#bfe9d3")
PAPER_2 = HexColor("#eaf2ee")
LINE = HexColor("#d5e0db")
GLOW = HexColor("#0e5a43")
NET_LINE = HexColor("#1d6a52")
ON_DARK_MUTED = Color(242 / 255, 247 / 255, 245 / 255, alpha=0.72)

# Geometry of the article frame (points).
MARGIN_INNER = 45
MARGIN_OUTER = 45
HEAD_HEIGHT = 62
FOOT_HEIGHT = 58
TEXT_TOP = PAGE_HEIGHT - HEAD_HEIGHT
TEXT_BOTTOM = FOOT_HEIGHT

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT = "MezonSans"
FONT_SEMIBOLD = "MezonSans-SemiBold"
FONT_BOLD = "MezonSans-Bold"
FONT_BLACK = "MezonSans-ExtraBold"


def register_fonts() -> None:
    """Register the vendored Noto Sans instances (Latin, Cyrillic, Uzbek ʻ ғ қ ҳ)."""
    registered = set(pdfmetrics.getRegisteredFontNames())
    for name, filename in (
        (FONT, "NotoSans-Regular.ttf"),
        (FONT_SEMIBOLD, "NotoSans-SemiBold.ttf"),
        (FONT_BOLD, "NotoSans-Bold.ttf"),
        (FONT_BLACK, "NotoSans-ExtraBold.ttf"),
    ):
        if name not in registered:
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
    pdfmetrics.registerFontFamily(
        FONT, normal=FONT, bold=FONT_BOLD, italic=FONT, boldItalic=FONT_BOLD
    )


# --------------------------------------------------------------------------
# data passed in by the builder
# --------------------------------------------------------------------------


@dataclass
class BoardGroup:
    """One role group of the editorial board, e.g. "Editor-in-Chief"."""

    label: str
    members: list[tuple[str, str]]  # (name, "degree, title, affiliation")


@dataclass
class TocEntry:
    """A line of the contents: a section heading or an article."""

    title: str
    authors: str = ""
    page: int | None = None
    is_section: bool = False


@dataclass
class IssueLabels:
    """Every text and picture the frame prints, already in the print language."""

    journal_name: str
    journal_subtitle: str
    running_title: str  # "MEZON: REVIEW OF ECONOMIC RESEARCH"
    issue_line: str  # "2026-yil, sentyabr · 9-son"
    year_badge: str  # "2026"
    issue_badge: str  # "SENTYABR · 9-SON"
    edition_note: str  # "Electronic edition, September 2026."
    contents_title: str  # "MUNDARIJA"
    contents_rail: str  # "MUNDARIJA • СОДЕРЖАНИЕ • CONTENTS"
    identifiers: list[str] = field(default_factory=list)  # "e-ISSN 3060-…", "DOI 10.…"
    imprint: list[str] = field(default_factory=list)  # publisher, certificate, address
    contacts: list[tuple[str, str]] = field(default_factory=list)  # (label, value)
    licence_note: str = ""
    info_page_text: str = ""
    cover_image: bytes | None = None
    logo_image: bytes | None = None
    short_code: str = ""
    tagline: str = ""
    open_access_label: str = ""  # "OPEN ACCESS · CC BY 4.0"
    indexed_in_label: str = ""  # "Indexed in"
    indexing: list[tuple[str, bytes | None]] = field(default_factory=list)
    qr_url: str = ""
    website: str = ""
    cover_background: bytes | None = None
    back_cover_background: bytes | None = None
    page_background: bytes | None = None
    highlights_label: str = ""  # "In this issue"
    highlights: list[tuple[str, str]] = field(default_factory=list)  # (title, authors)


def _style(name: str, **kwargs) -> ParagraphStyle:
    base = {"fontName": FONT, "fontSize": 9.5, "leading": 13, "textColor": INK}
    base.update(kwargs)
    return ParagraphStyle(name, **base)


def _p(text: str) -> str:
    """Escape user text for a reportlab Paragraph."""
    return escape(text or "").replace("\n", "<br/>")


def _fit_text(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> float:
    """Largest font size ≤ ``size`` at which ``text`` fits in ``max_width``."""
    while size > 6 and pdfmetrics.stringWidth(text, font, size) > max_width:
        size -= 0.5
    return size


def _wrap_lines(text: str, font: str, size: float, width: float) -> list[str]:
    words = (text or "").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(candidate, font, size) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_spaced(
    c: canvas.Canvas, x: float, y: float, text: str, font: str, size: float, spacing: float
) -> float:
    """Draw ``text`` with letter spacing; return the width used."""
    cursor = x
    for char in text:
        c.setFont(font, size)
        c.drawString(cursor, y, char)
        cursor += pdfmetrics.stringWidth(char, font, size) + spacing
    return cursor - x


def _spaced_width(text: str, font: str, size: float, spacing: float) -> float:
    return sum(pdfmetrics.stringWidth(ch, font, size) + spacing for ch in text) - spacing


def _draw_mark(
    c: canvas.Canvas, x: float, y: float, size: float, letter: str, *, on_dark: bool = False
) -> None:
    """The square logo mark: ink tile, initial, mint dot."""
    c.setFillColor(HexColor("#0c2a2f") if on_dark else INK)
    c.roundRect(x, y, size, size, size * 0.22, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT_BLACK, size * 0.56)
    c.drawCentredString(x + size * 0.46, y + size * 0.28, (letter or "M")[:1].upper())
    c.setFillColor(MINT_BRIGHT)
    c.circle(x + size * 0.78, y + size * 0.78, size * 0.08, stroke=0, fill=1)


def _draw_image_cover(
    c: canvas.Canvas, data: bytes, x: float, y: float, w: float, h: float
) -> bool:
    """Draw ``data`` to fill the box (crop to cover); False when unreadable."""
    try:
        image = ImageReader(io.BytesIO(data))
        iw, ih = image.getSize()
    except Exception:
        return False
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    path = c.beginPath()
    path.rect(x, y, w, h)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")
    c.restoreState()
    return True


def _draw_image_contain(
    c: canvas.Canvas, data: bytes, x: float, y: float, w: float, h: float
) -> bool:
    """Draw ``data`` inside the box keeping its proportions; False when unreadable."""
    try:
        image = ImageReader(io.BytesIO(data))
        iw, ih = image.getSize()
    except Exception:
        return False
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")
    return True


def _draw_qr(
    c: canvas.Canvas, url: str, x: float, y: float, size: float, *, dark: Color = INK
) -> None:
    """A QR code for ``url`` with a white quiet zone."""
    widget = QrCodeWidget(url, barLevel="M")
    x0, y0, x1, y1 = widget.getBounds()
    width, height = x1 - x0, y1 - y0
    widget.barFillColor = dark
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(widget)
    c.setFillColor(white)
    c.roundRect(x - 4, y - 4, size + 8, size + 8, 6, stroke=0, fill=1)
    renderPDF.draw(drawing, c, x, y)


# --------------------------------------------------------------------------
# generative artwork
# --------------------------------------------------------------------------


def _network(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    seed: int,
    count: int,
    line_color: Color,
    node_color: Color,
    accent_color: Color | None = None,
    line_width: float = 0.6,
    links: int = 2,
) -> None:
    """A deterministic constellation: nodes joined to their nearest neighbours."""
    rng = random.Random(seed)
    points = [(x + rng.random() * w, y + rng.random() * h) for _ in range(count)]
    c.saveState()
    c.setStrokeColor(line_color)
    c.setLineWidth(line_width)
    drawn: set[tuple[int, int]] = set()
    for index, (px, py) in enumerate(points):
        nearest = sorted(
            (math.hypot(px - qx, py - qy), other)
            for other, (qx, qy) in enumerate(points)
            if other != index
        )[:links]
        for _distance, other in nearest:
            key = (min(index, other), max(index, other))
            if key in drawn:
                continue
            drawn.add(key)
            qx, qy = points[other]
            c.line(px, py, qx, qy)
    for index, (px, py) in enumerate(points):
        radius = 1.2 + rng.random() * 2.2
        c.setFillColor(accent_color if accent_color is not None and index % 7 == 0 else node_color)
        c.circle(px, py, radius, stroke=0, fill=1)
    c.restoreState()


def _draw_dark_ground(c: canvas.Canvas, *, seed: int, background: bytes | None) -> None:
    """Night palette ground: an uploaded picture (darkened) or the network artwork."""
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    if background and _draw_image_cover(c, background, 0, 0, PAGE_WIDTH, PAGE_HEIGHT):
        c.saveState()
        c.setFillColor(INK)
        c.setFillAlpha(0.5)
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
        c.setFillAlpha(0.35)
        c.rect(0, 0, PAGE_WIDTH * 0.62, PAGE_HEIGHT, stroke=0, fill=1)
        c.restoreState()
        return

    # PDF shadings ignore alpha, so the glow fades between two opaque colours
    # and extends: past the radius it is plain ink with no visible edge.
    c.saveState()
    path = c.beginPath()
    path.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT)
    c.clipPath(path, stroke=0, fill=0)
    c.radialGradient(
        PAGE_WIDTH * 0.85,
        PAGE_HEIGHT * 0.95,
        PAGE_WIDTH * 1.05,
        (GLOW, INK),
        positions=(0, 1),
        extend=True,
    )
    c.restoreState()
    c.setStrokeColor(Color(1, 1, 1, alpha=0.045))
    c.setLineWidth(0.5)
    step = 28
    x = 0.0
    while x <= PAGE_WIDTH:
        c.line(x, 0, x, PAGE_HEIGHT)
        x += step
    y = 0.0
    while y <= PAGE_HEIGHT:
        c.line(0, y, PAGE_WIDTH, y)
        y += step
    _network(
        c,
        PAGE_WIDTH * 0.32,
        PAGE_HEIGHT * 0.42,
        PAGE_WIDTH * 0.72,
        PAGE_HEIGHT * 0.6,
        seed=seed,
        count=46,
        line_color=NET_LINE,
        node_color=HexColor("#2f9c76"),
        accent_color=MINT_BRIGHT,
        line_width=0.7,
    )


def _draw_page_ground(c: canvas.Canvas, labels: IssueLabels, *, odd: bool) -> None:
    """Background of an inner page: the uploaded picture or margin decoration."""
    if labels.page_background and _draw_image_cover(
        c, labels.page_background, 0, 0, PAGE_WIDTH, PAGE_HEIGHT
    ):
        return
    # a pale mint strip on the outer edge with a small constellation in it
    strip = 9
    edge_x = PAGE_WIDTH - strip if odd else 0
    c.setFillColor(MINT_PALE)
    c.rect(edge_x, 0, strip, PAGE_HEIGHT, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.rect(edge_x if odd else strip - 2, PAGE_HEIGHT * 0.62, 2, PAGE_HEIGHT * 0.2, stroke=0, fill=1)
    net_w = MARGIN_OUTER - strip - 12
    net_x = PAGE_WIDTH - strip - net_w - 6 if odd else strip + 6
    _network(
        c,
        net_x,
        PAGE_HEIGHT * 0.55,
        net_w,
        PAGE_HEIGHT * 0.3,
        seed=7 if odd else 11,
        count=9,
        line_color=MINT_LINE,
        node_color=MINT_LINE,
        line_width=0.5,
        links=1,
    )


@lru_cache(maxsize=4)
def _page_ground_pdf(page_background: bytes | None, odd: bool) -> bytes:
    labels = IssueLabels("", "", "", "", "", "", "", "", "", page_background=page_background)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_page_ground(c, labels, odd=odd)
    c.showPage()
    c.save()
    return buffer.getvalue()


# --------------------------------------------------------------------------
# running head and page-number tab
# --------------------------------------------------------------------------


def draw_page_chrome(
    c: canvas.Canvas,
    labels: IssueLabels,
    page_number: int,
    *,
    footer_note: str = "",
) -> None:
    """Running head, mint rule and the page-number tab on the outer edge.

    Even pages carry the number on the left, odd pages on the right, as in a
    bound journal.
    """
    odd = page_number % 2 == 1
    left = MARGIN_INNER
    right = PAGE_WIDTH - MARGIN_OUTER
    base_y = PAGE_HEIGHT - 40
    mark = 16
    size = _fit_text(c, labels.running_title, FONT_BLACK, 8.5, 300)
    if odd:
        _draw_mark(c, right - mark, base_y - 4, mark, labels.journal_name)
        c.setFillColor(INK)
        c.setFont(FONT_BLACK, size)
        c.drawRightString(right - mark - 8, base_y, labels.running_title)
        c.setFillColor(MINT_TEXT)
        c.setFont(FONT_SEMIBOLD, 8)
        c.drawString(left, base_y, labels.issue_line)
    else:
        _draw_mark(c, left, base_y - 4, mark, labels.journal_name)
        c.setFillColor(INK)
        c.setFont(FONT_BLACK, size)
        c.drawString(left + mark + 8, base_y, labels.running_title)
        c.setFillColor(MINT_TEXT)
        c.setFont(FONT_SEMIBOLD, 8)
        c.drawRightString(right, base_y, labels.issue_line)

    # rule: mint on the outer two thirds, pale towards the spine
    rule_y = base_y - 10
    c.setLineWidth(1.2)
    split = left + (right - left) / 3
    if odd:
        c.setStrokeColor(MINT_LINE)
        c.line(left, rule_y, split, rule_y)
        c.setStrokeColor(MINT)
        c.line(split, rule_y, right, rule_y)
    else:
        c.setStrokeColor(MINT)
        c.line(left, rule_y, right - (split - left), rule_y)
        c.setStrokeColor(MINT_LINE)
        c.line(right - (split - left), rule_y, right, rule_y)
    c.setFillColor(MINT)
    c.circle(right if odd else left, rule_y, 2.2, stroke=0, fill=1)

    # page-number tab bleeding off the outer edge
    tab_w, tab_h, tab_y = 62, 22, 22
    c.setFillColor(INK)
    if odd:
        c.roundRect(PAGE_WIDTH - tab_w, tab_y, tab_w + 12, tab_h, 11, stroke=0, fill=1)
        c.setFillColor(MINT_BRIGHT)
        c.circle(PAGE_WIDTH - tab_w + 11, tab_y + tab_h / 2, 3, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont(FONT_BLACK, 10)
        c.drawCentredString(PAGE_WIDTH - tab_w / 2 + 6, tab_y + 7, str(page_number))
    else:
        c.roundRect(-12, tab_y, tab_w + 12, tab_h, 11, stroke=0, fill=1)
        c.setFillColor(MINT_BRIGHT)
        c.circle(tab_w - 11, tab_y + tab_h / 2, 3, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont(FONT_BLACK, 10)
        c.drawCentredString(tab_w / 2 - 6, tab_y + 7, str(page_number))

    if footer_note:
        c.setFillColor(INK_3)
        size = _fit_text(c, footer_note, FONT, 7, PAGE_WIDTH - 2 * (tab_w + 20))
        c.setFont(FONT, size)
        c.drawCentredString(PAGE_WIDTH / 2, tab_y + 8, footer_note)


def chrome_overlay(labels: IssueLabels, page_number: int, footer_note: str = "") -> bytes:
    """A one-page transparent PDF with only the running head and tab."""
    register_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    draw_page_chrome(c, labels, page_number, footer_note=footer_note)
    c.showPage()
    c.save()
    return buffer.getvalue()


# --------------------------------------------------------------------------
# cover and back cover
# --------------------------------------------------------------------------


def render_cover(labels: IssueLabels) -> bytes:
    """Front cover: the uploaded issue cover, or the designed brand cover."""
    register_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    if labels.cover_image and _draw_image_cover(
        c, labels.cover_image, 0, 0, PAGE_WIDTH, PAGE_HEIGHT
    ):
        c.showPage()
        c.save()
        return buffer.getvalue()

    seed = sum(ord(ch) for ch in labels.issue_badge + labels.year_badge)
    _draw_dark_ground(c, seed=seed, background=labels.cover_background)
    margin = 44
    width = PAGE_WIDTH - 2 * margin

    # masthead row
    top = PAGE_HEIGHT - margin
    if labels.logo_image and _draw_image_contain(c, labels.logo_image, margin, top - 44, 160, 44):
        pass
    else:
        _draw_mark(c, margin, top - 38, 38, labels.journal_name, on_dark=True)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(margin + 50, top - 16, labels.short_code or labels.journal_name)
        c.setFillColor(ON_DARK_MUTED)
        c.setFont(FONT, 8)
        c.drawString(margin + 50, top - 30, labels.edition_note)
    if labels.open_access_label:
        size = 7.5
        text_w = _spaced_width(labels.open_access_label, FONT_BOLD, size, 1.2)
        pill_w = text_w + 28
        px = PAGE_WIDTH - margin - pill_w
        c.setStrokeColor(MINT_BRIGHT)
        c.setLineWidth(0.9)
        c.roundRect(px, top - 30, pill_w, 22, 11, stroke=1, fill=0)
        c.setFillColor(MINT_BRIGHT)
        c.circle(px + 11, top - 19, 2.6, stroke=0, fill=1)
        _draw_spaced(c, px + 19, top - 22, labels.open_access_label, FONT_BOLD, size, 1.2)

    # title block
    size = 64
    name = labels.journal_name.upper()
    name_lines = _wrap_lines(name, FONT_BLACK, size, width)
    while (
        len(name_lines) > 2
        or any(pdfmetrics.stringWidth(n, FONT_BLACK, size) > width for n in name_lines)
    ) and size > 28:
        size -= 3
        name_lines = _wrap_lines(name, FONT_BLACK, size, width)
    y = PAGE_HEIGHT - 170
    c.setFillColor(white)
    for line in name_lines:
        c.setFont(FONT_BLACK, size)
        c.drawString(margin - 2, y, line)
        y -= size * 1.0
    c.setFillColor(MINT)
    c.roundRect(margin, y + size * 0.52, 84, 6, 3, stroke=0, fill=1)
    c.setFillColor(MINT_BRIGHT)
    c.circle(margin + 96, y + size * 0.52 + 3, 3, stroke=0, fill=1)
    y -= 8
    c.setFillColor(white)
    for line in _wrap_lines(labels.journal_subtitle, FONT_BOLD, 20, width * 0.85)[:2]:
        c.setFont(FONT_BOLD, 20)
        c.drawString(margin, y, line)
        y -= 26
    c.setFillColor(ON_DARK_MUTED)
    for line in _wrap_lines(labels.tagline, FONT, 11.5, width * 0.62)[:3]:
        c.setFont(FONT, 11.5)
        c.drawString(margin, y - 4, line)
        y -= 16
    if labels.identifiers:
        c.setFillColor(MINT_BRIGHT)
        c.setFont(FONT_SEMIBOLD, 9)
        c.drawString(margin, y - 14, "   ·   ".join(labels.identifiers[:3]))

    # issue badge
    badge_w, badge_h = 236, 118
    bx, by = PAGE_WIDTH - margin - badge_w, PAGE_HEIGHT * 0.37
    c.setFillColor(MINT_BRIGHT)
    c.roundRect(bx, by, badge_w, badge_h, 20, stroke=0, fill=1)
    c.setFillColor(MINT_INK)
    c.roundRect(bx + 16, by + badge_h - 12, 40, 3, 1.5, stroke=0, fill=1)
    c.setFont(FONT_BLACK, 54)
    c.drawCentredString(bx + badge_w / 2, by + 50, labels.year_badge)
    size = _fit_text(c, labels.issue_badge, FONT_BLACK, 16, badge_w - 28)
    c.setFont(FONT_BLACK, size)
    c.drawCentredString(bx + badge_w / 2, by + 22, labels.issue_badge)

    # "in this issue": the first articles, left of the badge and below it
    if labels.highlights:
        column_w = bx - margin - 28
        y = by + badge_h - 8
        c.setFillColor(MINT_BRIGHT)
        _draw_spaced(c, margin, y, labels.highlights_label.upper(), FONT_BOLD, 7.5, 1.4)
        y -= 20
        floor = 132
        for title, authors in labels.highlights:
            title_lines = _wrap_lines(title, FONT_SEMIBOLD, 10.5, column_w)[:2]
            needed = 14 * len(title_lines) + (12 if authors else 0) + 12
            if y - needed < floor:
                break
            c.setStrokeColor(MINT)
            c.setLineWidth(2)
            c.line(margin, y + 9, margin, y + 9 - needed + 10)
            for line in title_lines:
                c.setFillColor(white)
                c.setFont(FONT_SEMIBOLD, 10.5)
                c.drawString(margin + 10, y, line)
                y -= 14
            if authors:
                c.setFillColor(MINT_BRIGHT)
                c.setFont(FONT, 8.5)
                c.drawString(margin + 10, y, authors[:70])
                y -= 12
            y -= 12
            column_w = width if y < by - 10 else column_w

    # white band: indexing services, website, QR code
    band_h = 108
    c.setFillColor(white)
    c.rect(0, 0, PAGE_WIDTH, band_h, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.rect(0, band_h, PAGE_WIDTH, 4, stroke=0, fill=1)
    qr_size = 64
    if labels.qr_url:
        _draw_qr(c, labels.qr_url, PAGE_WIDTH - margin - qr_size, (band_h - qr_size) / 2, qr_size)
    right_limit = PAGE_WIDTH - margin - (qr_size + 20 if labels.qr_url else 0)
    c.setFillColor(INK_3)
    c.setFont(FONT_BOLD, 7)
    if labels.indexing:
        _draw_spaced(c, margin, band_h - 24, labels.indexed_in_label.upper(), FONT_BOLD, 7, 1.1)
        cursor = margin
        slot_h = 30
        for name, logo in labels.indexing:
            if cursor > right_limit - 60:
                break
            if logo and _draw_image_contain(c, logo, cursor, 34, 86, slot_h):
                cursor += 98
                continue
            text_size = 11
            text_w = pdfmetrics.stringWidth(name, FONT_BLACK, text_size)
            if cursor + text_w + 20 > right_limit:
                break
            c.setFillColor(PAPER_2)
            c.roundRect(cursor, 38, text_w + 20, 24, 12, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont(FONT_BLACK, text_size)
            c.drawString(cursor + 10, 46, name)
            cursor += text_w + 30
    if labels.website:
        c.setFillColor(MINT_TEXT)
        c.setFont(FONT_BOLD, 9)
        c.drawString(margin, 16, labels.website)
    c.showPage()
    c.save()
    return buffer.getvalue()


def render_back_cover(labels: IssueLabels) -> bytes:
    """Back cover: about text, QR code and a contact band on the night palette."""
    register_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_dark_ground(c, seed=97, background=labels.back_cover_background)
    margin = 44
    width = PAGE_WIDTH - 2 * margin

    _draw_mark(c, margin, PAGE_HEIGHT - margin - 44, 44, labels.journal_name, on_dark=True)
    c.setFillColor(white)
    name_size = _fit_text(c, labels.journal_name.upper(), FONT_BLACK, 26, width - 60)
    c.setFont(FONT_BLACK, name_size)
    c.drawString(margin + 58, PAGE_HEIGHT - margin - 22, labels.journal_name.upper())
    c.setFillColor(ON_DARK_MUTED)
    c.setFont(FONT_SEMIBOLD, 10)
    c.drawString(margin + 58, PAGE_HEIGHT - margin - 38, labels.journal_subtitle[:80])

    # about + QR panel
    panel_y, panel_h = 250, 190
    c.saveState()
    c.setFillColor(INK_DEEP)
    c.setFillAlpha(0.72)
    c.roundRect(margin, panel_y, width, panel_h, 18, stroke=0, fill=1)
    c.restoreState()
    c.setStrokeColor(Color(1, 1, 1, alpha=0.12))
    c.setLineWidth(0.8)
    c.roundRect(margin, panel_y, width, panel_h, 18, stroke=1, fill=0)
    qr_size = 110
    text_w = width - 48 - (qr_size + 28 if labels.qr_url else 0)
    y = panel_y + panel_h - 36
    c.setFillColor(MINT_BRIGHT)
    c.roundRect(margin + 24, y + 14, 36, 4, 2, stroke=0, fill=1)
    c.setFillColor(white)
    for line in _wrap_lines(labels.tagline or labels.journal_subtitle, FONT_BOLD, 14, text_w)[:4]:
        c.setFont(FONT_BOLD, 14)
        c.drawString(margin + 24, y - 6, line)
        y -= 20
    c.setFillColor(ON_DARK_MUTED)
    for line in _wrap_lines(labels.licence_note, FONT, 8.5, text_w)[:4]:
        c.setFont(FONT, 8.5)
        c.drawString(margin + 24, y - 12, line)
        y -= 12
    if labels.qr_url:
        _draw_qr(
            c,
            labels.qr_url,
            margin + width - 24 - qr_size,
            panel_y + (panel_h - qr_size) / 2,
            qr_size,
        )

    # contact band
    band_h = 150
    c.setFillColor(INK_DEEP)
    c.rect(0, 0, PAGE_WIDTH, band_h, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.rect(0, band_h, PAGE_WIDTH, 3, stroke=0, fill=1)
    items = labels.contacts[:4]
    if items:
        col_w = width / len(items)
        for index, (label, value) in enumerate(items):
            cx = margin + index * col_w
            c.setFillColor(MINT_BRIGHT)
            c.circle(cx + 10, band_h - 40, 10, stroke=0, fill=1)
            c.setFillColor(MINT_INK)
            c.setFont(FONT_BLACK, 9)
            c.drawCentredString(cx + 10, band_h - 43, (label or "•")[:1].upper())
            c.setFillColor(ON_DARK_MUTED)
            _draw_spaced(c, cx, band_h - 70, label.upper(), FONT_BOLD, 6.5, 1)
            c.setFillColor(white)
            value_size = _fit_text(c, value, FONT_SEMIBOLD, 9.5, col_w - 10)
            c.setFont(FONT_SEMIBOLD, value_size)
            c.drawString(cx, band_h - 86, value)
    c.setFillColor(ON_DARK_MUTED)
    c.setFont(FONT, 7.5)
    for index, line in enumerate(labels.identifiers[:3]):
        c.drawString(margin, 40 - index * 11, line)
    c.showPage()
    c.save()
    return buffer.getvalue()


# --------------------------------------------------------------------------
# flowing front matter: board, information page, contents
# --------------------------------------------------------------------------


def _flow_document(
    story: list,
    labels: IssueLabels,
    *,
    first_page_number: int | None,
    top_extra: float = 0,
    rail: str = "",
    decorate_head: bool = False,
) -> bytes:
    """Lay ``story`` out on A4 with the inner-page ground; numbered pages get the chrome."""
    buffer = io.BytesIO()

    def on_page(c: canvas.Canvas, doc) -> None:
        number = (first_page_number or 1) + doc.page - 1
        odd = number % 2 == 1 if first_page_number is not None else True
        _draw_page_ground(c, labels, odd=odd)
        if decorate_head:
            _network(
                c,
                PAGE_WIDTH * 0.63,
                PAGE_HEIGHT - 175,
                PAGE_WIDTH * 0.3,
                105,
                seed=23,
                count=16,
                line_color=MINT_LINE,
                node_color=MINT_LINE,
                accent_color=MINT,
                line_width=0.5,
            )
        if rail:
            c.saveState()
            c.setFillColor(MINT_LINE)
            size = 15
            length = _spaced_width(rail, FONT_BLACK, size, 3)
            c.translate(
                MARGIN_INNER - 16 if odd else PAGE_WIDTH - MARGIN_OUTER + 28,
                (PAGE_HEIGHT - length) / 2,
            )
            c.rotate(90)
            _draw_spaced(c, 0, 0, rail, FONT_BLACK, size, 3)
            c.restoreState()
        if first_page_number is not None:
            draw_page_chrome(c, labels, number)

    left = MARGIN_INNER + (10 if rail else 0)
    frame = Frame(
        left,
        TEXT_BOTTOM,
        PAGE_WIDTH - left - MARGIN_OUTER,
        TEXT_TOP - TEXT_BOTTOM - top_extra,
        leftPadding=0,
        rightPadding=0,
        topPadding=6,
        bottomPadding=0,
    )
    doc = BaseDocTemplate(buffer, pagesize=A4, title=labels.journal_name)
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=on_page)])
    doc.build(story)
    return buffer.getvalue()


def render_board(labels: IssueLabels, groups: Iterable[BoardGroup]) -> bytes:
    """Imprint page: journal block, editorial board by role, publisher details."""
    register_fonts()
    title = _style("title", fontName=FONT_BLACK, fontSize=26, leading=28, textColor=white)
    subtitle = _style("subtitle", fontSize=9, leading=12, textColor=ON_DARK_MUTED)
    role = _style(
        "role", fontName=FONT_BOLD, fontSize=10, leading=13, textColor=MINT_TEXT, spaceBefore=9
    )
    member = _style("member", fontSize=8.8, leading=11.6, textColor=INK_2)
    note = _style(
        "note",
        fontName=FONT_SEMIBOLD,
        fontSize=8.5,
        leading=11,
        textColor=MINT_TEXT,
        alignment=TA_RIGHT,
    )
    small = _style("small", fontSize=7.8, leading=10.5, textColor=INK_3)

    masthead = Table(
        [
            [Paragraph(_p(labels.journal_name), title)],
            [
                Paragraph(
                    _p(" ".join(filter(None, [labels.journal_subtitle, labels.tagline]))), subtitle
                )
            ],
        ],
        colWidths=[300],
    )
    masthead.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), INK),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (0, 0), 16),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
                ("LINEBELOW", (0, -1), (-1, -1), 4, MINT),
                ("ROUNDEDCORNERS", [10, 10, 10, 10]),
            ]
        )
    )
    head = Table(
        [[masthead, Paragraph(_p(labels.edition_note), note)]],
        colWidths=[310, PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER - 310],
    )
    head.setStyle(
        TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)])
    )
    story: list = [head, Spacer(1, 14)]
    for group in groups:
        if not group.members:
            continue
        story.append(Paragraph(_p(group.label), role))
        for name, details in group.members:
            text = f"<b><font color='#01141a'>{_p(name)}</font></b>"
            if details:
                text += f", {_p(details)}"
            story.append(Paragraph(text, member))
    if labels.imprint or labels.identifiers:
        story.append(Spacer(1, 16))
        rule = Table([[""]], colWidths=[PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER], rowHeights=[1])
        rule.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, LINE)]))
        story.append(rule)
        story.append(Spacer(1, 6))
        for line in [*labels.identifiers, *labels.imprint, labels.licence_note]:
            if line:
                story.append(Paragraph(_p(line), small))
    return _flow_document(story, labels, first_page_number=None, top_extra=-24, decorate_head=True)


def render_info_page(labels: IssueLabels) -> bytes:
    """Free-text page from site settings (e.g. accredited specialities)."""
    register_fonts()
    heading = _style(
        "heading", fontName=FONT_BLACK, fontSize=15, leading=19, spaceBefore=6, spaceAfter=6
    )
    body = _style("body", fontSize=9.5, leading=13.5, textColor=INK_2, spaceAfter=3)
    story: list = []
    for raw in labels.info_page_text.splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("#"):
            story.append(Paragraph(_p(line.lstrip("# ")), heading))
        else:
            story.append(Paragraph(_p(line), body))
    return _flow_document(story or [Spacer(1, 1)], labels, first_page_number=None, top_extra=-24)


def render_contents(labels: IssueLabels, entries: list[TocEntry], first_page_number: int) -> bytes:
    """The contents pages, numbered from ``first_page_number``."""
    register_fonts()
    heading = _style(
        "toc-heading", fontName=FONT_BLACK, fontSize=34, leading=38, textColor=INK, spaceAfter=2
    )
    rail = _style(
        "toc-rail", fontName=FONT_BOLD, fontSize=8, leading=10, textColor=MINT_TEXT, spaceAfter=16
    )
    title = _style("toc-title", fontName=FONT_SEMIBOLD, fontSize=9.2, leading=12, textColor=INK)
    authors = _style(
        "toc-authors", fontName=FONT_BOLD, fontSize=8.6, leading=11, textColor=MINT_TEXT
    )
    page = _style(
        "toc-page", fontName=FONT_BLACK, fontSize=10, leading=12, textColor=INK, alignment=TA_RIGHT
    )
    section = _style(
        "toc-section", fontName=FONT_BOLD, fontSize=8.5, leading=11, textColor=MINT_INK
    )

    width = PAGE_WIDTH - MARGIN_INNER - 10 - MARGIN_OUTER
    story: list = [
        Paragraph(_p(labels.contents_title), heading),
        Paragraph(_p(labels.contents_rail), rail),
    ]
    for entry in entries:
        if entry.is_section:
            row = Table([[Paragraph(_p(entry.title.upper()), section)]], colWidths=[width])
            row.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), MINT_BRIGHT),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
                    ]
                )
            )
            story.extend([Spacer(1, 8), row, Spacer(1, 4)])
            continue
        cell = [Paragraph(_p(entry.title.upper()), title)]
        if entry.authors:
            cell.append(Paragraph(_p(entry.authors), authors))
        number = "" if entry.page is None else str(entry.page)
        row = Table([[cell, Paragraph(number, page)]], colWidths=[width - 44, 44])
        row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE, None, (1, 2)),
                ]
            )
        )
        story.append(KeepTogether(row))
    return _flow_document(
        story, labels, first_page_number=first_page_number, rail=labels.contents_rail
    )


# --------------------------------------------------------------------------
# article pages
# --------------------------------------------------------------------------


def place_article_pages(
    source_pdf: bytes,
    labels: IssueLabels,
    first_page_number: int,
    *,
    trim: float = 18.0,
    footer_note: str = "",
):
    """Yield journal pages built from the galley pages of one article.

    Each page is the inner-page ground, then the trimmed galley page scaled to
    the text area and centred under the running head, then the chrome.
    """
    from pypdf import PageObject, PdfReader, Transformation

    reader = PdfReader(io.BytesIO(source_pdf))
    grounds = {
        odd: PdfReader(io.BytesIO(_page_ground_pdf(labels.page_background, odd))).pages[0]
        for odd in (True, False)
    }
    area_w = PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER
    area_h = TEXT_TOP - TEXT_BOTTOM - 6
    for index, source in enumerate(reader.pages):
        if (source.get("/Rotate") or 0) % 360:
            source.transfer_rotation_to_content()
        box = source.cropbox
        src_x, src_y = float(box.left) + trim, float(box.bottom) + trim
        src_w = max(float(box.width) - 2 * trim, 1.0)
        src_h = max(float(box.height) - 2 * trim, 1.0)
        scale = min(area_w / src_w, area_h / src_h)
        offset_x = MARGIN_INNER + (area_w - src_w * scale) / 2
        offset_y = TEXT_BOTTOM + area_h - src_h * scale
        number = first_page_number + index
        page = PageObject.create_blank_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        page.merge_page(grounds[number % 2 == 1])
        transform = (
            Transformation().translate(-src_x, -src_y).scale(scale).translate(offset_x, offset_y)
        )
        page.merge_transformed_page(source, transform, over=True, expand=False)
        overlay = PdfReader(io.BytesIO(chrome_overlay(labels, number, footer_note))).pages[0]
        page.merge_page(overlay)
        yield page


def page_count(pdf_bytes: bytes) -> int:
    """Number of pages in a PDF."""
    from pypdf import PdfReader

    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


__all__ = [
    "BoardGroup",
    "IssueLabels",
    "TocEntry",
    "page_count",
    "place_article_pages",
    "register_fonts",
    "render_back_cover",
    "render_board",
    "render_contents",
    "render_cover",
    "render_info_page",
]
