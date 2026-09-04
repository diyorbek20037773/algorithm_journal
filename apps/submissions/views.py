"""The five-step submission wizard and author-side submission actions."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django_ratelimit.decorators import ratelimit

from apps.core.translit import to_cyrillic
from apps.submissions import workflow
from apps.submissions.forms import (
    DECLARATIONS,
    AuthorFormSet,
    FileUploadForm,
    MetadataForm,
    ReviewersForm,
    RevisionUploadForm,
    WithdrawForm,
    WizardStartForm,
)
from apps.submissions.models import (
    Submission,
    SubmissionAuthor,
    SubmissionFile,
    SubmissionStatus,
)
from apps.submissions.services import count_words

WIZARD_STEPS = [
    (1, _("Start")),
    (2, _("Files")),
    (3, _("Metadata")),
    (4, _("Reviewers & cover letter")),
    (5, _("Review & submit")),
]


def _get_draft(request: HttpRequest, pk: int) -> Submission:
    """Fetch a draft the current user owns, or raise 403/404."""
    submission = get_object_or_404(Submission, pk=pk)
    if submission.submitter_id != request.user.pk:
        raise PermissionDenied
    if not submission.is_editable_by_author:
        raise PermissionDenied(_("This submission can no longer be edited."))
    return submission


def _wizard_context(submission: Submission | None, step: int, **extra: Any) -> dict[str, Any]:
    """Shared context for every wizard step."""
    return {
        "submission": submission,
        "steps": WIZARD_STEPS,
        "current_step": step,
        "declarations": DECLARATIONS,
        **extra,
    }


@login_required
def wizard_start(request: HttpRequest) -> HttpResponse:
    """List resumable drafts, or start a new submission."""
    drafts = Submission.objects.filter(
        submitter=request.user, status=SubmissionStatus.DRAFT
    ).order_by("-updated_at")
    return TemplateResponse(
        request,
        "submissions/wizard_intro.html",
        _wizard_context(None, 0, drafts=drafts),
    )


@login_required
@ratelimit(key="user", rate="10/d", method="POST", block=False)
def wizard_step1(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    """Step 1 — section, type, language and declarations."""
    submission = _get_draft(request, pk) if pk else None
    if getattr(request, "limited", False):
        messages.error(request, _("You have reached the daily submission limit."))
        return redirect("submissions:wizard_start")

    if request.method == "POST":
        form = WizardStartForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            if submission.pk is None:
                submission.submitter = request.user
                submission.title = _("Untitled manuscript")
            submission.wizard_step = max(submission.wizard_step, 2)
            submission.author_declarations = {
                key: bool(form.cleaned_data.get(f"declare_{key}")) for key, _label in DECLARATIONS
            }
            submission.anonymised_file_ok = submission.author_declarations.get("anonymised", False)
            submission.save()
            return redirect("submissions:wizard_step2", pk=submission.pk)
    else:
        form = WizardStartForm(instance=submission)

    return TemplateResponse(
        request, "submissions/wizard_step1.html", _wizard_context(submission, 1, form=form)
    )


@login_required
def wizard_step2(request: HttpRequest, pk: int) -> HttpResponse:
    """Step 2 — manuscript, title page and supporting files."""
    submission = _get_draft(request, pk)
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            for field, kind in FileUploadForm.KIND_MAP.items():
                uploaded = form.cleaned_data.get(field)
                if not uploaded:
                    continue
                version = submission.files.filter(kind=kind).count() + 1
                SubmissionFile.objects.create(
                    submission=submission,
                    kind=kind,
                    file=uploaded,
                    original_name=uploaded.name[:255],
                    uploaded_by=request.user,
                    version=version,
                    size=uploaded.size,
                    mime=getattr(uploaded, "content_type", "") or "",
                )
            words = form.word_count()
            if words:
                submission.word_count = words
            submission.wizard_step = max(submission.wizard_step, 3)
            submission.save()
            if words and words < 4000:
                messages.warning(
                    request,
                    _("The manuscript has about %(count)s words; research articles should have at least 4,000.")
                    % {"count": words},
                )
            return redirect("submissions:wizard_step3", pk=submission.pk)
    else:
        form = FileUploadForm()

    return TemplateResponse(
        request,
        "submissions/wizard_step2.html",
        _wizard_context(
            submission,
            2,
            form=form,
            files=submission.files.order_by("kind", "-version"),
            has_manuscript=submission.files.filter(
                kind=SubmissionFile.Kind.MANUSCRIPT_ANON
            ).exists(),
            has_title_page=submission.files.filter(kind=SubmissionFile.Kind.TITLE_PAGE).exists(),
        ),
    )


@login_required
def wizard_step3(request: HttpRequest, pk: int) -> HttpResponse:
    """Step 3 — multilingual metadata, JEL codes and authors."""
    submission = _get_draft(request, pk)
    metadata = submission.metadata or {}

    initial = {
        "funding_statement": submission.funding_statement,
        "conflict_of_interest_statement": submission.conflict_of_interest_statement
        or str(_("The authors declare no conflict of interest.")),
        "data_availability_statement": submission.data_availability_statement,
        "references": "\n".join(metadata.get("references", []) or []),
    }
    for code in ("en", "uz", "ru"):
        initial[f"title_{code}"] = metadata.get("title", {}).get(code, "")
        initial[f"abstract_{code}"] = metadata.get("abstract", {}).get(code, "")
        initial[f"keywords_{code}"] = ", ".join(metadata.get("keywords", {}).get(code, []) or [])
    if submission.jel_codes.exists():
        initial["jel_codes"] = list(submission.jel_codes.values_list("pk", flat=True))

    authors_queryset = SubmissionAuthor.objects.filter(submission=submission).order_by("order")

    if request.method == "POST":
        form = MetadataForm(request.POST)
        formset = AuthorFormSet(request.POST, queryset=authors_queryset, prefix="authors")
        if form.is_valid() and formset.is_valid():
            _save_metadata(submission, form)
            _save_authors(submission, formset)
            submission.wizard_step = max(submission.wizard_step, 4)
            submission.save()
            return redirect("submissions:wizard_step4", pk=submission.pk)
    else:
        form = MetadataForm(initial=initial)
        formset = AuthorFormSet(queryset=authors_queryset, prefix="authors")

    return TemplateResponse(
        request,
        "submissions/wizard_step3.html",
        _wizard_context(submission, 3, form=form, formset=formset),
    )


def _save_metadata(submission: Submission, form: MetadataForm) -> None:
    """Copy the metadata form into the submission, filling the Cyrillic variant."""
    data = form.cleaned_data
    titles = {code: data[f"title_{code}"] for code in ("en", "uz", "ru")}
    abstracts = {code: data[f"abstract_{code}"] for code in ("en", "uz", "ru")}
    keywords = {
        code: [k.strip() for k in data[f"keywords_{code}"].split(",") if k.strip()]
        for code in ("en", "uz", "ru")
    }
    titles["uz-cyrl"] = to_cyrillic(titles["uz"])
    abstracts["uz-cyrl"] = to_cyrillic(abstracts["uz"])
    keywords["uz-cyrl"] = [to_cyrillic(k) for k in keywords["uz"]]

    submission.metadata = {
        "title": titles,
        "abstract": abstracts,
        "keywords": keywords,
        "references": [
            line.strip() for line in data.get("references", "").splitlines() if line.strip()
        ],
    }
    submission.title_en = titles["en"]
    submission.title_uz = titles["uz"]
    submission.title_uz_cyrl = titles["uz-cyrl"]
    submission.title_ru = titles["ru"]
    submission.title = titles["en"]
    submission.abstract_en = abstracts["en"]
    submission.abstract_uz = abstracts["uz"]
    submission.abstract_uz_cyrl = abstracts["uz-cyrl"]
    submission.abstract_ru = abstracts["ru"]
    submission.abstract = abstracts["en"]
    submission.keywords_text = ", ".join(keywords["en"])
    submission.funding_statement = data.get("funding_statement", "")
    submission.conflict_of_interest_statement = data.get("conflict_of_interest_statement", "")
    submission.data_availability_statement = data.get("data_availability_statement", "")
    submission.save()
    submission.jel_codes.set(data["jel_codes"])


def _save_authors(submission: Submission, formset) -> None:
    """Persist the authors formset rows against the submission."""
    instances = formset.save(commit=False)
    for obj in formset.deleted_objects:
        obj.delete()
    for index, author in enumerate(instances, start=1):
        author.submission = submission
        if not author.order:
            author.order = index
        author.save()
    if not submission.authors.filter(is_corresponding=True).exists():
        first = submission.authors.order_by("order").first()
        if first is not None:
            first.is_corresponding = True
            first.save(update_fields=["is_corresponding", "updated_at"])


@login_required
def wizard_step4(request: HttpRequest, pk: int) -> HttpResponse:
    """Step 4 — suggested/opposed reviewers and cover letter."""
    submission = _get_draft(request, pk)
    if request.method == "POST":
        form = ReviewersForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save()
            submission.wizard_step = max(submission.wizard_step, 5)
            submission.save(update_fields=["wizard_step", "updated_at"])
            return redirect("submissions:wizard_step5", pk=submission.pk)
    else:
        form = ReviewersForm(
            instance=submission,
            initial={
                "suggested": "\n".join(submission.suggested_reviewers or []),
                "opposed": "\n".join(submission.opposed_reviewers or []),
            },
        )
    return TemplateResponse(
        request, "submissions/wizard_step4.html", _wizard_context(submission, 4, form=form)
    )


@login_required
def wizard_step5(request: HttpRequest, pk: int) -> HttpResponse:
    """Step 5 — summary and final submission."""
    submission = _get_draft(request, pk)
    problems = _completeness_problems(submission)

    if request.method == "POST":
        if problems:
            messages.error(request, _("Please complete every required item before submitting."))
        else:
            workflow.perform(submission, "submit", request.user, request=request)
            messages.success(
                request,
                _("Your manuscript has been submitted. Reference: %(ref)s")
                % {"ref": submission.reference},
            )
            return redirect("dashboard:home")

    return TemplateResponse(
        request,
        "submissions/wizard_step5.html",
        _wizard_context(
            submission,
            5,
            problems=problems,
            authors=submission.authors.order_by("order"),
            files=submission.files.order_by("kind"),
        ),
    )


def _completeness_problems(submission: Submission) -> list[str]:
    """Everything that still blocks submission."""
    problems: list[str] = []
    declarations = submission.author_declarations or {}
    if not all(declarations.get(key) for key, _label in DECLARATIONS):
        problems.append(str(_("All declarations in step 1 must be confirmed.")))
    if not submission.files.filter(kind=SubmissionFile.Kind.MANUSCRIPT_ANON).exists():
        problems.append(str(_("An anonymised manuscript file is required.")))
    if not submission.files.filter(kind=SubmissionFile.Kind.TITLE_PAGE).exists():
        problems.append(str(_("A title page file is required.")))
    metadata = submission.metadata or {}
    for code, label in (("en", _("English")), ("uz", _("Uzbek")), ("ru", _("Russian"))):
        if not metadata.get("title", {}).get(code):
            problems.append(str(_("Title in %(lang)s is missing.") % {"lang": label}))
        if not metadata.get("abstract", {}).get(code):
            problems.append(str(_("Abstract in %(lang)s is missing.") % {"lang": label}))
        if not metadata.get("keywords", {}).get(code):
            problems.append(str(_("Keywords in %(lang)s are missing.") % {"lang": label}))
    if not submission.jel_codes.exists():
        problems.append(str(_("At least one JEL code is required.")))
    if not submission.authors.exists():
        problems.append(str(_("At least one author is required.")))
    if not submission.authors.filter(is_corresponding=True).exists():
        problems.append(str(_("A corresponding author must be marked.")))
    return problems


@login_required
def upload_revision(request: HttpRequest, pk: int) -> HttpResponse:
    """Author uploads a revised manuscript and response letter."""
    submission = get_object_or_404(Submission, pk=pk, submitter=request.user)
    if submission.status != SubmissionStatus.REVISION_REQUESTED:
        raise PermissionDenied(_("No revision is currently requested."))

    if request.method == "POST":
        form = RevisionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            round_obj = submission.latest_round
            version = submission.files.filter(kind=SubmissionFile.Kind.REVISION).count() + 1
            SubmissionFile.objects.create(
                submission=submission,
                round=round_obj,
                kind=SubmissionFile.Kind.REVISION,
                file=form.cleaned_data["revision"],
                original_name=form.cleaned_data["revision"].name[:255],
                uploaded_by=request.user,
                version=version,
                size=form.cleaned_data["revision"].size,
            )
            if form.cleaned_data.get("response"):
                SubmissionFile.objects.create(
                    submission=submission,
                    round=round_obj,
                    kind=SubmissionFile.Kind.RESPONSE,
                    file=form.cleaned_data["response"],
                    uploaded_by=request.user,
                    version=version,
                )
            workflow.perform(
                submission,
                "resubmit",
                request.user,
                request=request,
                response_letter=form.cleaned_data["response_letter"],
            )
            messages.success(request, _("Your revision has been submitted."))
            return redirect("dashboard:home")
    else:
        form = RevisionUploadForm()

    return TemplateResponse(
        request,
        "submissions/upload_revision.html",
        {"submission": submission, "form": form},
    )


@login_required
def withdraw(request: HttpRequest, pk: int) -> HttpResponse:
    """Author withdraws a manuscript before acceptance."""
    submission = get_object_or_404(Submission, pk=pk, submitter=request.user)
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            workflow.perform(
                submission,
                "withdraw",
                request.user,
                request=request,
                reason=form.cleaned_data["reason"],
            )
            messages.success(request, _("The manuscript has been withdrawn."))
            return redirect("dashboard:home")
    else:
        form = WithdrawForm()
    return TemplateResponse(
        request, "submissions/withdraw.html", {"submission": submission, "form": form}
    )


@login_required
def delete_file(request: HttpRequest, pk: int) -> HttpResponse:
    """Remove a file from a draft submission."""
    submission_file = get_object_or_404(SubmissionFile, pk=pk)
    submission = submission_file.submission
    if submission.submitter_id != request.user.pk or not submission.is_editable_by_author:
        raise PermissionDenied
    submission_file.delete()
    messages.success(request, _("The file has been removed."))
    return redirect("submissions:wizard_step2", pk=submission.pk)
