"""Citation rendering (CSL) and bibliographic export formats."""

from __future__ import annotations

import json
import logging
from typing import Any

from django.utils.translation import gettext_lazy as _

from apps.core.services import get_site_settings

logger = logging.getLogger(__name__)

#: Citation styles offered in the "Cite this article" modal.
STYLES: list[dict[str, str]] = [
    {"code": "apa", "label": "APA 7th", "csl": "apa"},
    {"code": "mla", "label": "MLA 9th", "csl": "modern-language-association"},
    {"code": "chicago", "label": "Chicago (author-date)", "csl": "chicago-author-date"},
    {"code": "harvard", "label": "Harvard", "csl": "harvard-cite-them-right"},
    {"code": "vancouver", "label": "Vancouver", "csl": "vancouver"},
    {"code": "gost", "label": "GOST R 7.0.5-2008", "csl": "gost-r-7-0-5-2008-numeric"},
]

EXPORT_FORMATS: tuple[str, ...] = ("bibtex", "ris", "enw", "json")


def available_styles() -> list[dict[str, str]]:
    """The citation styles the cite modal exposes."""
    return STYLES


def csl_json(article) -> dict[str, Any]:
    """Build a CSL-JSON item for an article."""
    site = get_site_settings()
    date = article.display_date
    item: dict[str, Any] = {
        "id": f"arer-{article.pk}",
        "type": "article-journal",
        "title": article.title_en or article.title,
        "container-title": site.journal_name_en or site.journal_name,
        "container-title-short": site.short_code,
        "author": [{"family": a.family_name, "given": a.given_name} for a in article.author_list()],
        "language": article.language,
        "abstract": article.abstract_plain,
        "URL": article.doi_url or article.canonical_url,
    }
    if date:
        item["issued"] = {"date-parts": [[date.year, date.month, date.day]]}
    if site.eissn:
        item["ISSN"] = site.eissn
    if article.issue:
        item["volume"] = str(article.issue.volume.number)
        item["issue"] = str(article.issue.number)
    if article.pages:
        item["page"] = article.pages.replace("–", "-")
    if article.doi:
        item["DOI"] = article.doi
    if article.license:
        item["license"] = article.license.url
    return item


def render_citation(article, style: str = "apa") -> str:
    """Render a formatted citation string for ``article`` in ``style``.

    Uses ``citeproc-py`` with the bundled CSL styles.  If a style is missing
    or citeproc raises, the hand-written fallback renderer is used so the
    modal never shows an error (recorded in ``DECISIONS.md``).
    """
    spec = next((s for s in STYLES if s["code"] == style), STYLES[0])
    try:
        return _render_with_citeproc(article, spec["csl"])
    except Exception:  # pragma: no cover - depends on optional CSL data
        logger.info("citeproc-py could not render style %s; using fallback", spec["csl"])
        return _render_fallback(article, spec["code"])


def _render_with_citeproc(article, csl_style: str) -> str:
    """Render through citeproc-py; raises when the style is unavailable."""
    from citeproc import (
        Citation,
        CitationItem,
        CitationStylesBibliography,
        CitationStylesStyle,
        formatter,
    )
    from citeproc.source.json import CiteProcJSON
    from citeproc_styles import get_style_filepath

    path = get_style_filepath(csl_style)
    source = CiteProcJSON([csl_json(article)])
    style = CitationStylesStyle(path, validate=False)
    bibliography = CitationStylesBibliography(style, source, formatter.plain)
    citation = Citation([CitationItem(f"arer-{article.pk}")])
    bibliography.register(citation)
    rendered = "".join(str(item) for item in bibliography.bibliography())
    rendered = " ".join(rendered.split())
    if not rendered:
        raise ValueError("empty citation")
    return rendered


def _render_fallback(article, style: str) -> str:
    """Hand-written renderer with the same interface as citeproc."""
    site = get_site_settings()
    authors = article.author_list()
    year = article.display_date.year if article.display_date else "n.d."
    journal = site.journal_name_en or site.journal_name
    volume = article.issue.volume.number if article.issue else ""
    number = article.issue.number if article.issue else ""
    pages = article.pages
    doi = article.doi_url

    def apa_authors() -> str:
        names = [f"{a.family_name}, {a.initials}" for a in authors]
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        return ", ".join(names[:-1]) + ", & " + names[-1]

    def plain_authors(sep: str = ", ") -> str:
        return sep.join(f"{a.family_name} {a.initials}" for a in authors)

    title = article.title_en or article.title
    if style == "apa":
        parts = [f"{apa_authors()} ({year}).", f"{title}.", f"{journal}"]
        if volume:
            parts.append(f", {volume}({number})" if number else f", {volume}")
        if pages:
            parts.append(f", {pages}")
        parts.append(".")
        if doi:
            parts.append(f" {doi}")
        return "".join(parts).replace(" .", ".")
    if style == "mla":
        base = f'{plain_authors()}. "{title}." {journal}'
        if volume:
            base += f", vol. {volume}"
        if number:
            base += f", no. {number}"
        base += f", {year}"
        if pages:
            base += f", pp. {pages}"
        base += "."
        return base + (f" {doi}" if doi else "")
    if style == "chicago":
        base = f'{plain_authors()}. {year}. "{title}." {journal} {volume}'
        if number:
            base += f" ({number})"
        if pages:
            base += f": {pages}"
        base += "."
        return base + (f" {doi}" if doi else "")
    if style == "harvard":
        base = f"{plain_authors()} ({year}) '{title}', {journal}"
        if volume:
            base += f", {volume}({number})" if number else f", {volume}"
        if pages:
            base += f", pp. {pages}"
        base += "."
        return base + (f" {doi}" if doi else "")
    if style == "vancouver":
        base = f"{plain_authors()}. {title}. {journal}. {year}"
        if volume:
            base += f";{volume}"
        if number:
            base += f"({number})"
        if pages:
            base += f":{pages}"
        base += "."
        return base + (f" {doi}" if doi else "")
    # GOST R 7.0.5-2008
    base = f"{plain_authors(' , ')} {title} // {journal}. {year}."
    if volume:
        base += f" Т. {volume}."
    if number:
        base += f" № {number}."
    if pages:
        base += f" С. {pages}."
    return base + (f" DOI: {article.doi}." if article.doi else "")


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------
def export_article(article, fmt: str) -> tuple[str, str, str]:
    """Return ``(content, mime_type, filename)`` for a bibliographic export."""
    fmt = fmt.lower()
    if fmt not in EXPORT_FORMATS:
        raise ValueError(str(_("Unsupported export format.")))
    stem = f"ARER-{article.pk}"
    if fmt == "bibtex":
        return to_bibtex(article), "application/x-bibtex; charset=utf-8", f"{stem}.bib"
    if fmt == "ris":
        return to_ris(article), "application/x-research-info-systems; charset=utf-8", f"{stem}.ris"
    if fmt == "enw":
        return to_endnote(article), "application/x-endnote-refer; charset=utf-8", f"{stem}.enw"
    return (
        json.dumps(csl_json(article), ensure_ascii=False, indent=2),
        "application/vnd.citationstyles.csl+json; charset=utf-8",
        f"{stem}.json",
    )


def _bibtex_key(article) -> str:
    """Stable BibTeX citation key."""
    authors = article.author_list()
    family = authors[0].family_name.lower().replace(" ", "") if authors else "arer"
    year = article.display_date.year if article.display_date else "nd"
    return f"{family}{year}arer{article.pk}"


def to_bibtex(article) -> str:
    """Serialise the article as a BibTeX ``@article`` entry."""
    site = get_site_settings()
    fields: list[tuple[str, str]] = [
        ("title", article.title_en or article.title),
        ("author", " and ".join(a.citation_name for a in article.author_list())),
        ("journal", site.journal_name_en or site.journal_name),
    ]
    if article.display_date:
        fields.append(("year", str(article.display_date.year)))
    if article.issue:
        fields.append(("volume", str(article.issue.volume.number)))
        fields.append(("number", str(article.issue.number)))
    if article.pages:
        fields.append(("pages", article.pages.replace("–", "--")))
    if article.doi:
        fields.append(("doi", article.doi))
    if site.eissn:
        fields.append(("issn", site.eissn))
    fields.append(("url", article.canonical_url))
    fields.append(("abstract", article.abstract_plain))
    fields.append(("language", article.language))
    body = ",\n".join(f"  {k} = {{{_escape_bibtex(v)}}}" for k, v in fields if v)
    return f"@article{{{_bibtex_key(article)},\n{body}\n}}\n"


def _escape_bibtex(value: str) -> str:
    """Escape the characters BibTeX treats specially."""
    return (
        str(value)
        .replace("\\", "\\textbackslash{}")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
    )


def to_ris(article) -> str:
    """Serialise the article in RIS format."""
    site = get_site_settings()
    lines = ["TY  - JOUR"]
    for author in article.author_list():
        lines.append(f"AU  - {author.citation_name}")
    lines.append(f"TI  - {article.title_en or article.title}")
    lines.append(f"JO  - {site.journal_name_en or site.journal_name}")
    lines.append(f"J2  - {site.short_code}")
    if article.display_date:
        lines.append(f"PY  - {article.display_date.year}")
        lines.append(f"DA  - {article.display_date:%Y/%m/%d}")
    if article.issue:
        lines.append(f"VL  - {article.issue.volume.number}")
        lines.append(f"IS  - {article.issue.number}")
    if article.pages_start:
        lines.append(f"SP  - {article.pages_start}")
    if article.pages_end:
        lines.append(f"EP  - {article.pages_end}")
    if article.doi:
        lines.append(f"DO  - {article.doi}")
    if site.eissn:
        lines.append(f"SN  - {site.eissn}")
    if article.abstract_plain:
        lines.append(f"AB  - {article.abstract_plain}")
    for keyword in article.keywords.all():
        lines.append(f"KW  - {keyword.name}")
    lines.append(f"UR  - {article.canonical_url}")
    lines.append(f"LA  - {article.language}")
    lines.append("ER  - ")
    return "\r\n".join(lines) + "\r\n"


def to_endnote(article) -> str:
    """Serialise the article in the EndNote (refer) tagged format."""
    site = get_site_settings()
    lines = ["%0 Journal Article"]
    for author in article.author_list():
        lines.append(f"%A {author.citation_name}")
    lines.append(f"%T {article.title_en or article.title}")
    lines.append(f"%J {site.journal_name_en or site.journal_name}")
    if article.display_date:
        lines.append(f"%D {article.display_date.year}")
    if article.issue:
        lines.append(f"%V {article.issue.volume.number}")
        lines.append(f"%N {article.issue.number}")
    if article.pages:
        lines.append(f"%P {article.pages}")
    if article.doi:
        lines.append(f"%R {article.doi}")
    if site.eissn:
        lines.append(f"%@ {site.eissn}")
    if article.abstract_plain:
        lines.append(f"%X {article.abstract_plain}")
    for keyword in article.keywords.all():
        lines.append(f"%K {keyword.name}")
    lines.append(f"%U {article.canonical_url}")
    return "\n".join(lines) + "\n"
