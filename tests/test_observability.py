"""Structured logging, tracing switches, audit event stream and probes."""

from __future__ import annotations

import json
import logging

import pytest
from opentelemetry.sdk.trace import TracerProvider

from apps.core import observability
from apps.core.models import AuditLog
from apps.core.observability import AUDIT_LOGGER_NAME, JsonFormatter, init_tracing
from apps.core.services import log_action


def _record(msg: str = "hello %s", args: tuple = ("world",), **extra) -> logging.LogRecord:
    record = logging.LogRecord("apps.test", logging.WARNING, __file__, 1, msg, args, None)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_one_json_object(monkeypatch) -> None:
    """Each line is valid JSON with level, logger, message and service metadata."""
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_VERSION", "sha-abc123")
    line = JsonFormatter().format(_record(request_id="r-1"))
    assert "\n" not in line
    payload = json.loads(line)
    assert payload["level"] == "WARNING"
    assert payload["logger"] == "apps.test"
    assert payload["message"] == "hello world"
    assert payload["environment"] == "staging"
    assert payload["version"] == "sha-abc123"
    assert payload["request_id"] == "r-1"
    assert "trace_id" not in payload


def test_json_formatter_includes_active_trace_ids() -> None:
    """Inside a span the line carries the W3C trace and span ids."""
    tracer = TracerProvider().get_tracer("test")
    with tracer.start_as_current_span("unit") as span:
        payload = json.loads(JsonFormatter().format(_record()))
        context = span.get_span_context()
    assert payload["trace_id"] == format(context.trace_id, "032x")
    assert payload["span_id"] == format(context.span_id, "016x")


def test_json_formatter_serialises_exceptions() -> None:
    """Tracebacks stay inside the JSON document instead of breaking lines."""
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord("apps.test", logging.ERROR, __file__, 1, "failed", (), None)
        record.exc_info = sys.exc_info()
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError: boom" in payload["exception"]


def test_tracing_is_off_without_endpoint(monkeypatch) -> None:
    """No OTLP endpoint means no provider, no instrumentation, no overhead."""
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    assert observability.tracing_enabled() is False
    assert init_tracing("web") is False


def test_wsgi_instruments_before_building_the_handler() -> None:
    """Regression: instrumenting after get_wsgi_application() lost every request span."""
    from pathlib import Path

    source = (Path(__file__).resolve().parent.parent / "config" / "wsgi.py").read_text("utf-8")
    assert source.index('init_tracing("web")') < source.index(
        "application = get_wsgi_application()"
    )


def test_tracing_respects_sdk_disabled(monkeypatch) -> None:
    """OTEL_SDK_DISABLED wins over a configured endpoint (e.g. the migrate Job)."""
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    assert observability.tracing_enabled() is False


@pytest.mark.django_db
def test_log_action_writes_database_row_and_audit_stream(caplog, editor_user) -> None:
    """The audit trail lands in the database and on the dedicated audit logger."""
    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER_NAME):
        entry = log_action(AuditLog.Action.PUBLISH, actor=editor_user, target="Article 7")
    assert AuditLog.objects.filter(pk=entry.pk, action="publish").exists()
    records = [r for r in caplog.records if r.name == AUDIT_LOGGER_NAME]
    assert len(records) == 1
    assert records[0].audit_action == "publish"
    assert records[0].actor_id == editor_user.pk
    assert records[0].target == "Article 7"
    assert records[0].audit_id == entry.pk


@pytest.mark.django_db
def test_failed_login_reaches_audit_stream(caplog, client_anon) -> None:
    """Failed sign-ins are security events and must be shipped to the audit index."""
    from django.contrib.auth import authenticate

    with caplog.at_level(logging.INFO, logger=AUDIT_LOGGER_NAME):
        assert authenticate(username="nobody@example.org", password="wrong-password") is None
    actions = [getattr(r, "audit_action", None) for r in caplog.records]
    assert "login_failed" in actions


def test_livez_view_touches_no_backend(rf) -> None:
    """The liveness view itself needs no database (no django_db mark: access would fail)."""
    from apps.core.views import livez

    response = livez(rf.get("/livez/"))
    assert response.status_code == 200
    assert json.loads(response.content) == {"status": "ok"}
    assert "no-cache" in response["Cache-Control"]


@pytest.mark.django_db
def test_livez_route_is_language_neutral(client_anon) -> None:
    """Probes hit /livez/ directly, never a /en/ redirect."""
    response = client_anon.get("/livez/")
    assert response.status_code == 200
