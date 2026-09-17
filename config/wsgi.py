"""WSGI entry point."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

from apps.core.observability import init_tracing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# Must run before get_wsgi_application(): the Django instrumentation adds its
# middleware to settings, and the handler freezes the middleware chain when it
# is built.  Instrumenting afterwards yields orphan SQL/Redis spans and no
# request spans.  A no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set.
init_tracing("web")

application = get_wsgi_application()
