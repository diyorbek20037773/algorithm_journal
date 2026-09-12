# Performance record

SPEC §15.12 asks for query-count tests, static bundle sizes within budget and
"Lighthouse numbers recorded (or documented reason)". This file is that record.

Measured on 2026-09-05 against the seeded demonstration database
(`manage.py seed_demo`), Django 5.2 on Python 3.12, PostgreSQL 16, Redis 7.

## Why there are no Lighthouse scores

Lighthouse ships as a Node package (`npm i -g lighthouse`) or inside Chrome
DevTools. The platform is deliberately **Node-free** — CLAUDE.md §8 forbids a
Node build pipeline, and Tailwind is compiled by the standalone
`django-tailwind-cli` binary — so adding Node purely to score the site would
contradict the constraint the rest of the build is held to.

Instead the two things Lighthouse would have reported are measured directly and
asserted in CI:

* **Accessibility** — axe-core 4.10 over seven representative pages, run by
  `scripts/screenshots.py`, results in `docs/screenshots/accessibility.json`.
  Lighthouse's accessibility category *is* axe-core; this is the same engine
  with a wider rule set than Lighthouse enables by default.
* **Performance** — server query counts, response payload sizes and static
  bundle sizes, asserted in `tests/test_performance.py`. These are the numbers
  the application actually controls; Lighthouse's headline score is dominated by
  network conditions of the machine running it.

To produce Lighthouse numbers anyway, on a machine that has Node:

```bash
docker compose up -d
npx lighthouse http://localhost:8000/en/ --preset=desktop --view
npx lighthouse http://localhost:8000/en/article/1/ --form-factor=mobile --view
```

## Accessibility (axe-core 4.10.2, 1440 px)

| Page | Violations | Serious / critical |
|---|---|---|
| Home | 0 | 0 |
| Issue table of contents | 0 | 0 |
| Article landing | 0 | 0 |
| Search results | 0 | 0 |
| Editorial board | 0 | 0 |
| Submission wizard | 0 | 0 |
| Editor dashboard | 0 | 0 |

Three violation classes were found and fixed during the hardening phase:
`color-contrast` (the tertiary grey and the ORCID mark), `link-in-text-block`
(links distinguished by colour alone) and `heading-order` (search results). See
DECISIONS.md entries 13–15.

## Static bundles

| Asset | Raw | Gzipped | Budget |
|---|---|---|---|
| `static/css/output.css` (Tailwind v4, purged) | 33.4 KB | **7.1 KB** | < 60 KB |
| `static/js/htmx.min.js` | 50.9 KB | 16.0 KB | — |
| `static/js/alpine.min.js` | 44.8 KB | 15.8 KB | — |
| JavaScript total | 95.7 KB | **31.8 KB** | < 60 KB |

No framework runtime, no bundler, no web fonts loaded from a third party.

## Pages: queries and payload

Query counts are the enforced gate — `tests/test_performance.py` fails the build
above 15 queries for home, issue and article (20 for search, which runs the
full-text query plus its facets).

| Page | Queries | Budget | HTML | HTML gzipped |
|---|---|---|---|---|
| Home | 11 | 15 | 34.7 KB | 6.8 KB |
| Article landing | 15 | 15 | 73.1 KB | 14.1 KB |
| Search results | 10 | 20 | 27.5 KB | 5.8 KB |
| Editorial board | 2 | 15 | 24.7 KB | 4.1 KB |
| Statistics | 2 | 15 | 16.8 KB | 3.7 KB |

`test_article_page_does_not_scale_with_authors` adds eight more authors to an
article and asserts the query count does not move, which is what proves the
prefetching rather than the absolute number.

Wall-clock timings are deliberately **not** recorded here. They were taken on a
loaded developer laptop whose Redis and PostgreSQL were contending with an
unrelated Docker build, so the figures say more about that machine than about
the application. Query counts and payload sizes are reproducible anywhere.

## Caching

* Site settings, the navigation and the published-issue list are cached in Redis
  and invalidated on publication (`apps/core/services.py`,
  `apps/journal/signals.py`).
* Every public response carries `Cache-Control` suited to its volatility;
  article pages are safe behind a CDN because the download counter is recorded
  on the language-neutral `/article/<id>/pdf/` route, not on the landing page.
* `ManifestStaticFilesStorage` fingerprints static files in production, so they
  are served with a one-year immutable lifetime.

## Reproducing

```bash
make test                       # includes tests/test_performance.py
make screenshots                # regenerates docs/screenshots/accessibility.json
```


## Load test (TZ §10: 200 concurrent users)

`scripts/loadtest.py` opens N virtual readers against a production-mode
gunicorn and reports throughput, latency percentiles and the error rate. It is
how the 200-user requirement is *checked* rather than asserted, and it gates a
deployment (non-zero exit above the thresholds).

```bash
python scripts/loadtest.py --base https://<host> --users 200 --seconds 60
```

### What it found, 2026-09-12, on the build machine

| Configuration | req/s | errors | p50 | p95 |
|---|---|---|---|---|
| As delivered (3 workers × 2 threads, inline search) | 11.3 | **21.7 %** | 20.2 s | 30.0 s |
| + stored search vector | 29.7 | 0.17 % | 4.1 s | 14.9 s |
| + 9 workers × 4 threads, DB pool, Postgres tuned | 43.5 | **0 %** | 2.6 s | 7.4 s |
| + whole-page cache for anonymous readers | 43.6 | 0 % | 2.3 s | 8.2 s |

The first row is the defect: **search took 8.3 seconds** for a single request.
The inline `SearchVector` joined keywords × authors × references — a Cartesian
product of ~100 000 rows recomputed with `to_tsvector` on every search, on
fourteen articles. Ten percent of readers searching was enough to hold every
worker slot and time out the rest. The document is now stored in
`Article.search_vector` under a GIN index and maintained by signals; a search
is an index lookup and takes ~150 ms whatever the archive's size.

### Why the last two rows are identical — and why 43 req/s is not the answer

A cache hit costs about a millisecond of Python, yet throughput did not move.
Measuring the trivial `/healthz/` endpoint alone explains it:

| users | req/s | p50 |
|---|---|---|
| 10 | 90 | 55 ms |
| 50 | 63 | 514 ms |
| 200 | 52 | 3 738 ms |

An endpoint that does nothing saturates at ~50 req/s and its latency grows
with concurrency. That ceiling is **Docker Desktop for Windows** — host to
WSL2 VM to container port-forward — with the load generator competing for the
same CPUs. The application cannot be measured past it on this machine, in any
configuration.

What the figures above do establish: the timeout failures are gone (21.7 % →
0 %), the one structural defect is fixed, and each request is cheap. The
capacity number itself has to come from the target server. Run the command
above on the VPS before acceptance; a 4-vCPU Linux host with no port-forward
proxy in the path is a different machine from this one.

### What was changed for capacity

* **Stored search vector** with a GIN index (`apps/search/indexing.py`),
  refreshed by signals when an article, author, keyword or reference changes;
  `manage.py rebuild_search_index` repairs it after a bulk import.
* **Gunicorn** sized from the CPU count (2n+1, capped at 12) × 4 threads,
  workers recycled every ~1 000 requests, `/dev/shm` for the heartbeat.
* **psycopg connection pool** (`DB_POOL=true`): a few shared connections per
  worker instead of one pinned per thread.
* **Postgres** limits set explicitly for an 8 GB host: `max_connections=200`,
  `shared_buffers=1GB`, `effective_cache_size=3GB`.
* **Whole-page cache** for anonymous readers (`apps/core/caching.py`), 120 s,
  keyed by language and URL, bypassed for anyone signed in, invalidated by a
  generation counter that every publish and every CMS edit bumps. Article
  views are counted by a beacon the page fires after load, so caching the page
  does not lose the statistic.
