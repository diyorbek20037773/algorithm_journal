"""Production settings — hardened security, S3-capable storage, Resend e-mail."""

from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = False

# --- HTTPS / transport security ----------------------------------------------
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)  # noqa: F405
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)  # noqa: F405
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# --- Storage ------------------------------------------------------------------
if env("STORAGE_BACKEND", default="local") == "s3":  # noqa: F405
    INSTALLED_APPS = INSTALLED_APPS + ["storages"]  # noqa: F405
    STORAGES["default"] = {  # noqa: F405
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env("AWS_ACCESS_KEY_ID", default=""),  # noqa: F405
            "secret_key": env("AWS_SECRET_ACCESS_KEY", default=""),  # noqa: F405
            "bucket_name": env("AWS_STORAGE_BUCKET_NAME", default=""),  # noqa: F405
            "endpoint_url": env("AWS_S3_ENDPOINT_URL", default=None),  # noqa: F405
            "region_name": env("AWS_S3_REGION_NAME", default=""),  # noqa: F405
            "default_acl": "private",
            "querystring_auth": True,
        },
    }

# --- E-mail -------------------------------------------------------------------
if env("RESEND_API_KEY", default=""):  # noqa: F405
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

# --- Performance --------------------------------------------------------------
CONN_MAX_AGE = 60
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]
TEMPLATES[0]["APP_DIRS"] = False  # noqa: F405

# --- Admin hardening ----------------------------------------------------------
ADMIN_URL = env("ADMIN_URL", default="admin/")  # noqa: F405
