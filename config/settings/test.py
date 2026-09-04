"""Test settings — fast hashing, eager Celery, in-memory cache and e-mail."""

from __future__ import annotations

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*", "testserver", "localhost", "127.0.0.1"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "arer-test",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

AXES_ENABLED = False
STAFF_2FA_REQUIRED = True

STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

MEDIA_ROOT = BASE_DIR / ".pytest-media"

# Tests must not be throttled.
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {"anon": "10000/min"}}

RATELIMIT_ENABLE = False

LOGGING["root"]["level"] = "WARNING"
