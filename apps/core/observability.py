"""Structured logging and distributed tracing.

Two independent switches, both read from the environment so the same image
behaves correctly in Docker Compose, on a VPS and in Kubernetes:

* ``LOG_FORMAT=json`` — every log line becomes one JSON object on stdout, the
  shape Fluent Bit / Elasticsearch index without a parser.  Lines carry the
  active ``trace_id``/``span_id`` so Kibana and Jaeger link to each other.
* ``OTEL_EXPORTER_OTLP_ENDPOINT`` — when set, requests, SQL, Redis, outbound
  HTTP and Celery tasks are traced and exported over OTLP/HTTP (to an
  OpenTelemetry Collector, which forwards to Jaeger).  Unset, nothing is
  imported beyond the API and there is no overhead.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

logger = logging.getLogger(__name__)

AUDIT_LOGGER_NAME = "arer.audit"

# Attributes every ``LogRecord`` has; anything else was passed via ``extra=``.
_RESERVED = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys() | {"message", "asctime"}
)

_tracing_lock = threading.Lock()
_tracing_ready = False


def service_name() -> str:
    """Name reported to Jaeger and stamped on every JSON log line."""
    return os.environ.get("OTEL_SERVICE_NAME", "arer-web")


class JsonFormatter(logging.Formatter):
    """Render a ``LogRecord`` as a single-line JSON document."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialise the record, its ``extra`` fields and the current trace context."""
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": service_name(),
            "environment": os.environ.get("APP_ENV", "development"),
            "version": os.environ.get("APP_VERSION", "dev"),
        }
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            payload["trace_id"] = format(span_context.trace_id, "032x")
            payload["span_id"] = format(span_context.span_id, "016x")
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in vars(record).items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        return json.dumps(payload, default=str, ensure_ascii=False)


def tracing_enabled() -> bool:
    """Tracing is on only when an OTLP endpoint is configured."""
    return bool(os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")) and os.environ.get(
        "OTEL_SDK_DISABLED", "false"
    ).lower() not in {"1", "true", "yes"}


def init_tracing(role: str = "web") -> bool:
    """Install the tracer provider and auto-instrumentation once per process.

    Called from ``wsgi.py`` for gunicorn workers and from Celery's
    ``worker_process_init`` signal.  Returns ``True`` when tracing is active.
    """
    global _tracing_ready
    if not tracing_enabled():
        return False
    with _tracing_lock:
        if _tracing_ready:
            return True
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {
                "service.name": service_name(),
                "service.version": os.environ.get("APP_VERSION", "dev"),
                "deployment.environment": os.environ.get("APP_ENV", "development"),
                "service.instance.role": role,
            }
        )
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        # Probes and static files would drown real traffic in Jaeger.
        DjangoInstrumentor().instrument(excluded_urls="healthz,livez,static,media")
        PsycopgInstrumentor().instrument(enable_commenter=False)
        RedisInstrumentor().instrument()
        RequestsInstrumentor().instrument()
        CeleryInstrumentor().instrument()
        _tracing_ready = True
    logger.info("tracing enabled", extra={"otel_role": role})
    return True


def audit_event(action: str, **fields: Any) -> None:
    """Emit a security/editorial audit event on the dedicated audit logger.

    The database ``AuditLog`` stays the record editors browse; this stream is
    what the log pipeline ships to its own, longer-retained audit index.
    """
    logging.getLogger(AUDIT_LOGGER_NAME).info(
        "audit %s", action, extra={"audit_action": action, **fields}
    )
