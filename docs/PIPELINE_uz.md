# Yetkazib berish pipeline'i: Local → CI → CD → Monitoring

Bu hujjat kod dasturchi kompyuteridan Kubernetes klasterigacha qanday yetib
borishini va u yerda qanday kuzatilishini tushuntiradi. Har bir bosqich
repozitoriyda aniq fayl bilan ifodalangan.

```
 Local                  CI (GitHub Actions)                    CD (GitOps)              Monitoring
 ─────                  ───────────────────                    ───────────              ──────────
 git commit ─┐          quality ──┬─> sonarqube ─┐                                      Tracing  : OTel Collector → Jaeger
 make verify │  push    manifests ┴─> image ─────┼─> gitops ──> k8s/overlays/* ──> Argo CD ──> K8s   Logging  : Fluent Bit → Elasticsearch → Kibana
 git push ───┘ ───────> e2e ─────────────────────┘   (tag yangilanadi)                  Audit    : arer-audit-*, k8s-audit-*
```

---

## 1. Mahalliy ish stoli (Local)

| Qadam | Buyruq | Nima tekshiriladi |
|---|---|---|
| commit | `git commit` | `pre-commit` hook: ruff, ruff-format, djlint, `manage.py check`, migratsiyalar, YAML, maxfiy kalit izlash |
| test | `make test` | 440+ pytest testi (Postgres + Redis kerak: `docker compose up -d db redis`) |
| build | `make build` | Prod image CI bilan aynan bir xil yig'iladi (`--target runtime`, dev paketlarsiz) |
| manifest | `make k8s-validate` | `kubectl kustomize` + `kubeconform` barcha overlay'lar uchun |
| hammasi | `make verify` | lint → migratsiya → tarjimalar → test → build → k8s-validate |
| push | `git push` | `pre-push` hook test to'plamini yana ishga tushiradi |

Birinchi marta hook'larni o'rnatish:

```bash
uv sync --extra dev
uv run pre-commit install        # pre-commit va pre-push ikkalasini o'rnatadi
```

## 2. CI — `.github/workflows/ci.yml`

| Job | Vazifa | Qachon |
|---|---|---|
| `quality` | ruff, djlint, tarjimalar, `check --deploy`, migratsiyalar, pytest + coverage, backup/restore mashqi, pip-audit | har push/PR |
| `e2e` | Playwright: topshirishdan nashrgacha | har push/PR |
| `manifests` | kustomize render + kubeconform (Argo CD CRD'lari ham) | har push/PR |
| `sonarqube` | Kod sifati, xavfsizlik zaifliklari, coverage; **Quality Gate** o'tmasa pipeline to'xtaydi | `SONAR_TOKEN` bo'lsa |
| `image` | Docker image yig'ish; `main` va `v*` teglarda registry'ga yuklash | PR'da faqat build |
| `gitops` | Image tegini overlay'ga yozib, `[skip ci]` commit qiladi | faqat push (main yoki `v*`) |

**Image teglari:** `main` → `sha-<12 belgi>` (+ `latest`); `v1.2.0` teg → `1.2.0`.

### Sozlanadigan sirlar va o'zgaruvchilar (GitHub → Settings → Secrets and variables → Actions)

| Nomi | Turi | Kerakmi | Izoh |
|---|---|---|---|
| `SONAR_TOKEN` | secret | SonarQube uchun | Yo'q bo'lsa job "skipped" deb ogohlantiradi, pipeline davom etadi |
| `SONAR_HOST_URL` | variable | self-hosted SonarQube bo'lsa | Standart: `https://sonarcloud.io`. Self-hosted bo'lsa `sonar-project.properties` dan `sonar.organization` qatorini o'chiring |
| `IMAGE_REGISTRY` | variable | ixtiyoriy | Standart `ghcr.io`. Masalan ichki registry: `10.0.1.5:5000` yoki `registry.example.uz` |
| `IMAGE_NAME` | variable | ixtiyoriy | Standart: `diyorbek20037773/algorithm_journal` |
| `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` | secret | GHCR dan boshqa registry uchun | GHCR uchun `GITHUB_TOKEN` avtomatik ishlatiladi |

> **Diqqat:** registry nomini o'zgartirsangiz, `k8s/overlays/*/kustomization.yaml`
> dagi `newName` ham birinchi `gitops` job'da avtomatik yangilanadi. Klaster
> ichki registry'dan tortishi uchun `imagePullSecrets` yoki node darajasida
> `registries.yaml` (k3s) sozlang.

`main` branch himoyalangan bo'lsa, `github-actions[bot]` ga push ruxsatini bering
(yoki gitops job uchun deploy key/PAT ishlating) — aks holda `gitops` job xato beradi.

## 3. CD — Argo CD + Kubernetes

### Repozitoriy tuzilmasi

```
k8s/
├── base/                    # web (+media nginx sidecar), worker, beat, migrate Job, ingress, HPA, PDB, NetworkPolicy, ConfigMap
├── components/data/         # PostgreSQL 16 StatefulSet, Redis 7, kunlik pg_dump CronJob
├── overlays/staging/        # arer-staging namespace, demo ma'lumot, 100% trace
├── overlays/production/     # arer namespace, algorithm-journal.uz
├── monitoring/              # OTel Collector, Jaeger, Elasticsearch, Kibana, Fluent Bit, retention
├── cluster-audit/           # kube-apiserver audit policy
├── argocd/root.yaml         # app-of-apps
├── argocd/apps/             # AppProject, staging, production, monitoring Application'lari
└── secret.example.yaml      # Secret shabloni (haqiqiy qiymat Git'ga TUSHMAYDI)
```

### Birinchi o'rnatish (VPS, O'zbekiston — TZ §3.4)

```bash
# 1. k3s (bitta node) — Traefik o'rniga ingress-nginx ishlatamiz
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable=traefik" sh -

# 2. ingress-nginx, cert-manager, Argo CD
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/cloud/deploy.yaml
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Let's Encrypt ClusterIssuer'lar (letsencrypt va letsencrypt-staging) — docs/DEPLOYMENT.md

# 4. Namespace'lar va sirlar (qiymatlarni o'zingiz yarating!)
kubectl create namespace arer
kubectl -n arer create secret generic arer-secrets \
  --from-literal=DJANGO_SECRET_KEY="$(python3 -c 'import secrets;print(secrets.token_urlsafe(64))')" \
  --from-literal=POSTGRES_PASSWORD="KUCHLI-PAROL" \
  --from-literal=DATABASE_URL="postgres://arer:KUCHLI-PAROL@arer-postgres:5432/arer" \
  --from-literal=IP_HASH_SALT="$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')"
# staging uchun xuddi shu: -n arer-staging

# 5. GitOps'ni yoqish — shundan keyin klaster Git bilan o'zi sinxronlanadi
kubectl apply -n argocd -f k8s/argocd/root.yaml
```

Namespace'ni overlay ham yaratadi; sirni oldinroq yaratish uchun 4-qadamda qo'lda
ochdik. Sirlarni Git'da shifrlangan holda saqlash kerak bo'lsa — Sealed Secrets
yoki SOPS + External Secrets.

### Deploy qanday ishlaydi

1. `main` ga push → CI yashil → image `sha-…` registry'da → `gitops` job
   `k8s/overlays/staging/kustomization.yaml` dagi `newTag` ni yangilaydi.
2. Argo CD o'zgarishni ko'radi va sinxronlaydi, to'lqinlar tartibida:
   **-2** Postgres/Redis → **-1** `arer-migrate` Job (migratsiya + birinchi kontent)
   → **0** web/worker/beat (RollingUpdate, `maxUnavailable: 0`).
3. Production uchun: `make release VERSION=1.2.0` (yoki `git tag v1.2.0 && git push origin v1.2.0`)
   → `k8s/overlays/production` yangilanadi → Argo CD `arer-production` ni
   ish vaqti oynasida (Du–Ju, 10:00–22:00 Toshkent) sinxronlaydi.

**Orqaga qaytarish (rollback):** overlay commit'ini `git revert` qiling — Argo CD
oldingi image'ga qaytadi. Yoki Argo CD UI → History → Rollback (keyin Git'ni ham
tuzating, aks holda selfHeal qayta yangilaydi).

### Xavfsizlik

- Barcha pod'lar `runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities: drop ALL`,
  `seccompProfile: RuntimeDefault`; ilova namespace'lari Pod Security `restricted`.
- NetworkPolicy: default-deny; web faqat `ingress-nginx` dan; Postgres/Redis faqat ilova pod'laridan.
- ServiceAccount token ilova pod'lariga ulanmaydi.
- Probe'lar: `/livez/` (DB'ga tegmaydi — DB uzilsa pod'lar qayta ishga tushmaydi),
  `/healthz/` (readiness — DB va kesh).

## 4. Monitoring

UI'larga faqat port-forward orqali kiriladi (ochiq Ingress yo'q):

```bash
kubectl -n monitoring port-forward svc/jaeger-query 16686   # http://localhost:16686
kubectl -n monitoring port-forward svc/kibana 5601          # http://localhost:5601
```

### Tracing (Jaeger)

- Ilova OpenTelemetry bilan instrumentlangan: HTTP so'rovlar (Django), SQL (psycopg),
  Redis, tashqi HTTP (Crossref/ORCID — requests), Celery vazifalari.
- `OTEL_EXPORTER_OTLP_ENDPOINT` bo'sh bo'lsa tracing **o'chiq** (overhead yo'q).
- Oqim: ilova → `otel-collector:4318` → Jaeger → Elasticsearch (`jaeger-*`).
- Namuna olish: production 20%, staging 100% (`OTEL_TRACES_SAMPLER_ARG`).
- Mahalliy tekshiruv natijasi: `GET /oai/` bitta trace'da 1 HTTP + 8 SQL + 15 Redis span.

### Logging (EFK)

- `LOG_FORMAT=json` — har qator bitta JSON: `timestamp, level, logger, message,
  service, environment, version, trace_id, span_id`.
- Fluent Bit DaemonSet konteyner loglarini o'qiydi, pod metama'lumotini qo'shadi →
  indeks `arer-logs-YYYY.MM.DD`.
- Kibana'da `trace_id` bo'yicha qidirib, Jaeger'da o'sha so'rovni ochish mumkin.

### Audit

| Manba | Qayerga | Saqlash |
|---|---|---|
| Ilova: login, muvaffaqiyatsiz login, logout, tahririyat qarorlari, nashr, sozlamalar (`AuditLog` jadvali + `arer.audit` logger) | `arer-audit-*` | 365 kun |
| Kubernetes API: kim nimani yaratdi/o'zgartirdi/o'chirdi, `exec`/`port-forward` | `k8s-audit-*` | 365 kun |
| PostgreSQL: ulanishlar va DDL | `arer-logs-*` | 14 kun |
| Argo CD: har bir sinxronlash tarixi | Argo CD UI / `arer-logs-*` | — |

Kubernetes API audit'ni yoqish (control-plane node'da bir marta) —
`k8s/cluster-audit/audit-policy.yaml` boshidagi ko'rsatmaga qarang. Secret va
ConfigMap mazmuni logga **hech qachon** yozilmaydi (faqat metama'lumot).

Indekslarni tozalash: `es-retention` CronJob har kecha (loglar/trace'lar 14 kun, audit 365 kun).

## 5. Tekshiruv natijalari (2026-09-17)

| Tekshiruv | Natija |
|---|---|
| ruff lint + format, djlint | ✅ |
| `makemigrations --check`, tarjimalar to'liqligi | ✅ |
| pytest (e2e'siz) | ✅ hammasi o'tdi |
| `check --deploy` (prod) | ✅ xato yo'q (ogohlantirishlar env orqali boshqariladi) |
| Prod image build | ✅ 1.15 GB → 724 MB (dev paketlar olib tashlandi) |
| `STORAGE_BACKEND=s3` bilan ishga tushish | ✅ (avval `ModuleNotFoundError: storages` edi) |
| kubeconform (staging, production, monitoring, Argo CD) | ✅ 70/70 |
| Fluent Bit `--dry-run`, OTel Collector `validate` | ✅ |
| actionlint (workflow + shellcheck) | ✅ |
| Prod image + Jaeger end-to-end | ✅ ichma-ich trace'lar, JSON loglar |

SonarQube tahlili, registry'ga push va Argo CD sinxronlash haqiqiy tokenlar va
klaster talab qiladi — ular CI'da birinchi `main` push'da ishga tushadi.
