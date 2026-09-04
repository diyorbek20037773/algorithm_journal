"""Language-neutral galley download routes with usage counting."""

from __future__ import annotations

import mimetypes
import os

from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from apps.journal.models import Article, Galley


def _serve(request: HttpRequest, galley: Galley) -> HttpResponse:
    """Stream a galley file, delegating to the front proxy where possible."""
    if not galley.file:
        raise Http404("Galley file missing")

    filename = f"{galley.article_id}-{galley.label}".lower().replace(" ", "-")
    suffix = os.path.splitext(galley.file.name)[1] or ".pdf"
    download_name = f"{filename}{suffix}"
    content_type = galley.mime or mimetypes.guess_type(galley.file.name)[0] or "application/octet-stream"

    if not settings.DEBUG and getattr(settings, "USE_X_ACCEL_REDIRECT", False):
        response = HttpResponse(status=200)
        response["X-Accel-Redirect"] = f"/protected/{galley.file.name}"
        response["Content-Type"] = content_type
        response["Content-Disposition"] = f'inline; filename="{download_name}"'
        return response

    response = FileResponse(galley.file.open("rb"), content_type=content_type)
    response["Content-Disposition"] = f'inline; filename="{download_name}"'
    response["Content-Length"] = str(galley.size or galley.file.size)
    return response


@require_GET
def article_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    """Serve the primary PDF galley — the stable ``citation_pdf_url``."""
    from apps.metrics.services import record_access

    article = get_object_or_404(Article.objects.public().prefetch_related("galleys"), pk=pk)
    galley = article.primary_galley
    if galley is None:
        raise Http404("No PDF galley for this article")
    record_access(request, article, kind="download", galley=galley)
    return _serve(request, galley)


@require_GET
def galley_download(request: HttpRequest, pk: int, galley_id: int) -> HttpResponse:
    """Serve any galley belonging to a publicly visible article."""
    from apps.metrics.services import record_access

    article = get_object_or_404(Article.objects.public(), pk=pk)
    galley = get_object_or_404(Galley, pk=galley_id, article=article)
    record_access(request, article, kind="download", galley=galley)
    return _serve(request, galley)
