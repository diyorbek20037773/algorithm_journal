"""Stamp published PDFs with a running header, footer and metadata.

Every page of the primary galley receives the journal name and e-ISSN in the
header and the DOI, volume/issue/pages and licence in the footer.  The
unstamped file is preserved in ``Galley.original_file`` so the operation can be
repeated when pagination changes (SPEC §8).
"""

from __future__ import annotations

import io
import logging

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

HEADER_FONT_SIZE = 7.5
FOOTER_FONT_SIZE = 7.5
MARGIN = 24


def build_header_text(article) -> str:
    """The running header: journal name and e-ISSN."""
    from apps.core.services import get_site_settings

    site = get_site_settings()
    parts = [site.journal_name_en or site.journal_name]
    if site.eissn:
        parts.append(f"e-ISSN {site.eissn}")
    return "  ·  ".join(parts)


def build_footer_text(article) -> str:
    """The running footer: DOI, issue coordinates and licence."""
    parts: list[str] = []
    if article.doi:
        parts.append(f"https://doi.org/{article.doi}")
    if article.issue_id:
        label = f"Vol. {article.issue.volume.number}, No. {article.issue.number}"
        if article.pages:
            label += f", pp. {article.pages}"
        parts.append(label)
    elif article.status == article.Status.ONLINE_FIRST:
        parts.append("Online First")
    licence = article.license.code if article.license else "CC BY 4.0"
    parts.append(f"© The Author(s). {licence.replace('-', ' ')}")
    return "  ·  ".join(parts)


def _overlay_pdf(width: float, height: float, header: str, footer: str, page_number: int) -> bytes:
    """Render a single-page transparent overlay with the header and footer."""
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    pdf.setFillColor(HexColor("#4B5563"))

    pdf.setFont("Helvetica", HEADER_FONT_SIZE)
    pdf.drawString(MARGIN, height - MARGIN + 4, header[:120])

    pdf.setFont("Helvetica", FOOTER_FONT_SIZE)
    pdf.drawString(MARGIN, MARGIN - 8, footer[:140])
    pdf.drawRightString(width - MARGIN, MARGIN - 8, str(page_number))

    pdf.setStrokeColor(HexColor("#E5E7EB"))
    pdf.setLineWidth(0.4)
    pdf.line(MARGIN, height - MARGIN, width - MARGIN, height - MARGIN)
    pdf.line(MARGIN, MARGIN, width - MARGIN, MARGIN)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def stamp_galley(article, galley) -> bool:
    """Stamp ``galley`` in place, keeping the unstamped original."""
    from pypdf import PdfReader, PdfWriter

    if galley.mime != "application/pdf":
        return False

    # Preserve the pristine upload the first time we stamp.
    galley.file.open("rb")
    source_bytes = galley.file.read()
    galley.file.close()
    if not galley.original_file:
        galley.original_file.save(
            f"original-{galley.pk}.pdf", ContentFile(source_bytes), save=False
        )
    else:
        galley.original_file.open("rb")
        source_bytes = galley.original_file.read()
        galley.original_file.close()

    reader = PdfReader(io.BytesIO(source_bytes))
    writer = PdfWriter()
    header = build_header_text(article)
    footer = build_footer_text(article)

    for index, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay_reader = PdfReader(io.BytesIO(_overlay_pdf(width, height, header, footer, index)))
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    writer.add_metadata(
        {
            "/Title": (article.title_en or article.title)[:250],
            "/Author": article.authors_display(),
            "/Subject": build_header_text(article),
            "/Keywords": ", ".join(k.name for k in article.keywords.all()),
            "/Producer": "ARER production system",
            "/DOI": article.doi or "",
        }
    )

    output = io.BytesIO()
    writer.write(output)
    payload = output.getvalue()

    galley.file.save(f"arer-{article.pk}.pdf", ContentFile(payload), save=False)
    galley.size = len(payload)
    galley.save()
    logger.info("Stamped PDF for article %s (%s bytes)", article.pk, galley.size)
    return True
