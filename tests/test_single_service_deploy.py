"""A deploy without Redis (Railway with only Postgres) must still run the workflow."""

from __future__ import annotations

from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command
from kombu.exceptions import OperationalError

from apps.core.management.commands.seed_demo import DEMO_ADMIN_EMAIL
from apps.core.management.commands.seed_demo import Command as SeedCommand
from apps.submissions import tasks
from config.celery import ResilientTask, app

pytestmark = pytest.mark.django_db


def test_shared_tasks_use_the_resilient_base() -> None:
    """Every ``@shared_task`` inherits the broker-outage fallback."""
    assert isinstance(tasks.notify_submission_received, ResilientTask)
    assert issubclass(app.Task, ResilientTask)


def test_delay_runs_in_process_when_the_broker_is_down(settings) -> None:
    """A refused broker connection runs the task locally instead of raising."""
    settings.CELERY_TASK_ALWAYS_EAGER = False
    app.conf.task_always_eager = False
    try:
        with (
            mock.patch("celery.app.task.Task.apply_async", side_effect=OperationalError("refused")),
            mock.patch.object(ResilientTask, "apply", return_value="ran") as apply,
        ):
            result = tasks.notify_submission_received.delay(123)
    finally:
        app.conf.task_always_eager = True
    assert result == "ran"
    apply.assert_called_once_with((123,), {}, throw=False)


def test_other_errors_still_raise() -> None:
    """Only broker outages fall back; a programming error is not swallowed."""
    with (
        mock.patch("celery.app.task.Task.apply_async", side_effect=TypeError("bad args")),
        pytest.raises(TypeError),
    ):
        tasks.notify_submission_received.delay(1)


def test_demo_seed_runs_after_a_content_only_first_start(django_user_model) -> None:
    """Pages from a content-only first start must not block the later demo seed."""
    call_command("seed_demo", "--content-only", stdout=StringIO())
    assert SeedCommand._already_seeded(content_only=True)
    assert not SeedCommand._already_seeded(content_only=False)
    django_user_model.objects.create_user(email=DEMO_ADMIN_EMAIL, password="x" * 16)
    assert SeedCommand._already_seeded(content_only=False)


def test_settings_without_redis_use_a_shared_cache_and_eager_tasks() -> None:
    """With no REDIS_URL the base settings pick the database cache and eager Celery."""
    import importlib
    import os

    import config.settings.base as base

    dropped = {"REDIS_URL", "CELERY_BROKER_URL", "CELERY_TASK_ALWAYS_EAGER"}
    env = {k: v for k, v in os.environ.items() if k not in dropped}
    # Path.exists -> False keeps the developer's .env out of the reload.
    try:
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("pathlib.Path.exists", return_value=False),
        ):
            reloaded = importlib.reload(base)
            assert reloaded.CACHES["default"]["BACKEND"] == (
                "django.core.cache.backends.db.DatabaseCache"
            )
            assert reloaded.CELERY_TASK_ALWAYS_EAGER is True
        with (
            mock.patch.dict(os.environ, {**env, "REDIS_URL": "redis://redis:6379/0"}, clear=True),
            mock.patch("pathlib.Path.exists", return_value=False),
        ):
            reloaded = importlib.reload(base)
            assert reloaded.CACHES["default"]["BACKEND"].endswith("ResilientRedisCache")
            assert reloaded.CELERY_TASK_ALWAYS_EAGER is False
    finally:
        importlib.reload(base)
