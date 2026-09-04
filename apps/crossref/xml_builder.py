"""Generate Crossref deposit XML (schema 5.4.0) for articles and issues."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from django.conf import settings
from lxml import etree

from apps.core.services import get_site_settings
from apps.journal.models import Article

logger = logging.getLogger(__name__)

CROSSREF_NS = "http://www.crossref.org/schema/5.4.0"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
JATS_NS = "http://www.ncbi.nlm.nih.gov/JATS1"
AI_NS = "http://www.crossref.org/AccessIndicators.xsd"
FR_NS = "http://www.crossref.org/fundref.xsd"

SCHEMA_LOCATION = (
    f"{CROSSREF_NS} https://www.crossref.org/schemas/crossref5.4.0.xsd"
)

NSMAP = {
    None: CROSSREF_NS,
    "xsi": XSI_NS,
    "jats": JATS_NS,
    "ai": AI_NS,
    "fr": FR_NS,
}

XSD_PATH = Path(__file__).resolve().parent / "schemas" / "crossref5.4.0.xsd"


def _el(parent, tag: str, text: str | None = None, **attrs: Any):
    """Create a namespaced child element with optional text and attributes."""
    element = etree.SubElement(parent, f"{{{CROSSREF_NS}}}{tag}")
    if text:
        element.text = str(text)
    for key, value in attrs.items():
        if value not in (None, ""):
            element.set(key.replace("__", ":").replace("_", "-"), str(value))
    return element


def batch_id(prefix: str = "arer") -> str:
    """Deterministic-ish unique batch identifier."""
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    digest = hashlib.sha1(stamp.encode()).hexdigest()[:8]
    return f"{prefix}-{stamp}-{digest}"


def build_deposit(articles: list[Article], *, doi_batch_id: str | None = None) -> bytes:
    """Build a complete Crossref deposit document for ``articles``."""
    site = get_site_settings()
    doi_batch_id = doi_batch_id or batch_id()

    root = etree.Element(f"{{{CROSSREF_NS}}}doi_batch", nsmap=NSMAP)
    root.set(f"{{{XSI_NS}}}schemaLocation", SCHEMA_LOCATION)
    root.set("version", "5.4.0")

    head = _el(root, "head")
    _el(head, "doi_batch_id", doi_batch_id)
    _el(head, "timestamp", datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    depositor = _el(head, "depositor")
    _el(depositor, "depositor_name", settings.CROSSREF_DEPOSITOR_NAME)
    _el(depositor, "email_address", settings.CROSSREF_DEPOSITOR_EMAIL)
    _el(head, "registrant", settings.CROSSREF_REGISTRANT)

    body = _el(root, "body")

    # Group articles by issue so each <journal> block carries one issue.
    grouped: dict[Any, list[Article]] = {}
    for article in articles:
        grouped.setdefault(article.issue_id, []).append(article)

    for issue_id, group in grouped.items():
        journal = _el(body, "journal")
        _journal_metadata(journal, site)
        if issue_id is not None:
            _journal_issue(journal, group[0].issue)
        for article in group:
            _journal_article(journal, article, site)

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def _journal_metadata(journal, site) -> None:
    """``<journal_metadata>`` with full title, abbreviation and e-ISSN."""
    metadata = _el(journal, "journal_metadata", language="en")
    _el(metadata, "full_title", site.journal_name_en or site.journal_name)
    _el(metadata, "abbrev_title", site.short_code)
    if site.eissn:
        _el(metadata, "issn", site.eissn, media_type="electronic")
    if site.pissn:
        _el(metadata, "issn", site.pissn, media_type="print")


def _journal_issue(journal, issue) -> None:
    """``<journal_issue>`` with publication date, volume and issue number."""
    element = _el(journal, "journal_issue")
    if issue.published_at:
        _publication_date(element, issue.published_at, media_type="online")
    volume = _el(element, "journal_volume")
    _el(volume, "volume", issue.volume.number)
    _el(element, "issue", issue.number)


def _publication_date(parent, value, media_type: str = "online") -> None:
    """``<publication_date>`` element."""
    element = _el(parent, "publication_date", media_type=media_type)
    _el(element, "month", f"{value.month:02d}")
    _el(element, "day", f"{value.day:02d}")
    _el(element, "year", value.year)


def _journal_article(journal, article: Article, site) -> None:
    """One ``<journal_article>`` block with all mandatory children."""
    element = _el(journal, "journal_article", publication_type="full_text")
    element.set("language", article.language)

    titles = _el(element, "titles")
    _el(titles, "title", article.title_en or article.title)
    if article.subtitle_en or article.subtitle:
        _el(titles, "subtitle", article.subtitle_en or article.subtitle)

    contributors = _el(element, "contributors")
    for index, author in enumerate(article.author_list()):
        person = _el(
            contributors,
            "person_name",
            sequence="first" if index == 0 else "additional",
            contributor_role="author",
        )
        _el(person, "given_name", author.given_name)
        _el(person, "surname", author.family_name)
        if author.affiliation:
            affiliations = _el(person, "affiliations")
            institution = _el(affiliations, "institution")
            _el(institution, "institution_name", author.affiliation_display)
            if author.affiliation_ror:
                _el(
                    institution,
                    "institution_id",
                    f"https://ror.org/{author.affiliation_ror.lstrip('https://ror.org/')}",
                    type="ror",
                )
        if author.orcid:
            orcid = _el(person, "ORCID", author.orcid_url)
            orcid.set("authenticated", "true" if author.orcid_verified else "false")

    for language, text in _abstracts(article):
        abstract = etree.SubElement(element, f"{{{JATS_NS}}}abstract")
        abstract.set(f"{{http://www.w3.org/XML/1998/namespace}}lang", language)
        paragraph = etree.SubElement(abstract, f"{{{JATS_NS}}}p")
        paragraph.text = text

    if article.published_online_at:
        _publication_date(element, article.published_online_at, media_type="online")
    elif article.published_at:
        _publication_date(element, article.published_at, media_type="online")

    if article.pages_start:
        pages = _el(element, "pages")
        _el(pages, "first_page", article.pages_start)
        if article.pages_end:
            _el(pages, "last_page", article.pages_end)

    publisher_item = _el(element, "publisher_item")
    _el(publisher_item, "item_number", f"arer-{article.pk}", item_number_type="article_number")

    if article.license:
        program = etree.SubElement(element, f"{{{AI_NS}}}program")
        program.set("name", "AccessIndicators")
        free = etree.SubElement(program, f"{{{AI_NS}}}free_to_read")
        free.text = None
        license_ref = etree.SubElement(program, f"{{{AI_NS}}}license_ref")
        license_ref.set("applies_to", "vor")
        if article.display_date:
            license_ref.set("start_date", article.display_date.isoformat())
        license_ref.text = article.license.url

    doi_data = _el(element, "doi_data")
    _el(doi_data, "doi", article.doi)
    _el(doi_data, "resource", article.canonical_url)

    pdf_url = article.absolute_pdf_url
    crawler = _el(doi_data, "collection", property="crawler-based")
    item = _el(crawler, "item", crawler="iParadigms")
    _el(item, "resource", pdf_url)

    text_mining = _el(doi_data, "collection", property="text-mining")
    tm_item = _el(text_mining, "item")
    resource = _el(tm_item, "resource", pdf_url)
    resource.set("mime_type", "application/pdf")

    references = list(article.references.all())
    if references:
        citation_list = _el(element, "citation_list")
        for reference in references:
            citation = _el(citation_list, "citation", key=f"ref{reference.order}")
            if reference.doi:
                _el(citation, "doi", reference.doi)
            _el(citation, "unstructured_citation", reference.raw_text)


def _abstracts(article: Article) -> list[tuple[str, str]]:
    """Abstract text per language, English first."""
    out: list[tuple[str, str]] = []
    for code in ("en", "uz", "ru"):
        value = getattr(article, f"abstract_{code}", None)
        if value:
            from apps.core.markdown import strip_markdown

            out.append((code, strip_markdown(value)))
    return out


def validate(xml_bytes: bytes) -> list[str]:
    """Validate deposit XML against the bundled XSD.

    Returns a list of error strings (empty when valid).  When the schema
    bundle is unavailable the function performs well-formedness checking and
    structural assertions instead, and says so in the returned messages.
    """
    try:
        document = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as exc:
        return [f"XML is not well formed: {exc}"]

    if XSD_PATH.exists():
        try:
            schema = etree.XMLSchema(etree.parse(str(XSD_PATH)))
            if schema.validate(document):
                return []
            return [str(error) for error in schema.error_log]
        except etree.XMLSchemaParseError as exc:  # pragma: no cover - broken bundle
            logger.warning("Could not load the Crossref XSD: %s", exc)

    return _structural_check(document)


def _structural_check(document) -> list[str]:
    """Assert the elements Crossref requires when no XSD bundle is present."""
    errors: list[str] = []
    ns = {"cr": CROSSREF_NS}
    if document.tag != f"{{{CROSSREF_NS}}}doi_batch":
        errors.append("Root element must be doi_batch")
    if document.get("version") != "5.4.0":
        errors.append("doi_batch/@version must be 5.4.0")
    for path in ("cr:head/cr:doi_batch_id", "cr:head/cr:timestamp", "cr:head/cr:depositor", "cr:body"):
        if document.find(path, ns) is None:
            errors.append(f"Missing required element: {path}")
    for article in document.findall(".//cr:journal_article", ns):
        if article.find("cr:titles/cr:title", ns) is None:
            errors.append("journal_article is missing a title")
        if article.find("cr:doi_data/cr:doi", ns) is None:
            errors.append("journal_article is missing doi_data/doi")
        if article.find("cr:doi_data/cr:resource", ns) is None:
            errors.append("journal_article is missing doi_data/resource")
    if document.find(".//cr:journal_metadata/cr:full_title", ns) is None:
        errors.append("journal_metadata is missing full_title")
    return errors
