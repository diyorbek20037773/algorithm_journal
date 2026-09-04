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
