"""Base Django settings shared by every environment.

Environment-specific modules (``dev``, ``prod``, ``test``) import everything
from here and then override.  All secrets and deployment-dependent values are
read from environment variables (see ``.env.example``).
"""

from __future__ import annotations

from pathlib import Path

import environ

from config import locale_info  # noqa: F401  (registers the uz-cyrl locale)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-do-not-use-in-production")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["http://localhost:8000", "http://127.0.0.1:8000"]
)

SITE_DOMAIN = env("SITE_DOMAIN", default="localhost:8000")
SITE_PROTOCOL = env("SITE_PROTOCOL", default="http")
SITE_URL = f"{SITE_PROTOCOL}://{SITE_DOMAIN}"
SITE_ID = 1

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
DJANGO_APPS = [
    "modeltranslation",  # must precede django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "django_tailwind_cli",
    "django_htmx",
    "widget_tweaks",
    "django_countries",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.orcid",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "axes",
    "auditlog",
    "django_celery_beat",
    "django_celery_results",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.journal",
    "apps.submissions",
    "apps.review",
    "apps.production",
    "apps.crossref",
    "apps.orcid",
    "apps.oai",
    "apps.citations",
    "apps.metrics",
    "apps.plagiarism",
    "apps.preservation",
    "apps.search",
    "apps.dashboard",
    "apps.api",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "apps.core.middleware.SiteSettingsMiddleware",
    "apps.accounts.middleware.StaffTwoFactorMiddleware",
    "axes.middleware.AxesMiddleware",
]

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.navigation",
                "apps.core.context_processors.language_links",
            ],
        },
    },
]

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres://arer:arer_dev_password@localhost:5432/arer",
    )
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DATABASES["default"]["ATOMIC_REQUESTS"] = False

# -----------------------------------------------------------------------------
# Cache / Celery
# -----------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "arer",
    }
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tashkent"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_TIME_LIMIT = 600
CELERY_TASK_SOFT_TIME_LIMIT = 540

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# --- allauth ---
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.accounts.adapters.SocialAccountAdapter"
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",
    "signup": "3/h",
    "reset_password": "3/h",
}
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[ARER] "
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = False

ORCID_BASE = env("ORCID_BASE", default="sandbox")
SOCIALACCOUNT_PROVIDERS = {
    "orcid": {
        "BASE_DOMAIN": "sandbox.orcid.org" if ORCID_BASE == "sandbox" else "orcid.org",
        "MEMBER_API": False,
        "APP": {
            "client_id": env("ORCID_CLIENT_ID", default=""),
            "secret": env("ORCID_CLIENT_SECRET", default=""),
            "key": "",
        },
    }
}

# --- django-axes ---
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = 0.5  # hours == 30 minutes
AXES_LOCKOUT_PARAMETERS = ["ip_address"]
AXES_RESET_ON_SUCCESS = True
AXES_ENABLED = True
AXES_LOCKOUT_TEMPLATE = "errors/lockout.html"

# --- OTP / 2FA ---
OTP_TOTP_ISSUER = "ARER Editorial System"
STAFF_2FA_REQUIRED = True

# -----------------------------------------------------------------------------
# Internationalisation
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("uz", "Oʻzbekcha"),
    ("uz-cyrl", "Ўзбекча"),
    ("ru", "Русский"),
]
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_SAMESITE = "Lax"
LOCALE_PATHS = [BASE_DIR / "locale"]
FORMAT_MODULE_PATH = ["config.formats"]

USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Tashkent"

MODELTRANSLATION_LANGUAGES = ("en", "uz", "uz-cyrl", "ru")
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    "default": ("en",),
    "uz-cyrl": ("uz", "en"),
    "uz": ("uz-cyrl", "en"),
    "ru": ("en",),
}
MODELTRANSLATION_AUTO_POPULATE = False

# -----------------------------------------------------------------------------
# Static & media
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# django-tailwind-cli (standalone binary — no Node required)
TAILWIND_CLI_VERSION = "4.1.11"
TAILWIND_CLI_SRC_CSS = "static/src/css/input.css"
TAILWIND_CLI_DIST_CSS = "css/output.css"
TAILWIND_CLI_AUTOMATIC_DOWNLOAD = True
TAILWIND_CLI_PATH = str(BASE_DIR / ".tailwind")

# The Tailwind source lives at static/src/css/input.css as required by
# DESIGN_BRIEF §2. collectstatic is always run with --ignore=src, so the
# source file never reaches the manifest storage backend.
SILENCED_SYSTEM_CHECKS = ["django_tailwind_cli.W001"]

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="editor@localhost")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
ANYMAIL = {"RESEND_API_KEY": env("RESEND_API_KEY", default="")}

# -----------------------------------------------------------------------------
# Journal-specific configuration
# -----------------------------------------------------------------------------
DOI_PREFIX = env("DOI_PREFIX", default="10.00000")
CROSSREF_TEST = env.bool("CROSSREF_TEST", default=True)
CROSSREF_DEPOSIT_URL = env(
    "CROSSREF_DEPOSIT_URL", default="https://test.crossref.org/servlet/deposit"
)
CROSSREF_DEPOSIT_URL_PROD = env(
    "CROSSREF_DEPOSIT_URL_PROD", default="https://doi.crossref.org/servlet/deposit"
)
CROSSREF_USER = env("CROSSREF_USER", default="")
CROSSREF_PASSWORD = env("CROSSREF_PASSWORD", default="")
CROSSREF_DEPOSITOR_NAME = env("CROSSREF_DEPOSITOR_NAME", default="ARER Editorial Office")
CROSSREF_DEPOSITOR_EMAIL = env("CROSSREF_DEPOSITOR_EMAIL", default=DEFAULT_FROM_EMAIL)
CROSSREF_REGISTRANT = env("CROSSREF_REGISTRANT", default="ALGORITHM Review of Economic Research")
CROSSREF_POLITE_MAILTO = env("CROSSREF_POLITE_MAILTO", default=DEFAULT_FROM_EMAIL)

PLAGIARISM_PROVIDER = env("PLAGIARISM_PROVIDER", default="manual")
ITHENTICATE_URL = env("ITHENTICATE_URL", default="")
ITHENTICATE_API_KEY = env("ITHENTICATE_API_KEY", default="")

MATOMO_URL = env("MATOMO_URL", default="")
MATOMO_SITE_ID = env("MATOMO_SITE_ID", default="")

IP_HASH_SALT = env("IP_HASH_SALT", default="dev-ip-hash-salt")
CLAMAV_HOST = env("CLAMAV_HOST", default="")
TURNSTILE_SITE_KEY = env("TURNSTILE_SITE_KEY", default="")
TURNSTILE_SECRET_KEY = env("TURNSTILE_SECRET_KEY", default="")

MAX_UPLOAD_SIZE_MB = env.int("MAX_UPLOAD_SIZE_MB", default=20)
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

BACKUP_DIR = env("BACKUP_DIR", default=str(BASE_DIR / "backups"))
BACKUP_RETENTION_DAYS = env.int("BACKUP_RETENTION_DAYS", default=30)

# Editorial policy constants (SPEC §2 decision register)
REVIEW_DUE_DAYS = 21
MINOR_REVISION_DUE_DAYS = 30
MAJOR_REVISION_DUE_DAYS = 60
MIN_REVIEWERS_PER_ROUND = 2
DEFAULT_SIMILARITY_THRESHOLD = 20
ARTICLE_MIN_WORDS = 4000
ARTICLE_MAX_WORDS = 10000
ABSTRACT_MIN_WORDS = 150
ABSTRACT_MAX_WORDS = 250
KEYWORDS_MIN = 5
KEYWORDS_MAX = 8
JEL_MIN = 1
JEL_MAX = 5

# -----------------------------------------------------------------------------
# REST framework
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min"},
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ["GET", "HEAD", "OPTIONS"]
CORS_URLS_REGEX = r"^/(api|oai)/.*$"

# -----------------------------------------------------------------------------
# Security defaults (tightened in prod.py)
# -----------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # HTMX reads the token from the cookie
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com", "data:"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"level": "WARNING", "handlers": ["console"], "propagate": False},
        "apps": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}
