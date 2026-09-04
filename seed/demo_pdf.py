"""Generate real, text-based PDF galleys for the demonstration articles.

The PDFs carry the same running header and footer that the production PDF
stamper applies, so downloads, page counts and text extraction behave exactly
as they will for genuine articles.
"""

from __future__ import annotations

import io
import textwrap
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 22 * mm
LINE_HEIGHT = 12
BODY_WIDTH_CHARS = 96

INK = HexColor("#111827")
INK_2 = HexColor("#4B5563")
LINE = HexColor("#E5E7EB")
ACCENT = HexColor("#0F4C81")

BODY_SECTIONS: list[tuple[str, str]] = [
    (
        "1. Introduction",
        "This demonstration file reproduces the layout of a published article so that "
        "downloads, page counts, text extraction and the production stamping routine can "
        "be exercised end to end. The text below is placeholder prose describing the "
        "structure a real submission follows; it is not a research finding. The "
        "introduction states the research question, explains why it matters for policy and "
        "for the literature, summarises the contribution, and sets out how the remainder "
        "of the paper is organised.",
    ),
    (
        "2. Related literature",
        "The literature review places the question in its international context, "
        "identifies the specific gap the paper fills, and explains how the present "
        "approach differs from earlier work. Authors are expected to engage with "
        "international journals rather than regional sources alone, and to be explicit "
        "about which earlier results the paper confirms, extends or contradicts.",
    ),
    (
        "3. Data and methodology",
        "The methodology section describes the data sources, the sample construction, the "
        "variables and their measurement, the model specification and the identification "
        "strategy, in enough detail for the analysis to be reproduced. Software and "
        "package versions are reported. Where administrative micro-data are used, the "
        "access conditions are stated so that other researchers know what they can obtain.",
    ),
    (
        "4. Results",
        "Results are reported with point estimates, standard errors, sample sizes and the "
        "diagnostic tests appropriate to the specification. Tables are formatted for "
        "readability rather than for density, and every table and figure is self-contained: "
        "a reader should be able to interpret it without returning to the text. Robustness "
        "checks follow the main specification rather than replacing it.",
    ),
    (
        "5. Discussion and conclusion",
        "The discussion interprets the findings, compares them with earlier results, "
        "proposes mechanisms and states the limitations honestly. The conclusion answers "
        "the research question posed in the introduction, draws only the policy "
        "implications the evidence supports, and identifies what further work would "
        "resolve the remaining uncertainty.",
    ),
]


def _header_text(article: Any) -> str:
    """Running header: journal name and e-ISSN."""
    from apps.core.services import get_site_settings

    site = get_site_settings()
    parts = [site.journal_name_en or site.journal_name]
    if site.eissn:
        parts.append(f"e-ISSN {site.eissn}")
    return "  ·  ".join(parts)


def _footer_text(article: Any) -> str:
    """Running footer: DOI, issue coordinates and licence."""
    parts: list[str] = []
    if article.doi:
        parts.append(f"https://doi.org/{article.doi}")
    if article.issue_id:
        label = f"Vol. {article.issue.volume.number}, No. {article.issue.number}"
        if article.pages:
            label += f", pp. {article.pages}"
        parts.append(label)
    else:
        parts.append("Online First")
    parts.append("© The Author(s). CC BY 4.0")
    return "  ·  ".join(parts)


def _chrome(pdf: canvas.Canvas, article: Any, page_number: int) -> None:
    """Draw the header, footer and rules on the current page."""
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.4)
    pdf.line(MARGIN, PAGE_HEIGHT - MARGIN + 6, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN + 6)
    pdf.line(MARGIN, MARGIN - 6, PAGE_WIDTH - MARGIN, MARGIN - 6)

    pdf.setFillColor(INK_2)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(MARGIN, PAGE_HEIGHT - MARGIN + 10, _header_text(article)[:120])
    pdf.drawString(MARGIN, MARGIN - 14, _footer_text(article)[:140])
    pdf.drawRightString(PAGE_WIDTH - MARGIN, MARGIN - 14, str(page_number))


def build_article_pdf(article: Any) -> bytes:
    """Render a two-to-three page PDF for ``article`` and return the bytes."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle((article.title_en or article.title)[:200])
    pdf.setAuthor(article.authors_display())
    pdf.setSubject(_header_text(article))
    pdf.setKeywords(", ".join(k.name for k in article.keywords.all()))

    page_number = 1
    _chrome(pdf, article, page_number)
    y = PAGE_HEIGHT - MARGIN - 20

    # --- title block -------------------------------------------------------
    pdf.setFillColor(ACCENT)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(
        MARGIN, y, article.section.name_en.upper() if article.section.name_en else "ARTICLE"
    )
    y -= 18

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 15)
    for line in textwrap.wrap(article.title_en or article.title, 62):
        pdf.drawString(MARGIN, y, line)
        y -= 18
    y -= 4

    pdf.setFillColor(INK_2)
    pdf.setFont("Helvetica", 9.5)
    for line in textwrap.wrap(article.authors_display(), 100):
        pdf.drawString(MARGIN, y, line)
        y -= 12
    for author in article.author_list():
        text = f"{author.affiliation_display}" + (
            f" · ORCID {author.orcid}" if author.orcid else ""
        )
        for line in textwrap.wrap(text, 110):
            pdf.setFont("Helvetica", 7.5)
            pdf.drawString(MARGIN, y, line)
            y -= 10
    y -= 8

    # --- abstract ----------------------------------------------------------
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(MARGIN, y, "Abstract")
    y -= 13
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColor(INK_2)
    for line in textwrap.wrap(article.abstract_plain, BODY_WIDTH_CHARS):
        pdf.drawString(MARGIN, y, line)
        y -= 10.5
        if y < MARGIN + 40:
            pdf.showPage()
            page_number += 1
            _chrome(pdf, article, page_number)
            y = PAGE_HEIGHT - MARGIN - 20
            pdf.setFont("Helvetica", 8.5)
            pdf.setFillColor(INK_2)
    y -= 6

    keywords = ", ".join(k.name for k in article.keywords.all())
    jel = ", ".join(j.code for j in article.jel_codes.all())
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Oblique", 8.5)
    for label, value in (("Keywords: ", keywords), ("JEL classification: ", jel)):
        for line in textwrap.wrap(label + value, BODY_WIDTH_CHARS):
            pdf.drawString(MARGIN, y, line)
            y -= 10.5
    y -= 10

    # --- body --------------------------------------------------------------
    for heading, text in BODY_SECTIONS:
        if y < MARGIN + 70:
            pdf.showPage()
            page_number += 1
            _chrome(pdf, article, page_number)
            y = PAGE_HEIGHT - MARGIN - 20
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(MARGIN, y, heading)
        y -= 14
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(INK_2)
        for line in textwrap.wrap(text, BODY_WIDTH_CHARS):
            pdf.drawString(MARGIN, y, line)
            y -= 11
            if y < MARGIN + 30:
                pdf.showPage()
                page_number += 1
                _chrome(pdf, article, page_number)
                y = PAGE_HEIGHT - MARGIN - 20
                pdf.setFont("Helvetica", 9)
                pdf.setFillColor(INK_2)
        y -= 8

    # --- references --------------------------------------------------------
    references = list(article.references.all()[:8])
    if references:
        if y < MARGIN + 80:
            pdf.showPage()
            page_number += 1
            _chrome(pdf, article, page_number)
            y = PAGE_HEIGHT - MARGIN - 20
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(MARGIN, y, "References (extract)")
        y -= 14
        pdf.setFont("Helvetica", 7.5)
        pdf.setFillColor(INK_2)
        for reference in references:
            for line in textwrap.wrap(reference.raw_text.replace("*", ""), 118):
                pdf.drawString(MARGIN, y, line)
                y -= 9.5
                if y < MARGIN + 20:
                    pdf.showPage()
                    page_number += 1
                    _chrome(pdf, article, page_number)
                    y = PAGE_HEIGHT - MARGIN - 20
                    pdf.setFont("Helvetica", 7.5)
                    pdf.setFillColor(INK_2)
            y -= 3

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
