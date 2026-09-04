# Screenshots

Captured with `python scripts/screenshots.py` against the seeded demonstration
database. Regenerate them at any time with `make screenshots`.

## Public pages

Each page is captured in **English** (`-en`) and **Uzbek Cyrillic**
(`-uz-cyrl`), at 1440 px, full page — the Cyrillic set proves the layout
survives the longer strings and the second script.

| File | Page |
|---|---|
| `01-home` | Home |
| `02-issue` | Issue table of contents |
| `03-article` | Article landing page |
| `04-archive` | Archive |
| `05-search` | Search with filters |
| `06-board` | Editorial board |
| `07-policy` | Policy page (publication ethics) |
| `08-for-authors` | Author hub |
| `15-auth` | Sign in |
| `16-statistics` | Public statistics |
| `19-online-first` | Online First |
| `20-jel` | JEL classification browse |
| `21-announcements` | Announcements |
| `22-contact` | Contact |
| `23-aims-and-scope` | Aims & scope |
| `24-peer-review` | Peer review process |
| `25-fees` | Article processing charges |
| `26-checklist` | Pre-submission checklist |

## Editorial system

| File | Screen | Signed in as |
|---|---|---|
| `09-submit-wizard.png` | Submission wizard | author |
| `10-dashboard-editor.png` | Editor dashboard | section editor |
| `10b-queue-in-review.png` | "In review" queue with reviewer status dots | section editor |
| `11-dashboard-submission.png` | Submission detail, reviewers tab | section editor |
| `12-dashboard-reviewer.png` | Reviewer dashboard | reviewer |
| `13-dashboard-author.png` | Author dashboard with status timeline | author |
| `14-production-issue-builder.png` | Issue builder | production editor |
| `17-production-queue.png` | Production queue | production editor |

## Responsive set

`responsive/<page>-<width>.png` for home, issue, article and dashboard at
**360, 768, 1280 and 1920 px** (SPEC §15.13).

## Accessibility

`accessibility.json` holds the axe-core results for the home, issue, article,
search, board, submit and dashboard pages. The target is **zero serious or
critical violations**; the file records what the last run found.
