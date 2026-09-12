# syntax=docker/dockerfile:1
# =============================================================================
# ALGORITHM: Review of Economic Research — application image (multi-stage)
# Stage 1 builds the Python environment with uv; stage 2 is the slim runtime.
# =============================================================================

FROM python:3.12-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
        libqpdf-dev \
        zlib1g-dev \
        libjpeg-dev \
        libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml README.md uv.lock ./

# Install the exact versions uv.lock pins, into the standalone /opt/venv the
# runtime stage copies.  `uv export` reads the lock without needing the project
# venv layout that `uv sync` expects.
RUN uv venv /opt/venv \
    && uv export --frozen --extra dev --no-hashes --no-emit-project -o /tmp/requirements.txt \
    && uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt

# -----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.dev

RUN apt-get update && apt-get install --no-install-recommends -y \
        libpq5 \
        libqpdf29 \
        libmagic1 \
        gettext \
        curl \
        postgresql-client \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash arer

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=arer:arer . /app

# chmod belt-and-braces: a checkout made on Windows can lose the executable
# bit, and tini then fails with "exec entrypoint.sh: Permission denied" on
# any Linux host that builds from the image rather than a bind mount.
RUN mkdir -p /app/media /app/staticfiles /app/backups /app/exports /app/.tailwind \
    && chmod +x /app/scripts/*.sh \
    && chown -R arer:arer /app

USER arer

# Compile the .po catalogues so that the uz-cyrl locale is active at runtime.
RUN python manage.py compilemessages --ignore=.venv --ignore=node_modules || true

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--", "/app/scripts/entrypoint.sh"]
# Production by default. A platform that runs the image as-is (Railway, a bare
# `docker run`) must get gunicorn, not the development server; the dev compose
# file passes `web` explicitly.
CMD ["prod"]
