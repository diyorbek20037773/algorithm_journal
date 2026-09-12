# Railway — staging deployment

Railway is a good place to **show the site and test it**. It is not a place for
the production database: the client's terms of reference (§3.4) require the
personal data of Uzbek citizens — authors' and reviewers' names, e-mails and
affiliations — to be stored on servers in Uzbekistan, and Railway has no region
there. Use it for staging with demo data; put production on a VPS in Uzbekistan
per [`DEPLOYMENT.md`](DEPLOYMENT.md).

## Why the first deploy failed

```
[FATAL tini (2)] exec /app/scripts/entrypoint.sh failed: Permission denied
```

The repository was checked out on Windows, where git does not record the
executable bit, so `scripts/entrypoint.sh` was committed as `100644`. Docker
Desktop on Windows masks this through the bind mount, which is why it worked
locally and nowhere else. Fixed twice over: the files are now `100755` in git,
and the Dockerfile runs `chmod +x scripts/*.sh` regardless.

Two more things Railway needs that a compose stack does not:

* the container has to listen on Railway's `$PORT` — gunicorn now binds
  `0.0.0.0:${PORT:-8000}`;
* the image's default command must be production — `CMD ["prod"]` now starts
  gunicorn, where it used to start the development server.

## Services

One Railway project, four services, all built from this repository's
`Dockerfile`. The image is the same; only the start command differs.

| Service | Start command | Notes |
|---|---|---|
| `web` | *(default — `prod`)* | migrates, collects static, runs gunicorn |
| `worker` | `worker` | Celery worker: e-mail, Crossref deposits, PDF stamping |
| `beat` | `beat` | Celery beat: reminders, nightly aggregation |
| Postgres | Railway plugin | provides `DATABASE_URL` |
| Redis | Railway plugin | provides `REDIS_URL` |

Set the start command under *Settings → Deploy → Custom Start Command*. Leave
`web` empty so the Dockerfile default applies.

## Variables

Set these on every app service (Railway lets you share them through a
*Shared Variables* group). Values marked *generate* are secrets you create.

```
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=            # generate: python -c "import secrets;print(secrets.token_urlsafe(50))"
DJANGO_ALLOWED_HOSTS=algorithmjournal-production.up.railway.app
SITE_DOMAIN=algorithmjournal-production.up.railway.app
SITE_PROTOCOL=https
DJANGO_CSRF_TRUSTED_ORIGINS=https://algorithmjournal-production.up.railway.app

DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

DB_POOL=true
DB_POOL_MAX=4
GUNICORN_WORKERS=              # empty = 2×CPU+1; set 3 on a small plan
GUNICORN_THREADS=4

# Railway terminates TLS in front of the container.
SECURE_SSL_REDIRECT=false          # prod.py already trusts X-Forwarded-Proto
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend   # staging: no real mail
IP_HASH_SALT=                  # generate
```

`SECURE_SSL_REDIRECT=false` matters: Railway's edge already redirects to HTTPS
and forwards plain HTTP to the container, so a redirect inside the container
loops.

## Media files

Railway's filesystem is ephemeral — uploaded PDFs vanish on redeploy. For
staging that is acceptable with demo data (`seed_demo` regenerates the galleys).
For anything real, point `django-storages` at an S3-compatible bucket with the
`S3_*` variables in `.env.example`, or use a VPS with a disk.

## First start

After the first successful deploy, open a shell on the `web` service
(*Deployments → ⋯ → Shell*) and load the demonstration content:

```bash
python manage.py seed_demo
```

Then sign in with `eic@algorithm-journal.uz` / `Algorithm2026!`. Editorial
accounts must enrol a TOTP app on first sign-in — that is the mandatory policy,
not a fault.

## Checking a deploy

```bash
curl -sI https://algorithmjournal-production.up.railway.app/healthz/ | head -1
curl -s  https://algorithmjournal-production.up.railway.app/oai/?verb=Identify | head -5
```

And the load test, from any machine:

```bash
python scripts/loadtest.py --base https://algorithmjournal-production.up.railway.app --users 50 --seconds 30
```

Railway's smallest plans give the container about one vCPU, so expect a fraction
of what a 4-vCPU VPS sustains; the point of running it there is to catch
errors, not to size production.
