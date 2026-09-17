"""Build the monthly issue PDF and the per-article offprints.

The editorial office picks the articles of an issue in the issue builder; this
module turns them into

* one **issue PDF** — cover, imprint and editorial board, optional information
  page, contents, every article in order with continuous page numbers, back
  cover — stored in :attr:`Issue.full_issue_pdf`;
* one **offprint** per article — the same front matter and contents followed by
  the article's own pages with their issue page numbers — stored in
  :attr:`Article.offprint_pdf` and ready to be sent to the authors.

Pagination is computed here and written back to ``Article.pages_start`` /
``pages_end`` so the website, citations and Crossref agree with the PDF.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.utils.translation import pgettext

from apps.core.models import AuditLog
from apps.core.services import absolute_url, get_site_settings, log_action, send_templated_email
from apps.journal.models import Article, EditorialBoardMember, Issue
from apps.production import print_layout as layout

logger = logging.getLogger(__name__)

CONTENTS_RAIL = "MUNDARIJA • СОДЕРЖАНИЕ • CONTENTS"


class PrintBuildError(Exception):
    """A problem the editorial office can fix (missing galley, broken PDF)."""


@dataclass
class _Placed:
    article: Article
    source: bytes
    pages: int
    first_page: int = 0

    @property
    def last_page(self) -> int:
        return self.first_page + self.pages - 1


def _month_name(month: int) -> str:
    names = {
        1: pgettext("month name", "January"),
        2: pgettext("month name", "February"),
        3: pgettext("month name", "March"),
        4: pgettext("month name", "April"),
        5: pgettext("month name", "May"),
        6: pgettext("month name", "June"),
        7: pgettext("month name", "July"),
        8: pgettext("month name", "August"),
        9: pgettext("month name", "September"),
        10: pgettext("month name", "October"),
        11: pgettext("month name", "November"),
        12: pgettext("month name", "December"),
    }
    name = names[month]
    return name if translation.get_language() == "en" else name.lower()


# --------------------------------------------------------------------------
# selection and readiness
# --------------------------------------------------------------------------


def issue_articles(issue: Issue):
    """Articles of the issue in print order."""
    return (
        Article.objects.filter(issue=issue)
        .with_related()
        .order_by("section__order", "article_number", "id")
    )


def print_blockers(issue: Issue) -> dict[int, list[str]]:
    """Per-article reasons the issue PDF cannot be built yet."""
    problems: dict[int, list[str]] = {}
    for article in issue_articles(issue):
        if article.primary_galley is None:
            problems.setdefault(article.pk, []).append(_("no PDF galley"))
    return problems


def assign_articles(issue: Issue, article_ids: list[int], *, user=None, request=None) -> int:
    """Put the selected articles into ``issue`` (end of the running order)."""
    from apps.production.services import assign_to_issue

    count = 0
    candidates = Article.objects.filter(pk__in=article_ids).exclude(issue=issue)
    for article in candidates.exclude(status=Article.Status.PUBLISHED).order_by("pk"):
        assign_to_issue(article, issue, user=user)
        count += 1
    if count:
        log_action(
            AuditLog.Action.WORKFLOW,
            actor=user,
            target=f"Issue {issue.pk}",
            changes={"added_articles": count},
            request=request,
        )
    return count


def remove_articles(issue: Issue, article_ids: list[int], *, user=None, request=None) -> int:
    """Take unpublished articles back out of ``issue``."""
    queryset = Article.objects.filter(issue=issue, pk__in=article_ids).exclude(
        status=Article.Status.PUBLISHED
    )
    count = queryset.update(issue=None, article_number=None, pages_start="", pages_end="")
    if count:
        log_action(
            AuditLog.Action.WORKFLOW,
            actor=user,
            target=f"Issue {issue.pk}",
            changes={"removed_articles": count},
            request=request,
        )
    return count


# --------------------------------------------------------------------------
# labels
# --------------------------------------------------------------------------


def build_labels(issue: Issue) -> layout.IssueLabels:
    """Collect every printed string in the issue's print language."""
    site = get_site_settings()
    date = issue.published_at or timezone.localdate()
    month = _month_name(date.month)
    year = issue.volume.year or date.year
    values = {"month": month, "year": year, "number": issue.number, "volume": issue.volume.number}

    identifiers = []
    if site.pissn:
        identifiers.append(f"ISSN {site.pissn}")
    if site.eissn:
        identifiers.append(f"e-ISSN {site.eissn}")
    if issue.doi:
        identifiers.append(f"DOI {issue.doi}")
    elif site.doi_prefix:
        identifiers.append(f"DOI {site.doi_prefix}")

    imprint = []
    if site.publisher_name:
        imprint.append(_("Publisher: %(name)s") % {"name": site.publisher_name})
    if site.registration_certificate_number:
        certificate = _("Registration certificate No. %(number)s") % {
            "number": site.registration_certificate_number
        }
        if site.registration_certificate_date:
            certificate += f" ({site.registration_certificate_date:%d.%m.%Y})"
        if site.registration_authority:
            certificate += f", {site.registration_authority}"
        imprint.append(certificate)
    address = site.contact_address or site.publisher_address
    if address:
        imprint.append(_("Address: %(address)s") % {"address": " ".join(address.split())})

    website = settings.SITE_URL.replace("https://", "").replace("http://", "").rstrip("/")
    contacts: list[tuple[str, str]] = []
    if site.contact_phone:
        contacts.append((_("Phone"), site.contact_phone))
    if site.contact_email:
        contacts.append((_("E-mail"), site.contact_email))
    if website:
        contacts.append((_("Website"), website))
    telegram = (site.social_links or {}).get("telegram")
    if telegram:
        contacts.append(("Telegram", str(telegram)))

    def read(field_file) -> bytes | None:
        if not field_file:
            return None
        try:
            field_file.open("rb")
            try:
                return field_file.read()
            finally:
                field_file.close()
        except (OSError, ValueError):
            logger.warning("Could not read %s for the issue PDF", field_file.name)
            return None

    return layout.IssueLabels(
        journal_name=site.wordmark_name or site.journal_name,
        journal_subtitle=site.wordmark_descriptor,
        tagline=site.journal_subtitle,
        running_title=(site.journal_name or site.wordmark_name).upper(),
        issue_line=_("%(month)s %(year)s · No. %(number)s") % values,
        year_badge=str(year),
        issue_badge=(_("%(month)s · No. %(number)s") % values).upper(),
        edition_note=_("Electronic edition, %(month)s %(year)s.") % values,
        contents_title=_("Contents").upper(),
        contents_rail=CONTENTS_RAIL,
        identifiers=identifiers,
        imprint=imprint,
        contacts=contacts,
        licence_note=_(
            "All articles are published in open access under the Creative Commons "
            "Attribution 4.0 International licence (CC BY 4.0)."
        ),
        info_page_text=site.print_info_page,
        cover_image=read(issue.cover),
        logo_image=read(site.logo_dark),
        short_code=site.short_code,
        open_access_label=_("Open access · CC BY 4.0").upper(),
        indexed_in_label=_("Abstracting and indexing"),
        indexing=[
            (service.name, read(service.logo))
            for service in site.indexing_badges.filter(is_active=True).order_by("order", "name")
        ],
        qr_url=absolute_url(issue.get_absolute_url()),
        website=website,
        cover_background=read(site.print_cover_background),
        back_cover_background=read(site.print_back_cover_background),
        page_background=read(site.print_page_background),
        highlights_label=_("In this issue"),
    )


def board_groups() -> list[layout.BoardGroup]:
    """Active editorial board members grouped by role, in masthead order."""
    labels = {
        EditorialBoardMember.Role.EDITOR_IN_CHIEF: _("Editor-in-Chief"),
        EditorialBoardMember.Role.DEPUTY_EDITOR: _("Deputy Editor"),
        EditorialBoardMember.Role.MANAGING_EDITOR: _("Managing Editor"),
        EditorialBoardMember.Role.SECTION_EDITOR: _("Section Editors"),
        EditorialBoardMember.Role.BOARD_MEMBER: _("Editorial Board"),
        EditorialBoardMember.Role.ADVISORY: _("International Advisory Board"),
    }
    members = EditorialBoardMember.objects.filter(is_active=True).order_by("order", "full_name")
    groups = []
    for role in EditorialBoardMember.ROLE_ORDER:
        if role not in labels:
            continue
        rows = [
            (
                member.full_name,
                ", ".join(
                    part
                    for part in (member.degree, member.academic_title, member.affiliation)
                    if part
                ),
            )
            for member in members
            if member.role == role
        ]
        groups.append(layout.BoardGroup(label=labels[role], members=rows))
    return groups


def _article_title(article: Article) -> str:
    """The title in the article's own language, as printed on its first page."""
    with translation.override(article.language or translation.get_language()):
        return article.title


def _authors_line(article: Article) -> str:
    names = []
    for author in article.author_list():
        family = author.family_name_native or author.family_name
        given = author.given_name_native or author.given_name
        names.append(f"{family} {given}".strip())
    return ", ".join(names)


def _footer_note(article: Article) -> str:
    if article.doi:
        return f"https://doi.org/{article.doi}"
    return ""


def _galley_bytes(article: Article) -> bytes:
    galley = article.primary_galley
    if galley is None:
        raise PrintBuildError(_("Article #%(pk)s has no PDF galley.") % {"pk": article.pk})
    # The unstamped upload first: the public galley carries the website footer.
    for field_file in (galley.original_file, galley.file):
        if not field_file:
            continue
        try:
            field_file.open("rb")
            try:
                return field_file.read()
            finally:
                field_file.close()
        except (OSError, ValueError):
            logger.warning(
                "Galley file %s of article %s is unreadable", field_file.name, article.pk
            )
    raise PrintBuildError(
        _("The PDF galley of article #%(pk)s could not be read.") % {"pk": article.pk}
    )


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------


@dataclass
class BuildResult:
    """What a build produced."""

    issue_pdf: bytes
    offprints: dict[int, bytes]
    page_ranges: dict[int, tuple[int, int]]
    page_count: int


def render_issue(issue: Issue) -> BuildResult:
    """Render the issue PDF and every offprint in memory (no database writes)."""
    from pypdf import PdfReader, PdfWriter

    articles = list(issue_articles(issue))
    if not articles:
        raise PrintBuildError(_("The issue has no articles."))

    with translation.override(issue.print_language or "uz"):
        labels = build_labels(issue)
        labels.highlights = [(_article_title(a), _authors_line(a)) for a in articles[:5]]
        groups = board_groups()
        layout.register_fonts()

        placed: list[_Placed] = []
        for article in articles:
            source = _galley_bytes(article)
            try:
                pages = layout.page_count(source)
            except Exception as exc:
                raise PrintBuildError(
                    _("The PDF galley of article #%(pk)s is damaged.") % {"pk": article.pk}
                ) from exc
            if pages == 0:
                raise PrintBuildError(
                    _("The PDF galley of article #%(pk)s is empty.") % {"pk": article.pk}
                )
            placed.append(_Placed(article=article, source=source, pages=pages))

        cover = layout.render_cover(labels)
        board = layout.render_board(labels, groups)
        info = layout.render_info_page(labels) if labels.info_page_text.strip() else b""
        back = layout.render_back_cover(labels)
        first = issue.print_first_page or 1
        front_pages = 1 + layout.page_count(board) + (layout.page_count(info) if info else 0)
        contents_start = first + front_pages

        def contents_entries() -> list[layout.TocEntry]:
            entries: list[layout.TocEntry] = []
            current_section = None
            show_sections = len({p.article.section_id for p in placed}) > 1
            for item in placed:
                if show_sections and item.article.section_id != current_section:
                    current_section = item.article.section_id
                    entries.append(
                        layout.TocEntry(title=item.article.section.name, is_section=True)
                    )
                entries.append(
                    layout.TocEntry(
                        title=_article_title(item.article),
                        authors=_authors_line(item.article),
                        page=item.first_page or 9999,
                    )
                )
            return entries

        contents = layout.render_contents(labels, contents_entries(), contents_start)
        for _attempt in range(3):
            contents_pages = layout.page_count(contents)
            cursor = contents_start + contents_pages
            for item in placed:
                item.first_page = cursor
                cursor += item.pages
            contents = layout.render_contents(labels, contents_entries(), contents_start)
            if layout.page_count(contents) == contents_pages:
                break

        front = [PdfReader(io.BytesIO(cover)), PdfReader(io.BytesIO(board))]
        if info:
            front.append(PdfReader(io.BytesIO(info)))
        front.append(PdfReader(io.BytesIO(contents)))
        back_reader = PdfReader(io.BytesIO(back))

        issue_writer = PdfWriter()
        for reader in front:
            for page in reader.pages:
                issue_writer.add_page(page)

        offprints: dict[int, bytes] = {}
        page_ranges: dict[int, tuple[int, int]] = {}
        trim = float(getattr(settings, "PRINT_SOURCE_TRIM", 18.0))
        for item in placed:
            try:
                article_pages = list(
                    layout.place_article_pages(
                        item.source,
                        labels,
                        item.first_page,
                        trim=trim,
                        footer_note=_footer_note(item.article),
                    )
                )
            except Exception as exc:
                raise PrintBuildError(
                    _("The PDF galley of article #%(pk)s could not be placed.")
                    % {"pk": item.article.pk}
                ) from exc
            offprint = PdfWriter()
            for reader in front:
                for page in reader.pages:
                    offprint.add_page(page)
            for page in article_pages:
                issue_writer.add_page(page)
                offprint.add_page(page)
            offprint.add_page(back_reader.pages[0])
            offprint.add_metadata(_pdf_metadata(labels, _article_title(item.article), item.article))
            buffer = io.BytesIO()
            offprint.write(buffer)
            offprints[item.article.pk] = buffer.getvalue()
            page_ranges[item.article.pk] = (item.first_page, item.last_page)

        issue_writer.add_page(back_reader.pages[0])
        issue_writer.add_metadata(
            _pdf_metadata(labels, f"{labels.journal_name} — {labels.issue_line}")
        )
        buffer = io.BytesIO()
        issue_writer.write(buffer)
        issue_pdf = buffer.getvalue()

    return BuildResult(
        issue_pdf=issue_pdf,
        offprints=offprints,
        page_ranges=page_ranges,
        page_count=len(issue_writer.pages),
    )


def _pdf_metadata(labels: layout.IssueLabels, title: str, article: Article | None = None) -> dict:
    metadata = {
        "/Title": title[:250],
        "/Subject": f"{labels.running_title} · {labels.issue_line}",
        "/Producer": "MEZON production system",
    }
    if article is not None:
        metadata["/Author"] = article.authors_display()
        if article.doi:
            metadata["/DOI"] = article.doi
    return metadata


def _replace_file(field_file, name: str, payload: bytes) -> None:
    """Save ``payload`` into ``field_file`` and delete the previous file."""
    old_name = field_file.name
    field_file.save(name, ContentFile(payload), save=False)
    if old_name and old_name != field_file.name:
        try:
            field_file.storage.delete(old_name)
        except OSError:  # pragma: no cover - storage hiccup must not fail the build
            logger.warning("Could not delete the previous file %s", old_name)


def build_issue_print(issue: Issue) -> BuildResult:
    """Render and store the issue PDF, the offprints and the pagination."""
    from apps.production.services import _queue_deposit, invalidate_public_caches

    result = render_issue(issue)
    with transaction.atomic():
        _replace_file(issue.full_issue_pdf, f"issue-{issue.pk}.pdf", result.issue_pdf)
        issue.print_page_count = result.page_count
        issue.save(update_fields=["full_issue_pdf", "print_page_count", "updated_at"])
        for article in Article.objects.filter(pk__in=result.offprints):
            start, end = result.page_ranges[article.pk]
            changed = (article.pages_start, article.pages_end) != (str(start), str(end))
            article.pages_start, article.pages_end = str(start), str(end)
            _replace_file(
                article.offprint_pdf, f"offprint-{article.pk}.pdf", result.offprints[article.pk]
            )
            article.save(update_fields=["pages_start", "pages_end", "offprint_pdf", "updated_at"])
            if (
                changed
                and article.doi
                and article.status in {Article.Status.ONLINE_FIRST, Article.Status.PUBLISHED}
            ):
                transaction.on_commit(lambda a=article: _queue_deposit(a, update=True))
    if issue.is_published:
        invalidate_public_caches()
    return result


def run_build(issue_id: int) -> str:
    """Build with status bookkeeping; used by the Celery task."""
    issue = Issue.objects.select_related("volume").get(pk=issue_id)
    Issue.objects.filter(pk=issue.pk).update(
        print_status=Issue.PrintStatus.BUILDING, print_error=""
    )
    try:
        result = build_issue_print(issue)
    except PrintBuildError as exc:
        Issue.objects.filter(pk=issue.pk).update(
            print_status=Issue.PrintStatus.FAILED, print_error=str(exc)
        )
        logger.warning("Issue PDF for issue %s failed: %s", issue.pk, exc)
        return "failed"
    except Exception:
        logger.exception("Issue PDF for issue %s crashed", issue.pk)
        with translation.override(settings.LANGUAGE_CODE):
            message = _("The issue PDF could not be built. The error has been logged.")
        Issue.objects.filter(pk=issue.pk).update(
            print_status=Issue.PrintStatus.FAILED, print_error=message
        )
        return "failed"
    Issue.objects.filter(pk=issue.pk).update(
        print_status=Issue.PrintStatus.READY,
        print_error="",
        print_built_at=timezone.now(),
    )
    logger.info(
        "Issue PDF built",
        extra={"issue_id": issue.pk, "pages": result.page_count, "articles": len(result.offprints)},
    )
    return "ready"


def request_build(issue: Issue, *, user=None, request=None) -> None:
    """Validate and queue a build of the issue PDF."""
    from apps.production.tasks import build_issue_print_task

    if not Article.objects.filter(issue=issue).exists():
        raise ValidationError(_("The issue has no articles."))
    blockers = print_blockers(issue)
    if blockers:
        raise ValidationError(
            _("Upload a PDF galley for these articles first: %(items)s")
            % {"items": ", ".join(f"#{pk}" for pk in blockers)}
        )
    Issue.objects.filter(pk=issue.pk).update(print_status=Issue.PrintStatus.QUEUED, print_error="")
    log_action(
        AuditLog.Action.WORKFLOW,
        actor=user,
        target=f"Issue {issue.pk}",
        changes={"action": "build_issue_pdf", "language": issue.print_language},
        request=request,
    )

    def enqueue() -> None:
        try:
            build_issue_print_task.delay(issue.pk)
        except Exception:  # pragma: no cover - broker outage: build in-process
            logger.warning("Broker unavailable; building issue %s synchronously", issue.pk)
            run_build(issue.pk)

    transaction.on_commit(enqueue)


# --------------------------------------------------------------------------
# sending to authors
# --------------------------------------------------------------------------


def offprint_recipients(article: Article) -> list[str]:
    """Corresponding authors, else every author, else the submitting account."""
    authors = list(article.author_list())
    emails = [a.email for a in authors if a.is_corresponding and a.email]
    if not emails:
        emails = [a.email for a in authors if a.email]
    if not emails and article.submission_id and article.submission.submitter_id:
        emails = [article.submission.submitter.email]
    return list(dict.fromkeys(emails))


def send_offprint(article: Article, *, user=None, request=None) -> int:
    """E-mail the offprint to the authors (attached when small, linked otherwise)."""
    from django.urls import reverse

    if not article.offprint_pdf:
        raise ValidationError(_("Build the issue PDF first; this article has no offprint yet."))
    recipients = offprint_recipients(article)
    if not recipients:
        raise ValidationError(_("No author e-mail address is recorded for this article."))

    article.offprint_pdf.open("rb")
    try:
        payload = article.offprint_pdf.read()
    finally:
        article.offprint_pdf.close()

    limit = int(getattr(settings, "OFFPRINT_ATTACH_MAX_BYTES", 8 * 1024 * 1024))
    download = absolute_url(reverse("production:article_offprint", args=[article.pk]))
    attachments = []
    if len(payload) <= limit:
        attachments.append((f"MEZON-article-{article.pk}.pdf", payload, "application/pdf"))

    language = article.language or "en"
    with translation.override(language):
        title = article.title
        subject = _("Your article in the journal layout: %(title)s") % {"title": title[:120]}
        body = _(
            "Dear author,\n\n"
            "Your article **%(title)s** has been typeset in the journal layout "
            "(%(issue)s, pp. %(start)s–%(end)s).\n\n"
            "The PDF is attached. You can also download it from your dashboard: %(url)s\n\n"
            "With best regards,\nthe editorial office"
        ) % {
            "title": title,
            "issue": article.issue.label if article.issue_id else "",
            "start": article.pages_start,
            "end": article.pages_end,
            "url": download,
        }
    sent = send_templated_email(
        "offprint_ready",
        to=recipients,
        context={"article": article, "download_url": download},
        language=language,
        fallback_subject=subject,
        fallback_body=body,
        attachments=attachments,
    )
    Article.objects.filter(pk=article.pk).update(offprint_sent_at=timezone.now())
    log_action(
        AuditLog.Action.WORKFLOW,
        actor=user,
        target=f"Article {article.pk}",
        changes={"action": "send_offprint", "recipients": len(recipients)},
        request=request,
    )
    return sent
