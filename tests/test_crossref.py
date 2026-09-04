"""Crossref deposit XML generation and validation (SPEC §15.6)."""

from __future__ import annotations

import pytest
from lxml import etree

from apps.crossref import xml_builder
from apps.crossref.models import DepositBatch
from apps.crossref.services import build_batch

pytestmark = pytest.mark.django_db

NS = {
    "cr": xml_builder.CROSSREF_NS,
    "jats": xml_builder.JATS_NS,
    "ai": xml_builder.AI_NS,
}


def _document(article) -> etree._Element:
    """Build and parse the deposit document for one article."""
    return etree.fromstring(xml_builder.build_deposit([article]))


def test_deposit_validates_against_the_schema(article, site_settings) -> None:
    """The generated XML validates (XSD when bundled, structural otherwise)."""
    errors = xml_builder.validate(xml_builder.build_deposit([article]))
    assert errors == [], errors


def test_head_carries_depositor_and_batch_id(article, site_settings) -> None:
    """The head block identifies the depositor and the batch."""
    document = _document(article)
    assert document.get("version") == "5.4.0"
    assert document.findtext("cr:head/cr:doi_batch_id", namespaces=NS)
    assert document.findtext("cr:head/cr:depositor/cr:depositor_name", namespaces=NS)
    assert document.findtext("cr:head/cr:registrant", namespaces=NS)


def test_journal_metadata(article, site_settings) -> None:
    """Full title, abbreviation and the electronic ISSN are present."""
    document = _document(article)
    assert document.findtext(".//cr:journal_metadata/cr:full_title", namespaces=NS) == (
        site_settings.journal_name_en
    )
    assert document.findtext(".//cr:journal_metadata/cr:abbrev_title", namespaces=NS) == "ARER"
    issn = document.find(".//cr:journal_metadata/cr:issn", namespaces=NS)
    assert issn.get("media_type") == "electronic"
    assert issn.text == site_settings.eissn


def test_journal_issue_has_volume_and_issue(article, site_settings) -> None:
    """The issue block carries the volume and issue numbers."""
    document = _document(article)
    assert document.findtext(".//cr:journal_volume/cr:volume", namespaces=NS) == "1"
    assert document.findtext(".//cr:journal_issue/cr:issue", namespaces=NS) == "1"


def test_contributors_include_orcid_and_affiliation(article, site_settings) -> None:
    """Every author is deposited with ORCID and affiliation."""
    document = _document(article)
    people = document.findall(".//cr:contributors/cr:person_name", namespaces=NS)
    assert len(people) == 2
    assert people[0].get("sequence") == "first"
    assert people[1].get("sequence") == "additional"
    assert people[0].get("contributor_role") == "author"
    orcid = people[0].find("cr:ORCID", namespaces=NS)
    assert orcid.text.endswith("0000-0002-1000-0031")
    assert orcid.get("authenticated") == "true"
    institution = people[0].find(".//cr:institution/cr:institution_name", namespaces=NS)
    assert "Banking and Finance Academy" in institution.text


def test_abstracts_are_deposited_per_language(article, site_settings) -> None:
    """JATS abstracts are deposited for each language that has text."""
    document = _document(article)
    abstracts = document.findall(".//jats:abstract", namespaces=NS)
    languages = {a.get("{http://www.w3.org/XML/1998/namespace}lang") for a in abstracts}
    assert {"en", "uz", "ru"} <= languages


def test_license_is_deposited(article, site_settings) -> None:
    """The CC BY licence is deposited as an AccessIndicators program."""
    document = _document(article)
    license_ref = document.find(".//ai:license_ref", namespaces=NS)
    assert license_ref is not None
    assert license_ref.text == article.license.url
    assert license_ref.get("applies_to") == "vor"


def test_doi_data_and_collections(article, site_settings) -> None:
    """The DOI, landing page, similarity-check and text-mining URLs are present."""
    document = _document(article)
    assert document.findtext(".//cr:doi_data/cr:doi", namespaces=NS) == article.doi
    resource = document.findtext(".//cr:doi_data/cr:resource", namespaces=NS)
    assert resource == article.canonical_url

    collections = document.findall(".//cr:doi_data/cr:collection", namespaces=NS)
    properties = {c.get("property") for c in collections}
    assert {"crawler-based", "text-mining"} <= properties
    crawler_item = document.find(
        ".//cr:collection[@property='crawler-based']/cr:item", namespaces=NS
    )
    assert crawler_item.get("crawler") == "iParadigms"


def test_citation_list_is_deposited(article, site_settings) -> None:
    """References are deposited so that Crossref can link citations."""
    document = _document(article)
    citations = document.findall(".//cr:citation_list/cr:citation", namespaces=NS)
    assert len(citations) == article.references.count()
    assert citations[0].findtext("cr:unstructured_citation", namespaces=NS)


def test_online_first_article_has_no_issue_block(online_first_article, site_settings) -> None:
    """An Online First deposit omits the journal_issue element."""
    document = _document(online_first_article)
    assert document.find(".//cr:journal_issue", namespaces=NS) is None
    assert document.findtext(".//cr:doi_data/cr:doi", namespaces=NS) == online_first_article.doi


def test_build_batch_creates_a_pending_record(article, site_settings) -> None:
    """Building a batch stores the XML and the article link."""
    batch = build_batch([article])
    assert batch.status == DepositBatch.Status.PENDING
    assert batch.articles.count() == 1
    assert batch.xml.name.endswith(".xml")
    assert batch.registrations.count() == 1


def test_deposit_without_credentials_stays_pending(article, site_settings, settings) -> None:
    """Missing credentials leave the batch pending with a clear message."""
    from apps.crossref.services import submit_batch

    settings.CROSSREF_USER = ""
    settings.CROSSREF_PASSWORD = ""
    batch = submit_batch(build_batch([article]))
    assert batch.status == DepositBatch.Status.PENDING
    assert "not attempted" in batch.response_log


def test_malformed_xml_is_reported() -> None:
    """Validation reports a well-formedness error rather than raising."""
    errors = xml_builder.validate(b"<not-closed>")
    assert errors and "well formed" in errors[0]
