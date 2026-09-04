"""Production settings — hardened security, S3-capable storage, Resend e-mail."""

from __future__ import annotations

from .base import *

DEBUG = False

# --- HTTPS / transport security ----------------------------------------------
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# --- Storage ------------------------------------------------------------------
if env("STORAGE_BACKEND", default="local") == "s3":
    INSTALLED_APPS = [*INSTALLED_APPS, "storages"]
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env("AWS_ACCESS_KEY_ID", default=""),
            "secret_key": env("AWS_SECRET_ACCESS_KEY", default=""),
            "bucket_name": env("AWS_STORAGE_BUCKET_NAME", default=""),
            "endpoint_url": env("AWS_S3_ENDPOINT_URL", default=None),
            "region_name": env("AWS_S3_REGION_NAME", default=""),
            "default_acl": "private",
            "querystring_auth": True,
        },
    }

# --- E-mail -------------------------------------------------------------------
if env("RESEND_API_KEY", default=""):
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

# --- Performance --------------------------------------------------------------
CONN_MAX_AGE = 60
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]
TEMPLATES[0]["APP_DIRS"] = False

# --- Admin hardening ----------------------------------------------------------
ADMIN_URL = env("ADMIN_URL", default="admin/")
