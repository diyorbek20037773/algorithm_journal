"""OAI-PMH 2.0 conformance tests (SPEC §15.8)."""

from __future__ import annotations

import pytest
from lxml import etree

pytestmark = pytest.mark.django_db

OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/"}


def _xml(client, query: str) -> etree._Element:
    """Fetch and parse an OAI-PMH response."""
    response = client.get(f"/oai/?{query}")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/xml")
    return etree.fromstring(response.content)


def test_identify(client_anon, article, site_settings) -> None:
    """Identify returns every mandatory element."""
    root = _xml(client_anon, "verb=Identify")
    identify = root.find("oai:Identify", OAI_NS)
    for tag in (
        "repositoryName",
        "baseURL",
        "protocolVersion",
        "adminEmail",
        "earliestDatestamp",
        "deletedRecord",
        "granularity",
    ):
        assert identify.findtext(f"oai:{tag}", namespaces=OAI_NS), tag
    assert identify.findtext("oai:protocolVersion", namespaces=OAI_NS) == "2.0"


def test_list_metadata_formats(client_anon, article, site_settings) -> None:
    """Both oai_dc and jats are advertised."""
    root = _xml(client_anon, "verb=ListMetadataFormats")
    prefixes = {e.text for e in root.findall(".//oai:metadataPrefix", OAI_NS)}
    assert prefixes == {"oai_dc", "jats"}


def test_list_sets_contains_sections_and_volumes(client_anon, article, site_settings) -> None:
    """Sets are exposed for sections and volumes."""
    root = _xml(client_anon, "verb=ListSets")
    specs = {e.text for e in root.findall(".//oai:setSpec", OAI_NS)}
    assert f"section:{article.section.slug}" in specs
    assert f"volume:{article.issue.volume.number}" in specs


def test_list_identifiers(client_anon, article, site_settings) -> None:
    """ListIdentifiers returns headers with identifiers and datestamps."""
    root = _xml(client_anon, "verb=ListIdentifiers&metadataPrefix=oai_dc")
    identifiers = [e.text for e in root.findall(".//oai:header/oai:identifier", OAI_NS)]
    assert any(f"article/{article.pk}" in i for i in identifiers)
    assert root.findall(".//oai:header/oai:datestamp", OAI_NS)


def test_list_records_oai_dc(client_anon, article, site_settings) -> None:
    """ListRecords in Dublin Core carries the article metadata."""
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=oai_dc")
    titles = [e.text for e in root.findall(".//dc:title", OAI_NS)]
    assert article.title_en in titles
    creators = [e.text for e in root.findall(".//dc:creator", OAI_NS)]
    assert "Karimov, Aziz" in creators
    identifiers = [e.text for e in root.findall(".//dc:identifier", OAI_NS)]
    assert article.doi_url in identifiers
    rights = [e.text for e in root.findall(".//dc:rights", OAI_NS)]
    assert "info:eu-repo/semantics/openAccess" in rights


def test_list_records_jats(client_anon, article, site_settings) -> None:
    """The JATS format returns article front matter."""
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=jats")
    jats = {"j": "http://www.ncbi.nlm.nih.gov/JATS1"}
    titles = [e.text for e in root.findall(".//j:article-title", jats)]
    assert article.title_en in titles
    assert root.findall(".//j:contrib", jats)


def test_get_record(client_anon, article, site_settings) -> None:
    """GetRecord returns exactly one record for a valid identifier."""
    from django.conf import settings as django_settings

    domain = django_settings.SITE_DOMAIN.split(":")[0]
    identifier = f"oai:{domain}:article/{article.pk}"
    root = _xml(client_anon, f"verb=GetRecord&metadataPrefix=oai_dc&identifier={identifier}")
    records = root.findall(".//oai:record", OAI_NS)
    assert len(records) == 1


def test_get_record_unknown_identifier(client_anon, article, site_settings) -> None:
    """An unknown identifier raises idDoesNotExist."""
    root = _xml(client_anon, "verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:x:article/99999")
    assert root.find("oai:error", OAI_NS).get("code") == "idDoesNotExist"


def test_bad_verb(client_anon, article, site_settings) -> None:
    """An unknown verb raises badVerb."""
    root = _xml(client_anon, "verb=Nonsense")
    assert root.find("oai:error", OAI_NS).get("code") == "badVerb"


def test_missing_verb(client_anon, article, site_settings) -> None:
    """A request without a verb raises badVerb."""
    root = _xml(client_anon, "metadataPrefix=oai_dc")
    assert root.find("oai:error", OAI_NS).get("code") == "badVerb"


def test_bad_metadata_prefix(client_anon, article, site_settings) -> None:
    """An unsupported prefix raises cannotDisseminateFormat."""
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=marcxml")
    assert root.find("oai:error", OAI_NS).get("code") == "cannotDisseminateFormat"


def test_bad_argument(client_anon, article, site_settings) -> None:
    """An unsupported argument raises badArgument."""
    root = _xml(client_anon, "verb=Identify&set=section:x")
    assert root.find("oai:error", OAI_NS).get("code") == "badArgument"


def test_no_records_match(client_anon, article, site_settings) -> None:
    """A set that matches nothing raises noRecordsMatch."""
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=oai_dc&set=section:nothing")
    assert root.find("oai:error", OAI_NS).get("code") == "noRecordsMatch"


def test_resumption_token_round_trip(client_anon, section, license_cc_by, site_settings) -> None:
    """More than one page of records produces a working resumption token."""
    import datetime as dt

    from apps.journal.models import Article

    for index in range(120):
        Article.objects.create(
            section=section,
            license=license_cc_by,
            status=Article.Status.ONLINE_FIRST,
            published_online_at=dt.date(2026, 1, 1),
            title=f"Bulk article {index}",
            title_en=f"Bulk article {index}",
        )

    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=oai_dc")
    token = root.find(".//oai:resumptionToken", OAI_NS)
    assert token is not None
    assert int(token.get("completeListSize")) >= 120
    assert token.text

    second = _xml(client_anon, f"verb=ListRecords&resumptionToken={token.text}")
    assert second.findall(".//oai:record", OAI_NS)


def test_resumption_token_cannot_be_combined(client_anon, article, site_settings) -> None:
    """Combining a resumption token with other arguments is a badArgument."""
    root = _xml(client_anon, "verb=ListRecords&resumptionToken=abc&metadataPrefix=oai_dc")
    assert root.find("oai:error", OAI_NS).get("code") == "badArgument"


def test_retracted_records_are_marked_deleted(client_anon, article, site_settings) -> None:
    """A retracted article is exposed as a deleted record."""
    from apps.journal.models import Article

    article.status = Article.Status.RETRACTED
    article.save()
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=oai_dc")
    headers = root.findall(".//oai:header", OAI_NS)
    assert any(h.get("status") == "deleted" for h in headers)


def test_from_until_filter(client_anon, article, site_settings) -> None:
    """A from date in the future matches nothing."""
    root = _xml(client_anon, "verb=ListRecords&metadataPrefix=oai_dc&from=2099-01-01")
    assert root.find("oai:error", OAI_NS).get("code") == "noRecordsMatch"
