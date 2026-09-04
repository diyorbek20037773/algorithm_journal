"""Role-based dashboards for authors, reviewers, editors and administrators."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.models import Role, User
from apps.accounts.permissions import user_can_edit_submission, user_can_view_submission
from apps.dashboard.forms import ProfileForm, TOTPSetupForm, UserDetailsForm
from apps.submissions import workflow
from apps.submissions.forms import (
    DecisionForm,
    DiscussionMessageForm,
    InviteReviewerForm,
    SimilarityForm,
)
from apps.submissions.models import (
    Discussion,
    DiscussionMessage,
    EditorialDecision,
    EditorNote,
    Review,
    ReviewAssignment,
    Submission,
    SubmissionFile,
    SubmissionStatus,
)
from apps.submissions.services import (
    build_decision_letter,
    find_reviewers,
    invite_reviewer,
    invite_reviewer_by_email,
)

PAGE_SIZE = 20

#: Editorial queues shown in the section-editor / EIC dashboard.
EDITOR_QUEUES: list[tuple[str, Any, list[str]]] = [
    ("new", _("New"), [SubmissionStatus.SUBMITTED]),
    ("screening", _("Screening"), [SubmissionStatus.SCREENING]),
    ("in_review", _("In review"), [SubmissionStatus.UNDER_REVIEW]),
    ("decision", _("Awaiting decision"), [SubmissionStatus.AWAITING_DECISION]),
    (
        "revisions",
        _("Revisions"),
        [SubmissionStatus.REVISION_REQUESTED, SubmissionStatus.RESUBMITTED],
    ),
    (
        "production",
        _("Accepted / in production"),
        [
            SubmissionStatus.ACCEPTED,
            SubmissionStatus.COPYEDITING,
            SubmissionStatus.AUTHOR_PROOF,
            SubmissionStatus.TYPESETTING,
            SubmissionStatus.READY_TO_PUBLISH,
        ],
    ),
]


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """Dispatch to the dashboard matching the user's primary role."""
    user = request.user
    context: dict[str, Any] = {"roles": sorted(user.role_names)}

    context["my_submissions"] = (
        Submission.objects.filter(submitter=user).with_related().order_by("-last_activity_at")[:10]
    )
    context["actions_needed"] = Submission.objects.filter(
        submitter=user,
        status__in=[SubmissionStatus.REVISION_REQUESTED, SubmissionStatus.AUTHOR_PROOF],
    )
    context["published_articles"] = [
        s.article
        for s in Submission.objects.filter(submitter=user).select_related("article")
        if s.article
    ]

    if user.is_reviewer or user.has_role(Role.REVIEWER):
        assignments = ReviewAssignment.objects.filter(reviewer=user).select_related(
            "round__submission"
        )
        context["review_invitations"] = assignments.filter(status=ReviewAssignment.Status.INVITED)
        context["active_reviews"] = assignments.filter(
            status__in=[ReviewAssignment.Status.ACCEPTED, ReviewAssignment.Status.OVERDUE]
        )

    if user.is_editorial_staff:
        queryset = Submission.objects.for_editor(user)
        context["editor_queues"] = [
            {
                "key": key,
                "label": label,
                "count": queryset.filter(status__in=statuses).count(),
                "items": list(queryset.filter(status__in=statuses).with_related()[:5]),
            }
            for key, label, statuses in EDITOR_QUEUES
        ]
        from apps.metrics.services import compute_kpi_window

        context["kpis"] = compute_kpi_window()

    return TemplateResponse(request, "dashboard/home.html", context)


@login_required
def queue(request: HttpRequest, key: str) -> HttpResponse:
    """A filterable, paginated editorial queue."""
    if not request.user.is_editorial_staff:
        raise PermissionDenied
    definition = next((q for q in EDITOR_QUEUES if q[0] == key), None)
    if definition is None:
        raise PermissionDenied
    _key, label, statuses = definition
    queryset = (
        Submission.objects.for_editor(request.user).filter(status__in=statuses).with_related()
    )

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(title__icontains=search) | queryset.filter(
            reference__icontains=search
        )
    section = request.GET.get("section")
    if section:
        queryset = queryset.filter(section__slug=section)
    order = request.GET.get("sort", "-last_activity_at")
    if order.lstrip("-") in {"last_activity_at", "submitted_at", "title", "status"}:
        queryset = queryset.order_by(order)

    paginator = Paginator(queryset, PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))
    template = (
        "dashboard/partials/queue_table.html"
        if request.headers.get("HX-Request")
        else "dashboard/queue.html"
    )
    return TemplateResponse(
        request,
        template,
        {
            "queue_key": key,
            "queue_label": label,
            "page_obj": page,
            "submissions": page.object_list,
            "queues": EDITOR_QUEUES,
            "search": search,
        },
    )


@login_required
def submission_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Editorial detail page with tabs for every aspect of a submission."""
    submission = get_object_or_404(Submission.objects.with_related(), pk=pk)
    if not user_can_view_submission(request.user, submission):
        raise PermissionDenied
    is_editor = user_can_edit_submission(request.user, submission)

    rounds = list(
        submission.rounds.prefetch_related("assignments__reviewer", "assignments__review").order_by(
            "number"
        )
    )
    context: dict[str, Any] = {
        "submission": submission,
        "is_editor": is_editor,
        "rounds": rounds,
        "files": submission.files.order_by("kind", "-version"),
        "authors": submission.authors.order_by("order"),
        "decisions": submission.decisions.select_related("decided_by"),
        "notes": submission.notes.select_related("author") if is_editor else [],
        "discussions": submission.discussions.prefetch_related("messages__author"),
        "transitions": workflow.available_transitions(submission, request.user)
        if is_editor
        else [],
        "similarity_form": SimilarityForm(instance=submission) if is_editor else None,
        "decision_form": DecisionForm() if is_editor else None,
        "invite_form": InviteReviewerForm() if is_editor else None,
        "message_form": DiscussionMessageForm(),
        "active_tab": request.GET.get("tab", "summary"),
    }
    return TemplateResponse(request, "dashboard/submission_detail.html", context)


@login_required
@require_POST
def record_similarity(request: HttpRequest, pk: int) -> HttpResponse:
    """Store the plagiarism-check outcome during screening."""
    submission = get_object_or_404(Submission, pk=pk)
    if not user_can_edit_submission(request.user, submission):
        raise PermissionDenied
    form = SimilarityForm(request.POST, request.FILES, instance=submission)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.similarity_checked_by = request.user
        submission.similarity_checked_at = timezone.now()
        submission.save()
        messages.success(request, _("The similarity result has been recorded."))
    else:
        messages.error(request, _("Please correct the similarity form."))
    return redirect("dashboard:submission_detail", pk=submission.pk)


@login_required
@require_POST
def run_transition(request: HttpRequest, pk: int) -> HttpResponse:
    """Run any workflow transition available to the current user."""
    submission = get_object_or_404(Submission, pk=pk)
    transition = request.POST.get("transition", "")
    editor_id = request.POST.get("editor")
    kwargs: dict[str, Any] = {}
    if editor_id:
        kwargs["editor"] = User.objects.filter(pk=editor_id).first()
    try:
        workflow.perform(submission, transition, request.user, request=request, **kwargs)
        messages.success(request, _("Done."))
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    except PermissionDenied:
        messages.error(request, _("You may not perform this action."))
    return redirect("dashboard:submission_detail", pk=submission.pk)


@login_required
def reviewer_finder(request: HttpRequest, pk: int) -> HttpResponse:
    """Search for suitable reviewers for a submission."""
    submission = get_object_or_404(Submission, pk=pk)
    if not user_can_edit_submission(request.user, submission):
        raise PermissionDenied
    existing = list(
        ReviewAssignment.objects.filter(round__submission=submission).values_list(
            "reviewer_id", flat=True
        )
    )
    existing.append(submission.submitter_id)
    candidates = find_reviewers(
        query=request.GET.get("q", ""),
        jel_codes=[c.code for c in submission.jel_codes.all()],
        exclude_users=existing,
    )
    template = (
        "dashboard/partials/reviewer_finder.html"
        if request.headers.get("HX-Request")
        else "dashboard/reviewer_finder.html"
    )
    return TemplateResponse(
        request,
        template,
        {
            "submission": submission,
            "candidates": candidates,
            "query": request.GET.get("q", ""),
            "invite_form": InviteReviewerForm(),
        },
    )


@login_required
@require_POST
def invite_reviewer_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Invite a reviewer, by account or by e-mail address."""
    submission = get_object_or_404(Submission, pk=pk)
    if not user_can_edit_submission(request.user, submission):
        raise PermissionDenied
    round_obj = submission.latest_round
    if round_obj is None:
        messages.error(request, _("Send the manuscript to review before inviting reviewers."))
        return redirect("dashboard:submission_detail", pk=submission.pk)

    form = InviteReviewerForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Choose a reviewer or enter an e-mail address."))
        return redirect("dashboard:reviewer_finder", pk=submission.pk)

    try:
        if form.cleaned_data.get("reviewer_id"):
            reviewer = get_object_or_404(User, pk=form.cleaned_data["reviewer_id"])
            invite_reviewer(
                round_obj,
                reviewer,
                invited_by=request.user,
                due_days=form.cleaned_data.get("due_days"),
            )
        else:
            invite_reviewer_by_email(
                round_obj,
                form.cleaned_data["email"],
                invited_by=request.user,
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
            )
        messages.success(request, _("The invitation has been sent."))
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("dashboard:submission_detail", pk=submission.pk)


@login_required
@require_POST
def cancel_assignment(request: HttpRequest, pk: int) -> HttpResponse:
    """Cancel an outstanding review invitation."""
    assignment = get_object_or_404(ReviewAssignment, pk=pk)
    if not user_can_edit_submission(request.user, assignment.round.submission):
        raise PermissionDenied
    assignment.status = ReviewAssignment.Status.CANCELLED
    assignment.save(update_fields=["status", "updated_at"])
    messages.success(request, _("The invitation has been cancelled."))
    return redirect("dashboard:submission_detail", pk=assignment.round.submission_id)


@login_required
@require_POST
def remind_reviewer(request: HttpRequest, pk: int) -> HttpResponse:
    """Send a manual reminder to a reviewer."""
    from apps.submissions.tasks import send_reviewer_invitation

    assignment = get_object_or_404(ReviewAssignment, pk=pk)
    if not user_can_edit_submission(request.user, assignment.round.submission):
        raise PermissionDenied
    send_reviewer_invitation.delay(assignment.pk)
    assignment.reminders_sent += 1
    assignment.last_reminder_at = timezone.now()
    assignment.save(update_fields=["reminders_sent", "last_reminder_at", "updated_at"])
    messages.success(request, _("A reminder has been sent."))
    return redirect("dashboard:submission_detail", pk=assignment.round.submission_id)


@login_required
@require_POST
def rate_review(request: HttpRequest, pk: int) -> HttpResponse:
    """Editor rates the quality of a completed review."""
    review = get_object_or_404(Review, pk=pk)
    if not user_can_edit_submission(request.user, review.assignment.round.submission):
        raise PermissionDenied
    rating = request.POST.get("rating")
    if rating and rating.isdigit() and 1 <= int(rating) <= 5:
        review.quality_rating = int(rating)
        review.save(update_fields=["quality_rating", "updated_at"])
        messages.success(request, _("Thank you — the rating has been saved."))
    return redirect("dashboard:submission_detail", pk=review.assignment.round.submission_id)


@login_required
def decide(request: HttpRequest, pk: int) -> HttpResponse:
    """Decision dialog, pre-filled with a merged letter."""
    submission = get_object_or_404(Submission.objects.with_related(), pk=pk)
    if not user_can_edit_submission(request.user, submission):
        raise PermissionDenied

    if request.method == "POST":
        form = DecisionForm(request.POST)
        if form.is_valid():
            try:
                workflow.record_decision(
                    submission,
                    decision=form.cleaned_data["decision"],
                    user=request.user,
                    letter=form.cleaned_data["letter"],
                    request=request,
                )
                messages.success(request, _("The decision has been recorded and sent."))
                return redirect("dashboard:submission_detail", pk=submission.pk)
            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, getattr(exc, "messages", [str(exc)])[0])
    else:
        preset = request.GET.get("decision", EditorialDecision.Decision.MINOR_REVISION)
        form = DecisionForm(
            initial={"decision": preset, "letter": build_decision_letter(submission, preset)}
        )

    return TemplateResponse(
        request,
        "dashboard/decide.html",
        {
            "submission": submission,
            "form": form,
            "reviews": Review.objects.filter(
                assignment__round__submission=submission, is_draft=False
            ).select_related("assignment__reviewer"),
        },
    )


@login_required
@require_POST
def post_message(request: HttpRequest, pk: int) -> HttpResponse:
    """Post a message into a submission's discussion thread."""
    submission = get_object_or_404(Submission, pk=pk)
    if not user_can_view_submission(request.user, submission):
        raise PermissionDenied
    form = DiscussionMessageForm(request.POST)
    if form.is_valid():
        visibility = (
            Discussion.Visibility.EDITORS_ONLY
            if user_can_edit_submission(request.user, submission)
            and request.POST.get("visibility") == "editors"
            else Discussion.Visibility.AUTHOR_EDITOR
        )
        discussion, _created = Discussion.objects.get_or_create(
            submission=submission,
            visibility=visibility,
            defaults={"subject": _("Correspondence"), "created_by": request.user},
        )
        DiscussionMessage.objects.create(
            discussion=discussion, author=request.user, body=form.cleaned_data["body"]
        )
        messages.success(request, _("Message posted."))
    return redirect(f"{submission.get_absolute_url()}?tab=discussion")


@login_required
@require_POST
def add_note(request: HttpRequest, pk: int) -> HttpResponse:
    """Add a private editorial note."""
    submission = get_object_or_404(Submission, pk=pk)
    if not user_can_edit_submission(request.user, submission):
        raise PermissionDenied
    body = request.POST.get("body", "").strip()
    if body:
        EditorNote.objects.create(submission=submission, author=request.user, body=body)
        messages.success(request, _("Note saved."))
    return redirect("dashboard:submission_detail", pk=submission.pk)


@login_required
def submission_file(request: HttpRequest, pk: int) -> HttpResponse:
    """Serve a submission file to an authorised user."""
    submission_file_obj = get_object_or_404(SubmissionFile, pk=pk)
    submission = submission_file_obj.submission
    user = request.user
    allowed = user_can_edit_submission(user, submission) or submission.submitter_id == user.pk
    if not allowed and submission_file_obj.is_visible_to_reviewers:
        allowed = ReviewAssignment.objects.filter(
            reviewer=user, round__submission=submission
        ).exists()
    if not allowed:
        raise PermissionDenied
    response = FileResponse(submission_file_obj.file.open("rb"))
    response["Content-Disposition"] = (
        f'inline; filename="{submission.reference or submission.pk}-{submission_file_obj.kind}"'
    )
    return response


@login_required
def reports(request: HttpRequest) -> HttpResponse:
    """Editorial KPI reports with CSV export."""
    if not request.user.is_editorial_staff:
        raise PermissionDenied
    from apps.metrics.models import EditorialKPI
    from apps.metrics.services import compute_kpi_window, monthly_series

    if request.GET.get("format") == "csv":
        import csv

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="arer-editorial-kpi.csv"'
        writer = csv.writer(response)
        writer.writerow(["month", "submissions", "accepted"])
        for row in monthly_series(24):
            writer.writerow([row["month"].isoformat(), row["submissions"], row["accepted"]])
        return response

    return TemplateResponse(
        request,
        "dashboard/reports.html",
        {
            "kpis": compute_kpi_window(),
            "monthly": monthly_series(),
            "snapshots": EditorialKPI.objects.all()[:24],
        },
    )


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """Edit the signed-in user's account and scholarly profile."""
    from apps.accounts.models import Profile

    profile_obj, _created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = UserDetailsForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _("Your profile has been updated."))
            return redirect("dashboard:profile")
    else:
        user_form = UserDetailsForm(instance=request.user)
        profile_form = ProfileForm(instance=profile_obj)
    return TemplateResponse(
        request,
        "dashboard/profile.html",
        {"user_form": user_form, "profile_form": profile_form, "profile": profile_obj},
    )


@login_required
def two_factor_setup(request: HttpRequest) -> HttpResponse:
    """Enrol a TOTP device (mandatory for editorial staff)."""
    import base64
    import io as _io

    import qrcode
    from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
    from django_otp.plugins.otp_totp.models import TOTPDevice

    device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if device is None and not request.user.has_verified_totp:
        device = TOTPDevice.objects.create(user=request.user, name="default", confirmed=False)

    if request.user.has_verified_totp and device is None:
        return TemplateResponse(request, "dashboard/two_factor.html", {"already_enrolled": True})

    recovery_codes: list[str] = []
    if request.method == "POST":
        form = TOTPSetupForm(request.POST)
        if (
            form.is_valid()
            and device is not None
            and device.verify_token(form.cleaned_data["token"])
        ):
            device.confirmed = True
            device.save()
            request.user.must_enroll_2fa = False
            request.user.save(update_fields=["must_enroll_2fa"])
            static_device, _created = StaticDevice.objects.get_or_create(
                user=request.user, name="recovery"
            )
            static_device.token_set.all().delete()
            for _index in range(10):
                token = StaticToken.random_token()
                StaticToken.objects.create(device=static_device, token=token)
                recovery_codes.append(token)
            messages.success(request, _("Two-factor authentication is now active."))
            return TemplateResponse(
                request,
                "dashboard/two_factor.html",
                {"success": True, "recovery_codes": recovery_codes},
            )
        messages.error(request, _("That code is not valid. Please try again."))
    else:
        form = TOTPSetupForm()

    qr_data = ""
    if device is not None:
        image = qrcode.make(device.config_url)
        buffer = _io.BytesIO()
        image.save(buffer, format="PNG")
        qr_data = base64.b64encode(buffer.getvalue()).decode()

    return TemplateResponse(
        request,
        "dashboard/two_factor.html",
        {"form": form, "device": device, "qr_data": qr_data},
    )
