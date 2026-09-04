"""Highwire Press, Dublin Core and JSON-LD metadata for article pages.

Google Scholar, Crossref and Schema.org consumers read these tags; SPEC §6.2
lists every required name.  Everything is derived from the model so the tests
can compare tag values to database values field by field.
"""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings

from apps.core.services import get_site_settings
from apps.journal.models import Article


def _date_slashes(value) -> str:
    """Format a date as ``YYYY/MM/DD`` (the Highwire convention)."""
    return value.strftime("%Y/%m/%d") if value else ""


def highwire_tags(article: Article) -> list[dict[str, str]]:
    """Return the ordered list of ``<meta>`` tags for an article page."""
    site = get_site_settings()
    tags: list[dict[str, str]] = []

    def add(name: str, content: Any) -> None:
        if content:
            tags.append({"name": name, "content": str(content)})

    add("citation_title", article.title_en or article.title)
    for author in article.author_list():
        tags.append({"name": "citation_author", "content": author.citation_name})
        if author.affiliation_display:
            tags.append(
                {"name": "citation_author_institution", "content": author.affiliation_display}
            )
        if author.orcid:
            tags.append({"name": "citation_author_orcid", "content": author.orcid_url})
        if author.is_corresponding and author.email:
            tags.append({"name": "citation_author_email", "content": author.email})

    add("citation_publication_date", _date_slashes(article.display_date))
    add("citation_online_date", _date_slashes(article.published_online_at))
    add("citation_journal_title", site.journal_name_en or site.journal_name)
    add("citation_journal_abbrev", site.short_code)
    add("citation_issn", site.eissn)
    if article.issue:
        add("citation_volume", article.issue.volume.number)
        add("citation_issue", article.issue.number)
    add("citation_firstpage", article.pages_start)
    add("citation_lastpage", article.pages_end)
    add("citation_doi", article.doi)
    add("citation_abstract_html_url", f"{settings.SITE_URL}{article.get_absolute_url()}")
    add("citation_pdf_url", article.absolute_pdf_url)
    add("citation_abstract", article.abstract_plain)
    keywords = "; ".join(k.name for k in article.keywords.all())
    add("citation_keywords", keywords)
    add("citation_language", article.language)
    add("citation_publisher", site.publisher_name)
    add("citation_fulltext_world_readable", "")

    # Dublin Core equivalents
    add("DC.title", article.title_en or article.title)
    for author in article.author_list():
        tags.append({"name": "DC.creator", "content": author.citation_name})
    add("DC.date", article.display_date.isoformat() if article.display_date else "")
    add("DC.publisher", site.publisher_name)
    add("DC.identifier", article.doi_url or article.canonical_url)
    add("DC.language", article.language)
    add("DC.type", "Text.Serial.Journal")
    add("DC.rights", article.license.url if article.license else "")
    add("DC.description", article.abstract_plain)
    for keyword in article.keywords.all():
        tags.append({"name": "DC.subject", "content": keyword.name})

    return tags


def json_ld(article: Article) -> str:
    """Build the ``ScholarlyArticle`` JSON-LD block for an article page."""
    site = get_site_settings()
    authors = []
    for author in article.author_list():
        person: dict[str, Any] = {
            "@type": "Person",
            "name": author.full_name,
            "givenName": author.given_name,
            "familyName": author.family_name,
        }
        if author.orcid:
            person["@id"] = author.orcid_url
            person["identifier"] = author.orcid_url
        if author.affiliation:
            affiliation: dict[str, Any] = {"@type": "Organization", "name": author.affiliation}
            if author.country:
                affiliation["address"] = {
                    "@type": "PostalAddress",
                    "addressLocality": author.city,
                    "addressCountry": author.country.code,
                }
            person["affiliation"] = affiliation
        authors.append(person)

    periodical: dict[str, Any] = {
        "@type": "Periodical",
        "name": site.journal_name,
        "publisher": {"@type": "Organization", "name": site.publisher_name},
    }
    if site.eissn:
        periodical["issn"] = site.eissn

    is_part_of: dict[str, Any] = periodical
    if article.issue:
        is_part_of = {
            "@type": "PublicationIssue",
            "issueNumber": article.issue.number,
            "datePublished": (
                article.issue.published_at.isoformat() if article.issue.published_at else None
            ),
            "isPartOf": {
                "@type": "PublicationVolume",
                "volumeNumber": article.issue.volume.number,
                "isPartOf": periodical,
            },
        }

    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": article.title,
        "name": article.title,
        "abstract": article.abstract_plain,
        "inLanguage": article.language,
        "author": authors,
        "datePublished": article.display_date.isoformat() if article.display_date else None,
        "isPartOf": is_part_of,
        "url": article.canonical_url,
        "isAccessibleForFree": True,
        "keywords": [k.name for k in article.keywords.all()],
        "publisher": {"@type": "Organization", "name": site.publisher_name},
    }
    if article.doi:
        data["identifier"] = [{"@type": "PropertyValue", "propertyID": "DOI", "value": article.doi}]
        data["sameAs"] = article.doi_url
    if article.license:
        data["license"] = article.license.url
    if article.pages_start:
        data["pageStart"] = article.pages_start
    if article.pages_end:
        data["pageEnd"] = article.pages_end
    galley = article.primary_galley
    if galley is not None:
        data["encoding"] = {
            "@type": "MediaObject",
            "contentUrl": article.absolute_pdf_url,
            "encodingFormat": "application/pdf",
        }
    return json.dumps(_prune(data), ensure_ascii=False, indent=2)


def periodical_json_ld() -> str:
    """JSON-LD describing the journal itself, used on the home page."""
    site = get_site_settings()
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Periodical",
        "name": site.journal_name,
        "alternateName": site.short_code,
        "description": site.journal_subtitle,
        "url": settings.SITE_URL,
        "inLanguage": ["en", "uz", "ru"],
        "publisher": {
            "@type": "Organization",
            "name": site.publisher_name,
            "address": site.publisher_address,
        },
    }
    if site.eissn:
        data["issn"] = site.eissn
    return json.dumps(_prune(data), ensure_ascii=False, indent=2)


def _prune(value: Any) -> Any:
    """Recursively drop ``None`` and empty values from a JSON-LD structure."""
    if isinstance(value, dict):
        return {k: _prune(v) for k, v in value.items() if v not in (None, "", [], {})}
    if isinstance(value, list):
        return [_prune(v) for v in value if v not in (None, "", [], {})]
    return value
