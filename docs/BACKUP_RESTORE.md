# Backup and restore / Zaxira nusxa va tiklash

**ALGORITHM: Review of Economic Research (ARER)**

A backup that has never been restored is not a backup. This document describes
what is backed up, how, where the copies live, and — most importantly — how a
restore is performed and verified.

> **Oʻzbekcha.** Hech qachon tiklanmagan zaxira nusxa — zaxira emas. Bu hujjatda
> nima, qanday va qayerda saqlanishi hamda tiklash tartibi tavsiflangan.

---

## 1. What is backed up

| Data | Where it lives | In the backup |
|---|---|---|
| Database (users, submissions, reviews, articles, audit log, settings) | PostgreSQL volume `pgdata` | `arer-db-<stamp>.dump` (custom format, compressed) |
| Uploaded files (manuscripts, galleys, similarity reports, logos) | volume `media` | `arer-media-<stamp>.tar.gz` |
| Checksums of both | — | `arer-<stamp>.sha256` |
| Configuration | `.env` on the server | **not** in the backup — keep a copy in your password manager |
| Code | GitHub | not backed up separately |

Redis holds only cache and Celery queues and is deliberately not backed up:
losing it costs a cache warm-up, nothing else.

---

## 2. Schedule and retention

* The `backup` service in `docker-compose.prod.yml` runs `scripts/backup.sh`
  every 24 hours.
* Archives are kept for **`BACKUP_RETENTION_DAYS`** days (default 30) in the
  `backups` volume.
* When `BACKUP_S3_TARGET` is set, every archive is also copied off-site with
  `rclone` or the AWS CLI. Off-site copies are what survive the loss of the
  server; configure them.

Manual backup at any time:

```bash
cd /srv/arer
docker compose -f docker-compose.prod.yml exec backup sh /scripts/backup.sh
```

Or, outside Docker:

```bash
BACKUP_DIR=/mnt/backups MEDIA_DIR=/srv/arer/media bash scripts/backup.sh
```

---

## 3. Restoring

> Restoring **overwrites** the target database. Never restore straight into a
> live installation you have not backed up first.

### 3.1 Into a scratch copy (always do this first)

```bash
cd /srv/arer
docker compose -f docker-compose.prod.yml exec db \
  psql -U arer -d postgres -c "CREATE DATABASE arer_check OWNER arer;"

docker compose -f docker-compose.prod.yml exec -e PGDATABASE=arer_check -e FORCE=1 \
  backup sh /scripts/restore.sh /backups/arer-db-<stamp>.dump

docker compose -f docker-compose.prod.yml exec db \
  psql -U arer -d arer_check -c "SELECT count(*) FROM journal_article;"
```

If the row counts look right, proceed. Drop the scratch database afterwards:

```bash
docker compose -f docker-compose.prod.yml exec db \
  psql -U arer -d postgres -c "DROP DATABASE arer_check;"
```

### 3.2 Into the live database

```bash
cd /srv/arer
docker compose -f docker-compose.prod.yml stop web worker beat

docker compose -f docker-compose.prod.yml exec -e FORCE=1 -e RESTORE_MEDIA=1 \
  backup sh /scripts/restore.sh /backups/arer-db-<stamp>.dump

docker compose -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml start web worker beat
curl -s https://algorithm-journal.uz/healthz/
```

`scripts/restore.sh` refuses to run against a non-empty database unless
`FORCE=1` is set — that guard is deliberate.

### 3.3 Restoring only the media files

```bash
tar -xzf backups/arer-media-<stamp>.tar.gz -C /srv/arer/
```

---

## 4. Verification

Every restore must be verified, not assumed:

```bash
# 1. The row counts match the source
psql -c "SELECT count(*) FROM journal_article;"
psql -c "SELECT count(*) FROM submissions_submission;"
psql -c "SELECT count(*) FROM accounts_user;"

# 2. The application starts and reports healthy
curl -s https://algorithm-journal.uz/healthz/

# 3. A published article resolves, with its PDF
curl -sI https://algorithm-journal.uz/article/1/pdf/ | head -1

# 4. Metadata completeness still passes
docker compose -f docker-compose.prod.yml run --rm web python manage.py check_metadata
```

CI runs the same drill on every push: `scripts/ci_backup_restore.sh` seeds a
database, backs it up, restores into a fresh one and compares the row counts. If
that job fails, the backup path is broken — fix it before anything else.

---

## 5. Disaster recovery

Complete loss of the server, with off-site backups available:

1. Provision a new VPS and follow `docs/DEPLOYMENT.md` sections 2–4.
2. Restore `.env` from your password manager.
3. Fetch the newest archives from off-site storage into `backups/`.
4. Start only the database: `docker compose -f docker-compose.prod.yml up -d db`.
5. Restore as in §3.2, including `RESTORE_MEDIA=1`.
6. Run `migrate`, `compilemessages`, `collectstatic`.
7. Start the full stack and verify as in §4.
8. Point DNS at the new server and wait for Caddy to issue the certificate.

Recovery-point objective: 24 hours (the nightly backup).
Recovery-time objective: about one hour with off-site archives at hand.

> **Oʻzbekcha.** Server butunlay yoʻqolsa: yangi VPS, `.env` ni tiklash, tashqi
> ombordan zaxira nusxalarni olish, bazani tiklash, `migrate` va tekshiruv.
> RPO — 24 soat, RTO — taxminan bir soat.

---

## 6. What backups do not replace

Backups protect against accident and failure. They are **not** digital
preservation: an archive in your bucket does not keep the scholarly record
available if the journal ceases to operate. That is the job of CLOCKSS/Portico,
the LOCKSS manifests and the per-issue export bundles described in
`/en/about/archiving/` and produced by:

```bash
docker compose -f docker-compose.prod.yml run --rm web \
  python manage.py export_issue_bundle <issue-id>
```

Keep one export bundle per issue outside the server, permanently.
