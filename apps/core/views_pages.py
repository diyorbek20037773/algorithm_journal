"""Views for the About hub, author/reviewer hubs, contact and statistics."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django_ratelimit.decorators import ratelimit

from apps.core.forms import ContactForm
from apps.core.models import IndexingService, Page
from apps.core.services import client_ip, send_templated_email


def _page_context(request: HttpRequest, slug: str) -> dict[str, Any]:
    """Shared context for a CMS-backed policy page."""
    page = get_object_or_404(Page.objects.published(), slug=slug)
    return {
        "page": page,
        "siblings": Page.objects.in_menu(page.menu_group),
        "meta_description": page.seo_description,
    }


def named_page(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a policy page that has its own named URL."""
    return TemplateResponse(request, "core/page_detail.html", _page_context(request, slug))


def about(request: HttpRequest) -> HttpResponse:
    """The About landing page with the journal's identifying facts."""
    context = _page_context(request, "about")
    context["show_identity_panel"] = True
    return TemplateResponse(request, "core/about.html", context)


def indexing(request: HttpRequest) -> HttpResponse:
    """Indexing and abstracting page listing only real, active services."""
    context = _page_context(request, "indexing")
    context["services"] = IndexingService.objects.filter(is_active=True)
    context["planned_services"] = IndexingService.objects.filter(is_active=False)
    return TemplateResponse(request, "core/indexing.html", context)


def for_authors(request: HttpRequest) -> HttpResponse:
    """Guided author funnel: scope → prepare → checklist → submit → after."""
    context = _page_context(request, "for-authors")
    context["author_pages"] = Page.objects.in_menu(Page.MenuGroup.AUTHORS)
    return TemplateResponse(request, "core/for_authors.html", context)


def for_reviewers(request: HttpRequest) -> HttpResponse:
    """Reviewer guidelines hub."""
    context = _page_context(request, "reviewer-guidelines")
    context["reviewer_pages"] = Page.objects.in_menu(Page.MenuGroup.REVIEWERS)
    return TemplateResponse(request, "core/for_reviewers.html", context)


#: The twelve items an author confirms before opening the submission wizard.
CHECKLIST_ITEMS: list[Any] = [
    _("The manuscript is original, unpublished, and not under consideration elsewhere."),
    _("The article is between 4,000 and 10,000 words (2,000–4,000 for a short communication)."),
    _("The manuscript file is anonymised: no author names, affiliations, acknowledgements or self-identifying citations."),
    _("A separate title page lists all authors, affiliations with city and country, ORCID iDs and the corresponding author."),
    _("Title, abstract (150–250 words) and 5–8 keywords are provided in English, Uzbek and Russian."),
    _("Between one and five JEL classification codes have been selected."),
    _("The structure follows IMRaD: introduction, literature, methods, results, discussion, conclusion."),
    _("References follow APA 7th edition, with DOIs where available; non-Latin sources include a transliteration and an English translation."),
    _("Tables and figures are numbered, captioned and referred to in the text; figures are legible at print size."),
    _("Funding, conflict of interest, data availability and generative-AI use are declared."),
    _("All co-authors have approved the submission and agree to publication under CC BY 4.0."),
    _("Research involving human participants states the ethical approval or explains why none was required."),
]


def checklist(request: HttpRequest) -> HttpResponse:
    """Interactive pre-submission checklist mirroring the wizard."""
    context = _page_context(request, "submission-checklist")
    context["checklist_items"] = CHECKLIST_ITEMS
    return TemplateResponse(request, "core/checklist.html", context)


def templates_download(request: HttpRequest) -> HttpResponse:
    """Manuscript template download page (DOCX and LaTeX)."""
    context = _page_context(request, "manuscript-template")
    return TemplateResponse(request, "core/templates_download.html", context)


@ratelimit(key="ip", rate="3/h", method="POST", block=False)
def contact(request: HttpRequest) -> HttpResponse:
    """Contact page with an anti-spam protected message form."""
    context = _page_context(request, "contact")
    was_limited = getattr(request, "limited", False)

    if request.method == "POST":
        form = ContactForm(request.POST)
        if was_limited:
            messages.error(
                request, _("Too many messages have been sent from this address. Please try later.")
            )
        elif form.is_valid():
            message = form.save(commit=False)
            message.ip = client_ip(request)
            message.save()
            site = request.site_settings
            send_templated_email(
                "contact_form",
                to=[site.contact_email or settings.DEFAULT_FROM_EMAIL],
                context={
                    "name": message.name,
                    "email": message.email,
                    "subject": message.subject,
                    "message": message.body,
                },
                fallback_subject=f"[Contact] {message.subject}",
                fallback_body=(
                    f"**From:** {message.name} <{message.email}>\n\n{message.body}"
                ),
            )
            messages.success(request, _("Thank you — your message has been sent."))
            return redirect("core:contact")
    else:
        form = ContactForm()

    context["form"] = form
    return TemplateResponse(request, "core/contact.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Public statistics page (SPEC §6.9)."""
    from apps.metrics.services import public_statistics

    context: dict[str, Any] = {"stats": public_statistics()}
    page = Page.objects.published().filter(slug="statistics").first()
    context["page"] = page
    return TemplateResponse(request, "core/statistics.html", context)
