# Deployment guide / Joylashtirish qoʻllanmasi

**ALGORITHM: Review of Economic Research (ARER)**

English first, Uzbek (Latin) after each section. — Avval inglizcha, keyin har bir
boʻlim uchun oʻzbekcha (lotin).

---

## 1. What you need

| Item | Recommended | Note |
|---|---|---|
| Server | Ubuntu 24.04 LTS VPS in Uzbekistan | 4 vCPU, 8 GB RAM, 100 GB NVMe |
| Domain | `algorithm-journal.uz` | A/AAAA records pointing at the server |
| Software on the server | Docker Engine 26+ and the Compose plugin | nothing else is required |
| Ports open | 80/tcp, 443/tcp, 443/udp | Caddy needs 80 to issue certificates |
| E-mail | Resend API key (or SMTP) | SPF and DKIM on the domain |
| Backups | S3-compatible bucket | off-site, 30-day retention |

Personal data (accounts, reviewers, manuscripts) must stay on the server in
Uzbekistan; only public article metadata is distributed abroad, to Crossref and
the indexing services (SPEC D20).

> **Oʻzbekcha.** Sizga Oʻzbekistondagi Ubuntu 24.04 VPS (4 vCPU / 8 GB / 100 GB),
> domen, Docker Engine 26+ va Compose plagini, 80/443 portlari, Resend (yoki
> SMTP) kaliti hamda tashqi zaxira uchun S3 bucket kerak. Shaxsiy maʼlumotlar
> Oʻzbekistondagi serverda qoladi.

---

## 2. Prepare the server

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl git ufw

# Docker Engine + Compose plugin
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"      # log out and back in afterwards

# Firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp
sudo ufw enable

# Unattended security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

Harden SSH: disable password authentication and root login in
`/etc/ssh/sshd_config` (`PasswordAuthentication no`, `PermitRootLogin no`), then
`sudo systemctl restart ssh`.

> **Oʻzbekcha.** Serverni yangilang, Docker va ufw oʻrnating, 80/443 portlarini
> oching, SSH da parol bilan kirishni oʻchiring.

---

## 3. DNS

| Record | Name | Value |
|---|---|---|
| A | `algorithm-journal.uz` | server IPv4 |
| AAAA | `algorithm-journal.uz` | server IPv6 (if available) |
| A | `www` | server IPv4 |
| TXT | `@` | SPF, e.g. `v=spf1 include:_spf.resend.com ~all` |
| TXT / CNAME | as Resend instructs | DKIM |
| TXT | `_dmarc` | `v=DMARC1; p=quarantine; rua=mailto:dmarc@algorithm-journal.uz` |

Wait until `dig +short algorithm-journal.uz` returns the server address before
starting Caddy: certificate issuance fails otherwise.

---

## 4. Get the code and configure it

```bash
sudo mkdir -p /srv && cd /srv
git clone https://github.com/diyorbek20037773/algorithm_journal.git arer
cd arer
cp .env.example .env
```

Edit `.env`. The values that **must** change before going live:

```ini
DJANGO_SECRET_KEY=<output of: make secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=algorithm-journal.uz,www.algorithm-journal.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://algorithm-journal.uz,https://www.algorithm-journal.uz
SITE_DOMAIN=algorithm-journal.uz
SITE_PROTOCOL=https
ACME_EMAIL=editor@algorithm-journal.uz

POSTGRES_PASSWORD=<a long random password>

SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
IP_HASH_SALT=<a long random string>

RESEND_API_KEY=<from resend.com>
DEFAULT_FROM_EMAIL=editor@algorithm-journal.uz

DOI_PREFIX=<your Crossref prefix, e.g. 10.71234>
CROSSREF_USER=<Crossref deposit user>
CROSSREF_PASSWORD=<Crossref deposit password>
CROSSREF_TEST=False          # keep True until the first test deposit succeeds

ORCID_BASE=production
ORCID_CLIENT_ID=<from orcid.org/developer-tools>
ORCID_CLIENT_SECRET=<same>

BACKUP_S3_TARGET=s3://arer-backups/prod
```

`docs/INTEGRATIONS.md` explains where each credential comes from and what the
platform does until it is set.

> **Oʻzbekcha.** Kodni klonlang, `.env` faylini toʻldiring: SECRET_KEY, domen,
> Postgres paroli, HTTPS sozlamalari, Resend kaliti, Crossref va ORCID
> maʼlumotlari. Har bir qiymat manbasi `docs/INTEGRATIONS.md` da.

---

## 5. First start

```bash
cd /srv/arer
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d db redis

docker compose -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml run --rm web python manage.py compilemessages --ignore=.venv
docker compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput --ignore=src

# Journal configuration, policy pages, sections, JEL codes and e-mail templates.
# Use --minimal on a real installation: it loads the configuration and the
# policy pages but no demonstration articles or submissions.
docker compose -f docker-compose.prod.yml run --rm web python manage.py seed_demo --minimal

# Your own administrator account
docker compose -f docker-compose.prod.yml run --rm web python manage.py createsuperuser

docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

Then open `https://algorithm-journal.uz/`. Caddy obtains the certificate on the
first request; give it up to a minute.

Check the health endpoint:

```bash
curl -s https://algorithm-journal.uz/healthz/
# {"status": "ok", "database": "ok", "cache": "ok"}
```

> **Oʻzbekcha.** `build` → `migrate` → `compilemessages` → `collectstatic` →
> `seed_demo --minimal` → `createsuperuser` → `up -d`. Keyin sayt HTTPS orqali
> ochiladi; sertifikatni Caddy avtomatik oladi.

---

## 6. After the first start

1. **Sign in** at `/admin/` and enrol your TOTP device — two-factor
   authentication is mandatory for editorial accounts.
2. **Site settings** (`/admin/core/sitesettings/`): e-ISSN, registration
   certificate number and date, founder and publisher name and address, contact
   details, DOI prefix, logo.
3. **Editorial board** (`/admin/journal/editorialboardmember/`): replace every
   entry marked "DEMO — replace" with real members. The board page shows a
   warning banner while any demo entry remains.
4. **Policy pages** (`/admin/core/page/`): proofread the Uzbek, Uzbek Cyrillic
   and Russian versions. Each seeded page is flagged `needs_editorial_review`;
   clear the flag as you approve it.
5. **Sections** (`/admin/journal/section/`): assign section editors.
6. **E-mail**: send a test message from the admin, then check Resend's dashboard
   for delivery and the SPF/DKIM verdict.
7. **Crossref**: with `CROSSREF_TEST=True`, run
   `manage.py crossref_deposit --article <id>` and confirm the test deposit
   succeeds before switching to `False`.

> **Oʻzbekcha.** Kirgach 2FA ni yoqing, sayt sozlamalarini toʻldiring, DEMO
> hayʼat aʼzolarini almashtiring, siyosat sahifalarining tarjimasini tekshiring,
> boʻlim muharrirlarini tayinlang, pochtani sinang, Crossref test depozitini
> oʻtkazing.

---

## 7. Updating

```bash
cd /srv/arer
bash scripts/deploy.sh
```

The script pulls the code, takes a database backup, rebuilds the images, applies
migrations, recompiles translations, collects static files, restarts the stack
and waits for the health check.

> **Oʻzbekcha.** Yangilash uchun `bash scripts/deploy.sh` — u zaxira nusxa
> oladi, migratsiyalarni qoʻllaydi va tizimni qayta ishga tushiradi.

---

## 8. Rolling back

```bash
cd /srv/arer
git log --oneline -n 10             # find the previous commit
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# If a migration must also be undone:
docker compose -f docker-compose.prod.yml run --rm web \
  python manage.py migrate <app> <previous_migration_number>

# If the data must be restored:
FORCE=1 RESTORE_MEDIA=1 bash scripts/restore.sh backups/arer-db-<stamp>.dump
```

Always restore into a copy first when you are unsure — see
`docs/BACKUP_RESTORE.md`.

---

## 9. Backups

The `backup` service in `docker-compose.prod.yml` runs `scripts/backup.sh` every
24 hours: a custom-format `pg_dump`, a gzipped media archive, SHA-256 checksums,
30-day retention and an optional off-site copy to `BACKUP_S3_TARGET`.

Verify the schedule and restore procedure monthly:

```bash
docker compose -f docker-compose.prod.yml exec backup sh /scripts/backup.sh
ls -lh backups/ | tail
```

---

## 10. Monitoring

* **Health endpoint** — `https://algorithm-journal.uz/healthz/` returns JSON and
  HTTP 503 when the database or cache is unreachable. Point UptimeRobot, Better
  Stack or Healthchecks.io at it with a five-minute interval and alerting to the
  editorial e-mail.
* **Certificate expiry** — Caddy renews automatically; monitor the domain's TLS
  expiry as a safety net.
* **Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f web
  docker compose -f docker-compose.prod.yml logs -f worker
  docker compose -f docker-compose.prod.yml exec caddy cat /data/access.log | tail
  ```
* **Disk** — `df -h` and `docker system df`; prune old images with
  `docker image prune -a` after a successful deployment.
* **Celery** — `docker compose -f docker-compose.prod.yml exec worker celery -A config inspect active`.

---

## 11. Analytics (optional)

```bash
docker compose -f docker-compose.prod.yml --profile analytics up -d matomo matomo-db
```

Then set `MATOMO_URL` and `MATOMO_SITE_ID` in `.env` and restart `web`. The
tracking snippet is injected only when both are set, is configured without
cookies and honours "Do Not Track". Google Analytics is not used, by policy.

---

## 12. Common problems

| Symptom | Cause | Fix |
|---|---|---|
| Certificate is not issued | DNS not propagated, or port 80 blocked | `dig +short <domain>`, `sudo ufw status`; check `docker compose logs caddy` |
| `DisallowedHost` in the logs | `DJANGO_ALLOWED_HOSTS` missing the domain | add it and restart `web` |
| CSRF failures on forms | `DJANGO_CSRF_TRUSTED_ORIGINS` missing `https://` | add the full origin |
| Static files missing | `collectstatic` not run after a change | rerun step 5 or `bash scripts/deploy.sh` |
| `/uz-cyrl/` pages fall back to English | `compilemessages` not run | rerun it; the `.mo` files are not committed |
| E-mail not delivered | `RESEND_API_KEY` unset or SPF/DKIM missing | check `docs/INTEGRATIONS.md` |
| Crossref deposit stays `pending` | credentials unset | set `CROSSREF_USER`/`CROSSREF_PASSWORD` |
| Editors cannot reach the dashboard | 2FA not enrolled | complete enrolment at `/dashboard/two-factor/setup/` |
