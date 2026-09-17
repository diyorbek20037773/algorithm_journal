"""Journal print layout: the typeset issue and the author offprint.

The layout follows the editorial office's InDesign sample (cover, imprint and
editorial board, an optional information page, the multilingual contents,
article pages with a running head and a page-number tab, back cover) in the
MEZON brand colours.

Article bodies are not re-typeset: each article's final PDF galley — the file
the typesetter approved — is placed page by page into the journal frame.  The
galley page is trimmed by ``PRINT_SOURCE_TRIM`` points and scaled to fit the
text area below the running head, so any A4/Letter PDF exported from Word or
InDesign drops into the template without manual work.

Everything here is pure rendering: it takes plain data classes and returns
PDF bytes.  Collecting data from the database, pagination bookkeeping and
storage live in :mod:`apps.production.issue_print`.
"""

from __future__ import annotations

import io
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

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
INK_2 = HexColor("#46565a")
INK_3 = HexColor("#6b7a7e")
MINT = HexColor("#3ddc97")
MINT_BRIGHT = HexColor("#84ffc1")
MINT_TEXT = HexColor("#047a4f")
MINT_INK = HexColor("#04241a")
PAPER_2 = HexColor("#eaf2ee")
LINE = HexColor("#d5e0db")
GLOW = HexColor("#0e5a43")
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
    """Every text the frame prints, already translated into the print language."""

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
    contacts: list[str] = field(default_factory=list)  # phone, e-mail, web
    licence_note: str = ""
    info_page_text: str = ""
    cover_image: bytes | None = None
    logo_image: bytes | None = None
    short_code: str = ""
    tagline: str = ""


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


def _draw_mark(c: canvas.Canvas, x: float, y: float, size: float, letter: str) -> None:
    """The square logo mark: dark ink tile, initial, mint dot."""
    c.setFillColor(INK)
    c.roundRect(x, y, size, size, size * 0.22, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT_BLACK, size * 0.56)
    c.drawCentredString(x + size * 0.46, y + size * 0.28, (letter or "M")[:1].upper())
    c.setFillColor(MINT_BRIGHT)
    c.circle(x + size * 0.78, y + size * 0.78, size * 0.08, stroke=0, fill=1)


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
    if odd:
        _draw_mark(c, right - mark, base_y - 4, mark, labels.journal_name)
        name_x = right - mark - 8
        c.setFillColor(INK)
        size = _fit_text(c, labels.running_title, FONT_BLACK, 8.5, 300)
        c.setFont(FONT_BLACK, size)
        c.drawRightString(name_x, base_y, labels.running_title)
        c.setFillColor(MINT_TEXT)
        c.setFont(FONT_SEMIBOLD, 8)
        c.drawString(left, base_y, labels.issue_line)
    else:
        _draw_mark(c, left, base_y - 4, mark, labels.journal_name)
        c.setFillColor(INK)
        size = _fit_text(c, labels.running_title, FONT_BLACK, 8.5, 300)
        c.setFont(FONT_BLACK, size)
        c.drawString(left + mark + 8, base_y, labels.running_title)
        c.setFillColor(MINT_TEXT)
        c.setFont(FONT_SEMIBOLD, 8)
        c.drawRightString(right, base_y, labels.issue_line)

    c.setStrokeColor(MINT)
    c.setLineWidth(1)
    c.line(left, base_y - 10, right, base_y - 10)

    # page-number tab bleeding off the outer edge
    tab_w, tab_h, tab_y = 62, 22, 22
    c.setFillColor(MINT)
    if odd:
        c.roundRect(PAGE_WIDTH - tab_w, tab_y, tab_w + 12, tab_h, 11, stroke=0, fill=1)
        c.setFillColor(MINT_INK)
        c.setFont(FONT_BLACK, 10)
        c.drawCentredString(PAGE_WIDTH - tab_w / 2 + 4, tab_y + 7, str(page_number))
    else:
        c.roundRect(-12, tab_y, tab_w + 12, tab_h, 11, stroke=0, fill=1)
        c.setFillColor(MINT_INK)
        c.setFont(FONT_BLACK, 10)
        c.drawCentredString(tab_w / 2 - 4, tab_y + 7, str(page_number))

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


def _draw_dark_ground(c: canvas.Canvas) -> None:
    """Night palette background: ink, a mint glow and a faint grid."""
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
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
    c.setStrokeColor(Color(1, 1, 1, alpha=0.05))
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


def render_cover(labels: IssueLabels) -> bytes:
    """Front cover: the uploaded issue cover, or the generated brand cover."""
    register_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    if labels.cover_image:
        image = ImageReader(io.BytesIO(labels.cover_image))
        iw, ih = image.getSize()
        scale = max(PAGE_WIDTH / iw, PAGE_HEIGHT / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(image, (PAGE_WIDTH - w) / 2, (PAGE_HEIGHT - h) / 2, w, h, mask="auto")
        c.showPage()
        c.save()
        return buffer.getvalue()

    _draw_dark_ground(c)
    margin = 48

    # logo or mark
    top = PAGE_HEIGHT - margin
    if labels.logo_image:
        image = ImageReader(io.BytesIO(labels.logo_image))
        iw, ih = image.getSize()
        h = 44
        c.drawImage(image, margin, top - h, iw * h / ih, h, mask="auto")
    else:
        _draw_mark(c, margin, top - 40, 40, labels.journal_name)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(margin + 52, top - 17, labels.short_code or labels.journal_name)
        c.setFillColor(ON_DARK_MUTED)
        c.setFont(FONT, 8)
        c.drawString(margin + 52, top - 31, labels.edition_note)

    # journal name
    width = PAGE_WIDTH - 2 * margin
    size = 58
    name_lines = _wrap_lines(labels.journal_name.upper(), FONT_BLACK, size, width)
    while len(name_lines) > 2 and size > 30:
        size -= 4
        name_lines = _wrap_lines(labels.journal_name.upper(), FONT_BLACK, size, width)
    y = PAGE_HEIGHT - 190
    c.setFillColor(white)
    c.setFont(FONT_BLACK, size)
    for line in name_lines:
        c.drawString(margin, y, line)
        y -= size * 1.02
    c.setFillColor(MINT)
    c.rect(margin, y + size * 0.55, 72, 5, stroke=0, fill=1)
    y -= 6
    c.setFillColor(white)
    for line in _wrap_lines(labels.journal_subtitle, FONT_BOLD, 18, width * 0.85)[:2]:
        c.setFont(FONT_BOLD, 18)
        c.drawString(margin, y, line)
        y -= 24
    c.setFillColor(ON_DARK_MUTED)
    for line in _wrap_lines(labels.tagline, FONT, 11, width * 0.7)[:3]:
        c.setFont(FONT, 11)
        c.drawString(margin, y - 4, line)
        y -= 15

    # issue badge
    badge_w, badge_h = 250, 108
    bx, by = PAGE_WIDTH - margin - badge_w, PAGE_HEIGHT * 0.36
    c.setFillColor(MINT_BRIGHT)
    c.roundRect(bx, by, badge_w, badge_h, 18, stroke=0, fill=1)
    c.setFillColor(MINT_INK)
    c.setFont(FONT_BLACK, 50)
    c.drawCentredString(bx + badge_w / 2, by + 50, labels.year_badge)
    size = _fit_text(c, labels.issue_badge, FONT_BLACK, 16, badge_w - 24)
    c.setFont(FONT_BLACK, size)
    c.drawCentredString(bx + badge_w / 2, by + 22, labels.issue_badge)

    # identifiers at the foot
    y = 150
    c.setStrokeColor(Color(1, 1, 1, alpha=0.14))
    c.line(margin, y + 22, PAGE_WIDTH - margin, y + 22)
    c.setFont(FONT_SEMIBOLD, 10)
    c.setFillColor(white)
    for item in labels.identifiers[:4]:
        c.drawString(margin, y, item)
        y -= 16
    c.setFillColor(ON_DARK_MUTED)
    c.setFont(FONT, 8.5)
    y = 150
    for line in labels.contacts[:4]:
        c.drawRightString(PAGE_WIDTH - margin, y, line)
        y -= 14
    c.showPage()
    c.save()
    return buffer.getvalue()


def render_back_cover(labels: IssueLabels) -> bytes:
    """Back cover: contacts and licence on the night palette."""
    register_fonts()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_dark_ground(c)
    margin = 48
    _draw_mark(c, margin, PAGE_HEIGHT - margin - 40, 40, labels.journal_name)
    c.setFillColor(white)
    c.setFont(FONT_BLACK, 20)
    c.drawString(margin + 54, PAGE_HEIGHT - margin - 26, labels.journal_name.upper()[:40])

    y = 190
    c.setFillColor(MINT_BRIGHT)
    c.roundRect(margin, y - 8, PAGE_WIDTH - 2 * margin, 1.5, 0.75, stroke=0, fill=1)
    y -= 34
    c.setFont(FONT_SEMIBOLD, 10)
    c.setFillColor(white)
    for line in labels.contacts:
        c.drawString(margin, y, line)
        y -= 18
    if labels.licence_note:
        c.setFillColor(ON_DARK_MUTED)
        c.setFont(FONT, 8)
        for line in _wrap_lines(labels.licence_note, FONT, 8, PAGE_WIDTH - 2 * margin):
            c.drawString(margin, y - 6, line)
            y -= 11
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
) -> bytes:
    """Lay ``story`` out on A4; with a page number the pages get the chrome."""
    buffer = io.BytesIO()

    def on_page(c: canvas.Canvas, doc) -> None:
        if first_page_number is not None:
            draw_page_chrome(c, labels, first_page_number + doc.page - 1)

    frame = Frame(
        MARGIN_INNER,
        TEXT_BOTTOM,
        PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER,
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
    note = _style("note", fontSize=8.5, leading=11, textColor=MINT_TEXT, alignment=TA_RIGHT)
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
    return _flow_document(story, labels, first_page_number=None, top_extra=-24)


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
        "toc-heading", fontName=FONT_BLACK, fontSize=30, leading=34, textColor=INK, spaceAfter=4
    )
    rail = _style(
        "toc-rail", fontName=FONT_BOLD, fontSize=8, leading=10, textColor=MINT_TEXT, spaceAfter=14
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

    width = PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER
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
    return _flow_document(story, labels, first_page_number=first_page_number)


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

    Each source page is trimmed, scaled to the text area and centred under the
    running head; the chrome is drawn on top.
    """
    from pypdf import PageObject, PdfReader, Transformation

    reader = PdfReader(io.BytesIO(source_pdf))
    area_w = PAGE_WIDTH - MARGIN_INNER - MARGIN_OUTER
    area_h = TEXT_TOP - TEXT_BOTTOM - 6
    for index, source in enumerate(reader.pages):
        box = source.cropbox
        src_x, src_y = float(box.left) + trim, float(box.bottom) + trim
        src_w = max(float(box.width) - 2 * trim, 1.0)
        src_h = max(float(box.height) - 2 * trim, 1.0)
        rotation = (source.get("/Rotate") or 0) % 360
        if rotation:
            source.transfer_rotation_to_content()
            box = source.cropbox
            src_x, src_y = float(box.left) + trim, float(box.bottom) + trim
            src_w = max(float(box.width) - 2 * trim, 1.0)
            src_h = max(float(box.height) - 2 * trim, 1.0)
        scale = min(area_w / src_w, area_h / src_h)
        offset_x = MARGIN_INNER + (area_w - src_w * scale) / 2
        offset_y = TEXT_BOTTOM + area_h - src_h * scale
        page = PageObject.create_blank_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        transform = (
            Transformation().translate(-src_x, -src_y).scale(scale).translate(offset_x, offset_y)
        )
        page.merge_transformed_page(source, transform, over=True, expand=False)
        number = first_page_number + index
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
