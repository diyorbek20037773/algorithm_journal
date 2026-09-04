"""Development settings — debug on, permissive security, Mailpit e-mail."""

from __future__ import annotations

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Mailpit in Docker, console fallback for bare-metal development.
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# Serve unhashed static files in development (no collectstatic required).
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

INTERNAL_IPS = ["127.0.0.1", "localhost"]

AXES_ENABLED = env.bool("AXES_ENABLED", default=True)

# Keep the developer experience fast: no HTTPS redirects, no HSTS.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
