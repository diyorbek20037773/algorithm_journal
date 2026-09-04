"""A spec-exact OAI-PMH 2.0 endpoint (verbs, formats, sets, resumption)."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone as dt_timezone
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from lxml import etree

from apps.core.services import get_site_settings
from apps.journal.models import Article, Issue, Section

OAI_NS = "http://www.openarchives.org/OAI/2.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DC_NS = "http://purl.org/dc/elements/1.1/"
OAI_DC_NS = "http://www.openarchives.org/OAI/2.0/oai_dc/"
JATS_NS = "http://www.ncbi.nlm.nih.gov/JATS1"

PAGE_SIZE = 100

VERBS = {
    "Identify",
    "ListMetadataFormats",
    "ListSets",
    "ListIdentifiers",
    "ListRecords",
    "GetRecord",
}

METADATA_FORMATS = {
    "oai_dc": {
        "schema": "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
        "namespace": OAI_DC_NS,
    },
    "jats": {
        "schema": "https://jats.nlm.nih.gov/publishing/1.3/xsd/JATS-journalpublishing1-3.xsd",
        "namespace": JATS_NS,
    },
}

#: Arguments each verb accepts, beyond ``verb`` itself.
ALLOWED_ARGS: dict[str, set[str]] = {
    "Identify": set(),
    "ListMetadataFormats": {"identifier"},
    "ListSets": {"resumptionToken"},
    "ListIdentifiers": {"from", "until", "metadataPrefix", "set", "resumptionToken"},
    "ListRecords": {"from", "until", "metadataPrefix", "set", "resumptionToken"},
    "GetRecord": {"identifier", "metadataPrefix"},
}


def _now() -> str:
    """Current UTC timestamp in OAI-PMH format."""
    return timezone.now().astimezone(dt_timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _identifier(article: Article) -> str:
    """OAI identifier of an article."""
    domain = settings.SITE_DOMAIN.split(":")[0]
    return f"oai:{domain}:article/{article.pk}"


def _parse_identifier(value: str) -> int | None:
    """Extract the article primary key from an OAI identifier."""
    if not value or "article/" not in value:
        return None
    try:
        return int(value.rsplit("article/", 1)[1])
    except (ValueError, IndexError):
        return None


def _parse_date(value: str | None) -> datetime | None:
    """Parse an OAI ``from``/``until`` argument."""
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=dt_timezone.utc)
        except ValueError:
            continue
    raise ValueError(value)


def _root(request: HttpRequest, verb: str | None, params: dict[str, str]):
    """Build the shared OAI-PMH envelope."""
    root = etree.Element(
        f"{{{OAI_NS}}}OAI-PMH", nsmap={None: OAI_NS, "xsi": XSI_NS}
    )
    root.set(
        f"{{{XSI_NS}}}schemaLocation",
        f"{OAI_NS} http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
    )
    response_date = etree.SubElement(root, f"{{{OAI_NS}}}responseDate")
    response_date.text = _now()
    request_el = etree.SubElement(root, f"{{{OAI_NS}}}request")
    request_el.text = f"{settings.SITE_URL}/oai/"
    if verb:
        request_el.set("verb", verb)
    for key, value in params.items():
        if value and key != "verb":
            request_el.set(key, value)
    return root


def _error(root, code: str, message: str) -> HttpResponse:
    """Attach an ``<error>`` element and serialise the document."""
    error = etree.SubElement(root, f"{{{OAI_NS}}}error")
    error.set("code", code)
    error.text = message
    return _respond(root)


def _respond(root) -> HttpResponse:
    """Serialise the OAI document as an XML HTTP response."""
    xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return HttpResponse(xml, content_type="text/xml; charset=utf-8")


def _encode_token(state: dict[str, Any]) -> str:
    """Encode resumption state into an opaque token."""
    return base64.urlsafe_b64encode(json.dumps(state).encode()).decode()


def _decode_token(token: str) -> dict[str, Any]:
    """Decode a resumption token, raising ``ValueError`` when malformed."""
    try:
        return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception as exc:  # noqa: BLE001 - any failure is a bad token
        raise ValueError("badResumptionToken") from exc


@require_GET
def endpoint(request: HttpRequest) -> HttpResponse:
    """Single OAI-PMH entry point implementing all six verbs."""
    params = {k: v for k, v in request.GET.items()}
    verb = params.get("verb")
    root = _root(request, verb, params)

    if verb is None:
        return _error(root, "badVerb", "The verb argument is missing.")
    if verb not in VERBS:
        return _error(root, "badVerb", f"Unsupported verb: {verb}")

    extra = set(params) - {"verb"} - ALLOWED_ARGS[verb]
    if extra:
        return _error(root, "badArgument", f"Unsupported arguments: {', '.join(sorted(extra))}")
    if "resumptionToken" in params and set(params) - {"verb", "resumptionToken"}:
        return _error(
            root, "badArgument", "resumptionToken cannot be combined with other arguments."
        )

    handler = {
        "Identify": _identify,
        "ListMetadataFormats": _list_metadata_formats,
        "ListSets": _list_sets,
        "ListIdentifiers": _list_records,
        "ListRecords": _list_records,
        "GetRecord": _get_record,
    }[verb]
    return handler(root, params, verb)


def _identify(root, params: dict[str, str], verb: str) -> HttpResponse:
    """``Identify`` — repository description."""
    site = get_site_settings()
    identify = etree.SubElement(root, f"{{{OAI_NS}}}Identify")
    earliest = (
        Article.objects.public().order_by("published_at").values_list("published_at", flat=True).first()
    )

    def add(tag: str, text: str) -> None:
        element = etree.SubElement(identify, f"{{{OAI_NS}}}{tag}")
        element.text = text

    add("repositoryName", site.journal_name_en or site.journal_name)
    add("baseURL", f"{settings.SITE_URL}/oai/")
    add("protocolVersion", "2.0")
    add("adminEmail", site.contact_email)
    add(
        "earliestDatestamp",
        f"{earliest.isoformat()}T00:00:00Z" if earliest else "2026-01-01T00:00:00Z",
    )
    add("deletedRecord", "persistent")
    add("granularity", "YYYY-MM-DDThh:mm:ssZ")
    return _respond(root)


def _list_metadata_formats(root, params: dict[str, str], verb: str) -> HttpResponse:
    """``ListMetadataFormats`` — the two supported prefixes."""
    identifier = params.get("identifier")
    if identifier:
        pk = _parse_identifier(identifier)
        if pk is None or not Article.objects.public().filter(pk=pk).exists():
            return _error(root, "idDoesNotExist", "Unknown identifier.")
    container = etree.SubElement(root, f"{{{OAI_NS}}}ListMetadataFormats")
    for prefix, spec in METADATA_FORMATS.items():
        element = etree.SubElement(container, f"{{{OAI_NS}}}metadataFormat")
        etree.SubElement(element, f"{{{OAI_NS}}}metadataPrefix").text = prefix
        etree.SubElement(element, f"{{{OAI_NS}}}schema").text = spec["schema"]
        etree.SubElement(element, f"{{{OAI_NS}}}metadataNamespace").text = spec["namespace"]
    return _respond(root)


def _list_sets(root, params: dict[str, str], verb: str) -> HttpResponse:
    """``ListSets`` — sections and volumes are exposed as sets."""
    container = etree.SubElement(root, f"{{{OAI_NS}}}ListSets")
    for section in Section.objects.filter(is_active=True):
        element = etree.SubElement(container, f"{{{OAI_NS}}}set")
        etree.SubElement(element, f"{{{OAI_NS}}}setSpec").text = f"section:{section.slug}"
        etree.SubElement(element, f"{{{OAI_NS}}}setName").text = section.name_en or section.name
    volumes = (
        Issue.objects.published()
        .select_related("volume")
        .values_list("volume__number", "volume__year")
        .distinct()
        .order_by("volume__number")
    )
    for number, year in volumes:
        element = etree.SubElement(container, f"{{{OAI_NS}}}set")
        etree.SubElement(element, f"{{{OAI_NS}}}setSpec").text = f"volume:{number}"
        etree.SubElement(element, f"{{{OAI_NS}}}setName").text = f"Volume {number} ({year})"
    return _respond(root)


def _queryset_for(params: dict[str, str]):
    """Build the article queryset matching the ``from``/``until``/``set`` filters."""
    queryset = (
        Article.objects.filter(
            status__in=[
                Article.Status.PUBLISHED,
                Article.Status.ONLINE_FIRST,
                Article.Status.RETRACTED,
            ]
        )
        .with_related()
        .order_by("pk")
    )
    since = _parse_date(params.get("from"))
    until = _parse_date(params.get("until"))
    if since:
        queryset = queryset.filter(updated_at__gte=since)
    if until:
        queryset = queryset.filter(updated_at__lte=until)
    set_spec = params.get("set")
    if set_spec:
        if set_spec.startswith("section:"):
            queryset = queryset.filter(section__slug=set_spec.split(":", 1)[1])
        elif set_spec.startswith("volume:"):
            value = set_spec.split(":", 1)[1]
            if value.isdigit():
                queryset = queryset.filter(issue__volume__number=int(value))
            else:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
    return queryset


def _list_records(root, params: dict[str, str], verb: str) -> HttpResponse:
    """``ListRecords`` and ``ListIdentifiers`` with resumption tokens."""
    token = params.get("resumptionToken")
    if token:
        try:
            state = _decode_token(token)
        except ValueError:
            return _error(root, "badResumptionToken", "The resumption token is not valid.")
        params = {**state.get("params", {}), "verb": verb}
        offset = int(state.get("offset", 0))
    else:
        offset = 0

    prefix = params.get("metadataPrefix", "oai_dc")
    if prefix not in METADATA_FORMATS:
        return _error(root, "cannotDisseminateFormat", f"Unknown metadataPrefix: {prefix}")

    try:
        queryset = _queryset_for(params)
    except ValueError:
        return _error(root, "badArgument", "The from/until date could not be parsed.")

    total = queryset.count()
    if total == 0:
        return _error(root, "noRecordsMatch", "No records match the request.")

    page = list(queryset[offset : offset + PAGE_SIZE])
    container = etree.SubElement(root, f"{{{OAI_NS}}}{verb}")

    for article in page:
        if verb == "ListIdentifiers":
            _header(container, article)
        else:
            record = etree.SubElement(container, f"{{{OAI_NS}}}record")
            _header(record, article)
            if article.status != Article.Status.RETRACTED:
                metadata = etree.SubElement(record, f"{{{OAI_NS}}}metadata")
                _metadata(metadata, article, prefix)

    next_offset = offset + PAGE_SIZE
    resumption = etree.SubElement(container, f"{{{OAI_NS}}}resumptionToken")
    resumption.set("completeListSize", str(total))
    resumption.set("cursor", str(offset))
    if next_offset < total:
        clean = {k: v for k, v in params.items() if k not in {"verb", "resumptionToken"}}
        resumption.text = _encode_token({"offset": next_offset, "params": clean})
    return _respond(root)


def _get_record(root, params: dict[str, str], verb: str) -> HttpResponse:
    """``GetRecord`` — one article by OAI identifier."""
    prefix = params.get("metadataPrefix")
    if prefix is None:
        return _error(root, "badArgument", "metadataPrefix is required.")
    if prefix not in METADATA_FORMATS:
        return _error(root, "cannotDisseminateFormat", f"Unknown metadataPrefix: {prefix}")
    identifier = params.get("identifier")
    pk = _parse_identifier(identifier or "")
    article = (
        Article.objects.filter(
            pk=pk,
            status__in=[
                Article.Status.PUBLISHED,
                Article.Status.ONLINE_FIRST,
                Article.Status.RETRACTED,
            ],
        )
        .with_related()
        .first()
        if pk
        else None
    )
    if article is None:
        return _error(root, "idDoesNotExist", "Unknown identifier.")

    container = etree.SubElement(root, f"{{{OAI_NS}}}GetRecord")
    record = etree.SubElement(container, f"{{{OAI_NS}}}record")
    _header(record, article)
    if article.status != Article.Status.RETRACTED:
        metadata = etree.SubElement(record, f"{{{OAI_NS}}}metadata")
        _metadata(metadata, article, prefix)
    return _respond(root)


def _header(parent, article: Article) -> None:
    """``<header>`` element with identifier, datestamp and sets."""
    header = etree.SubElement(parent, f"{{{OAI_NS}}}header")
    if article.status == Article.Status.RETRACTED:
        header.set("status", "deleted")
    etree.SubElement(header, f"{{{OAI_NS}}}identifier").text = _identifier(article)
    etree.SubElement(header, f"{{{OAI_NS}}}datestamp").text = article.updated_at.astimezone(
        dt_timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    etree.SubElement(header, f"{{{OAI_NS}}}setSpec").text = f"section:{article.section.slug}"
    if article.issue_id:
        etree.SubElement(header, f"{{{OAI_NS}}}setSpec").text = (
            f"volume:{article.issue.volume.number}"
        )


def _metadata(parent, article: Article, prefix: str) -> None:
    """Dispatch to the requested metadata serialiser."""
    if prefix == "oai_dc":
        _oai_dc(parent, article)
    else:
        _jats(parent, article)


def _oai_dc(parent, article: Article) -> None:
    """Dublin Core representation of an article."""
    site = get_site_settings()
    dc_root = etree.SubElement(
        parent, f"{{{OAI_DC_NS}}}dc", nsmap={"oai_dc": OAI_DC_NS, "dc": DC_NS, "xsi": XSI_NS}
    )
    dc_root.set(
        f"{{{XSI_NS}}}schemaLocation",
        f"{OAI_DC_NS} http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
    )

    def add(tag: str, text: str | None) -> None:
        if text:
            etree.SubElement(dc_root, f"{{{DC_NS}}}{tag}").text = str(text)

    add("title", article.title_en or article.title)
    for author in article.author_list():
        add("creator", author.citation_name)
    for keyword in article.keywords.all():
        add("subject", keyword.name)
    for jel in article.jel_codes.all():
        add("subject", f"JEL {jel.code}")
    add("description", article.abstract_plain)
    add("publisher", site.publisher_name)
    add("date", article.display_date.isoformat() if article.display_date else "")
    add("type", "info:eu-repo/semantics/article")
    add("type", "info:eu-repo/semantics/publishedVersion")
    add("format", "application/pdf")
    add("identifier", article.doi_url or article.canonical_url)
    add("identifier", article.canonical_url)
    add("source", f"{site.journal_name}; {article.issue.label if article.issue else 'Online First'}")
    add("language", article.language)
    if article.license:
        add("rights", article.license.url)
    add("rights", "info:eu-repo/semantics/openAccess")


def _jats(parent, article: Article) -> None:
    """Minimal JATS front matter for an article."""
    site = get_site_settings()
    root = etree.SubElement(parent, f"{{{JATS_NS}}}article", nsmap={"jats": JATS_NS})
    root.set("article-type", "research-article")
    front = etree.SubElement(root, f"{{{JATS_NS}}}front")

    journal_meta = etree.SubElement(front, f"{{{JATS_NS}}}journal-meta")
    etree.SubElement(journal_meta, f"{{{JATS_NS}}}journal-id").text = site.short_code
    title_group = etree.SubElement(journal_meta, f"{{{JATS_NS}}}journal-title-group")
    etree.SubElement(title_group, f"{{{JATS_NS}}}journal-title").text = (
        site.journal_name_en or site.journal_name
    )
    if site.eissn:
        issn = etree.SubElement(journal_meta, f"{{{JATS_NS}}}issn")
        issn.set("pub-type", "epub")
        issn.text = site.eissn
    publisher = etree.SubElement(journal_meta, f"{{{JATS_NS}}}publisher")
    etree.SubElement(publisher, f"{{{JATS_NS}}}publisher-name").text = site.publisher_name

    article_meta = etree.SubElement(front, f"{{{JATS_NS}}}article-meta")
    if article.doi:
        doi = etree.SubElement(article_meta, f"{{{JATS_NS}}}article-id")
        doi.set("pub-id-type", "doi")
        doi.text = article.doi
    group = etree.SubElement(article_meta, f"{{{JATS_NS}}}title-group")
    etree.SubElement(group, f"{{{JATS_NS}}}article-title").text = article.title_en or article.title

    contrib_group = etree.SubElement(article_meta, f"{{{JATS_NS}}}contrib-group")
    for author in article.author_list():
        contrib = etree.SubElement(contrib_group, f"{{{JATS_NS}}}contrib")
        contrib.set("contrib-type", "author")
        if author.orcid:
            orcid = etree.SubElement(contrib, f"{{{JATS_NS}}}contrib-id")
            orcid.set("contrib-id-type", "orcid")
            orcid.text = author.orcid_url
        name = etree.SubElement(contrib, f"{{{JATS_NS}}}name")
        etree.SubElement(name, f"{{{JATS_NS}}}surname").text = author.family_name
        etree.SubElement(name, f"{{{JATS_NS}}}given-names").text = author.given_name
        if author.affiliation_display:
            etree.SubElement(contrib, f"{{{JATS_NS}}}aff").text = author.affiliation_display

    if article.display_date:
        pub_date = etree.SubElement(article_meta, f"{{{JATS_NS}}}pub-date")
        pub_date.set("pub-type", "epub")
        etree.SubElement(pub_date, f"{{{JATS_NS}}}day").text = str(article.display_date.day)
        etree.SubElement(pub_date, f"{{{JATS_NS}}}month").text = str(article.display_date.month)
        etree.SubElement(pub_date, f"{{{JATS_NS}}}year").text = str(article.display_date.year)

    if article.issue_id:
        etree.SubElement(article_meta, f"{{{JATS_NS}}}volume").text = str(
            article.issue.volume.number
        )
        etree.SubElement(article_meta, f"{{{JATS_NS}}}issue").text = str(article.issue.number)
    if article.pages_start:
        etree.SubElement(article_meta, f"{{{JATS_NS}}}fpage").text = article.pages_start
    if article.pages_end:
        etree.SubElement(article_meta, f"{{{JATS_NS}}}lpage").text = article.pages_end

    if article.abstract_plain:
        abstract = etree.SubElement(article_meta, f"{{{JATS_NS}}}abstract")
        etree.SubElement(abstract, f"{{{JATS_NS}}}p").text = article.abstract_plain

    keywords = list(article.keywords.all())
    if keywords:
        kwd_group = etree.SubElement(article_meta, f"{{{JATS_NS}}}kwd-group")
        for keyword in keywords:
            etree.SubElement(kwd_group, f"{{{JATS_NS}}}kwd").text = keyword.name
