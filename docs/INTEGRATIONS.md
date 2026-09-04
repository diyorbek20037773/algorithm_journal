# Integrations — what to obtain, how, and what happens until you do

**ALGORITHM: Review of Economic Research (ARER)**

Every integration in this document is optional to *run* the platform and
mandatory to be *taken seriously* as a scholarly journal. Each section says
what the service is, what it costs, how to get the credentials, which
environment variables to set, and exactly what the platform does while the
credentials are missing.

---

## 1. Crossref — DOI registration

**What it is.** The registration agency that mints DOIs and links citations.
Without it, articles have no persistent identifier and no serious database will
index the journal.

**Cost (2026 figures, confirm at signup).** Annual membership from **USD 275**
for a publisher with revenue under USD 1 million, plus **USD 1 per current-year
DOI** (back-file DOIs are cheaper). Similarity Check is an optional add-on at
about USD 20 per year plus per-document fees.

**How to get it.**

1. Apply for membership at <https://www.crossref.org/membership/>. You will need
   the journal's title, ISSN (apply for the e-ISSN first, §7), the publisher's
   legal name and address, and a bank account for the invoice.
2. Crossref assigns a **DOI prefix** of the form `10.71234` and creates a
   **deposit account** (a user name and password, distinct from your Crossref
   web login).
3. Test first against the sandbox at `https://test.crossref.org`.

**Configure.**

```ini
DOI_PREFIX=10.71234
CROSSREF_USER=arer.deposit
CROSSREF_PASSWORD=…
CROSSREF_DEPOSITOR_NAME=ARER Editorial Office
CROSSREF_DEPOSITOR_EMAIL=editor@algorithm-journal.uz
CROSSREF_REGISTRANT=ALGORITHM Review of Economic Research
CROSSREF_POLITE_MAILTO=editor@algorithm-journal.uz
CROSSREF_TEST=True     # switch to False after a successful test deposit
```

**Verify.**

```bash
python manage.py crossref_validate --all          # XML must validate
python manage.py crossref_deposit --article 1     # goes to the sandbox
python manage.py crossref_status                  # poll the outcome
```

**Until it is set.** DOIs are still reserved locally in the documented form
`10.xxxxx/arer.{year}.{article-id}` and displayed on the article page; deposit
batches are created, the XML is generated and validated against the bundled
5.4.0 schema, and each batch stays in status `pending` with the message
"Deposit not attempted: credentials are not set" visible in the production
dashboard. Nothing is lost: when the credentials arrive, run
`python manage.py crossref_deposit --issue <id>` for each published issue.

**Switching from test to production.** Set `CROSSREF_TEST=False`, restart, and
re-deposit. Test-system DOIs never resolve publicly; that is expected.

---

## 2. ORCID — author identifiers

**What it is.** A persistent identifier for researchers. Crossref, DOAJ and
Scopus all expect it, and it is what makes author pages reliable.

**Cost.** The **Public API is free**. The Member API (which can write to a
researcher's record) requires membership and is out of scope for v1.

**How to get it.**

1. Sign in at <https://orcid.org/> with an institutional account.
2. Open **Developer tools** and register a public API client.
3. Set the redirect URI to
   `https://algorithm-journal.uz/accounts/orcid/login/callback/`.
4. You receive a **Client ID** (`APP-XXXXXXXXXXXXXXXX`) and a **Client secret**.

Register the sandbox client separately at <https://sandbox.orcid.org/> while
testing.

**Configure.**

```ini
ORCID_BASE=production          # or: sandbox
ORCID_CLIENT_ID=APP-XXXXXXXXXXXXXXXX
ORCID_CLIENT_SECRET=…
```

**Until it is set.** The "Sign in with ORCID" button appears but the OAuth flow
fails at ORCID's end. Authors can still type their ORCID iD by hand in the
submission wizard and in their profile — it is validated for format, deposited
with Crossref and shown on the article page, but flagged as **not
authenticated** in the Crossref deposit (`authenticated="false"`), which is the
honest and correct value.

---

## 3. E-mail — Resend (or any SMTP provider)

**What it is.** Transactional e-mail: verification, submission receipts,
reviewer invitations, decisions, proofs, publication notices.

**Cost.** Resend's free tier covers 3,000 e-mails per month and 100 per day,
which is comfortably more than a monthly journal needs.

**How to get it.**

1. Create an account at <https://resend.com/>.
2. Add the domain `algorithm-journal.uz` and publish the DNS records it shows:
   a **DKIM** `TXT`/`CNAME` record and an **SPF** entry
   (`v=spf1 include:_spf.resend.com ~all`). Add a DMARC record as well:
   `_dmarc TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@algorithm-journal.uz"`.
3. Wait for the domain to show **Verified**, then create an API key.

**Configure.**

```ini
RESEND_API_KEY=re_…
DEFAULT_FROM_EMAIL=editor@algorithm-journal.uz
SERVER_EMAIL=server@algorithm-journal.uz
```

Or, with plain SMTP instead:

```ini
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=…
EMAIL_HOST_PASSWORD=…
```

**Until it is set.** In development every message goes to **Mailpit**
(<http://localhost:8025>) and nothing leaves the machine. In production without
a key, Django falls back to the console backend and messages are written to the
container log — visible with `docker compose logs web`, but **not delivered**.
Authors would not receive verification links, so set this before opening
submissions.

**Verify.** Register a test account and confirm the verification e-mail arrives
and does not land in spam. Check Resend's dashboard for the SPF/DKIM verdict.

---

## 4. Similarity Check (iThenticate)

**What it is.** Crossref's plagiarism-detection service, resold from Turnitin.

**Cost.** About USD 20 per year for the service plus roughly USD 0.75 per
document checked; available only to Crossref members who deposit full-text
links (which this platform already does — see the `crawler-based` collection in
the deposit XML).

**How to get it.** Apply through your Crossref membership dashboard; Turnitin
then provisions an iThenticate account and API credentials.

**Configure.**

```ini
PLAGIARISM_PROVIDER=ithenticate
ITHENTICATE_URL=https://…turnitin.com
ITHENTICATE_API_KEY=…
```

**Until it is set.** `PLAGIARISM_PROVIDER=manual` (the default) is fully
functional: the editor runs the check in whatever tool the institution has,
uploads the report PDF and enters the percentage on the submission's screening
tab. The workflow refuses to send a manuscript to review until a result exists
and is within the threshold, exactly as with the automated provider. The
`IThenticateProvider` class is implemented against the v2 API but raises
`NotConfigured` and falls back to manual until both variables are set — no live
call is ever made by accident.

---

## 5. CLOCKSS / Portico — digital preservation

**What it is.** Dark archives that keep the journal readable if it ceases to
exist. DOAJ awards its Seal partly on this, and Scopus asks about it.

**Cost.** CLOCKSS charges publishers on a sliding scale starting around
USD 275 per year for small publishers; Portico's fee is similar. Some national
consortia cover the cost.

**How to get it.** Apply at <https://clockss.org/> or
<https://www.portico.org/>. Both ask for: the ISSN, the number of articles per
year, the harvest method, and a technical contact. Point them at:

* the LOCKSS manifests: `https://algorithm-journal.uz/lockss/`
* the OAI-PMH endpoint: `https://algorithm-journal.uz/oai/?verb=Identify`
* export bundles, one per issue, produced by
  `python manage.py export_issue_bundle <issue-id>`

**Until it is set.** The manifests, the permission statements, the sitemaps and
the export bundles all exist and are correct — the archives simply are not
harvesting yet. Keep one export bundle per issue off-site in the meantime; that
is the interim preservation copy.

---

## 6. DOAJ — Directory of Open Access Journals

**What it is.** The reference index of trustworthy open-access journals.
Inclusion is a prerequisite for most further indexing.

**Cost.** Free.

**When to apply.** After **12 months** of continuous publication with at least
five research articles. Applying too early wastes the six-month re-application
embargo.

**Checklist mapped to this platform.**

| DOAJ requirement | Where it is satisfied |
|---|---|
| ISSN registered and confirmed | Site settings → `eissn` |
| Journal title matches the ISSN record | Site settings → `journal_name` |
| Publisher name and country | Site settings → `publisher_name`, `publisher_address` |
| At least one editor with public affiliation | `/about/editorial-board/` |
| Peer-review type stated | `/about/peer-review/` (double-blind) |
| Editorial board with affiliations | `/about/editorial-board/` |
| Aims and scope | `/about/aims-and-scope/` |
| Author guidelines | `/for-authors/guidelines/` |
| APC information, even when zero | `/about/fees/` — states "no charges" explicitly |
| Licence terms, machine readable | CC BY 4.0, on every article and in the Crossref deposit |
| Copyright retained by authors | `/about/open-access/` |
| Deposit/archiving policy | `/about/archiving/` |
| Plagiarism policy | `/about/publication-ethics/` |
| Publication ethics statement (COPE) | `/about/publication-ethics/` |
| Persistent article identifiers | DOI on every article |
| Full-text URLs and metadata for harvesting | `/api/v1/doaj-export/`, OAI-PMH |
| Article-level metadata upload | `/api/v1/doaj-export/` produces DOAJ-shaped JSON |

**Apply at** <https://doaj.org/apply/>. Expect two to six months.

---

## 7. e-ISSN

Apply through the **ISSN National Centre of Uzbekistan** (the national library),
or through the ISSN International Centre if no national centre applies. You will
need the journal title, the URL, the publisher, the frequency and the first
issue. It is free or nominally priced and usually takes a few weeks.

Set it in **Admin → Site settings → e-ISSN**. Until then the site prints
"e-ISSN: pending" rather than inventing a number, and the Crossref deposit omits
the ISSN element (the deposit still validates).

---

## 8. Google Scholar

**Cost.** Free; there is no application form. Scholar crawls sites that meet its
technical requirements, which this platform already satisfies:

* Highwire Press `citation_*` meta tags on every article page;
* a stable, language-neutral `citation_pdf_url` (`/article/<id>/pdf/`);
* text-based PDFs (not scanned images);
* every article reachable from the home page in at most three clicks;
* `robots.txt` allowing all agents, plus complete XML sitemaps;
* one canonical URL per article with `hreflang` alternates.

**Troubleshooting.** If articles do not appear within about eight weeks:

1. Check the tags: `curl -s <article-url> | grep citation_`.
2. Confirm the PDF is text: `pdftotext` should return the article text.
3. Confirm `robots.txt` does not block `/article/`.
4. Confirm the sitemap is reachable and lists the articles.
5. Use the inclusion form at
   <https://scholar.google.com/intl/en/scholar/inclusion.html> only after the
   above are verified.

---

## 9. Scopus (CSAB)

**Cost.** Free to apply; review takes six to twelve months, and rejection
carries a two-year embargo, so apply only when ready.

**When to apply.** After **at least two years** of continuous publication with a
citation record. Minimum expectations: peer review described publicly, English
abstracts and English references for all articles, international editorial board
and author base, punctual publication, and an ISSN.

**Checklist mapped to this platform.**

| CSAB criterion | Where it is satisfied |
|---|---|
| Publicly available peer-review policy | `/about/peer-review/` |
| Diversity of editors, geographic | `/about/editorial-board/` (replace demo entries first) |
| Diversity of authors, geographic | `/statistics/` shows author countries |
| Abstracts in English | mandatory, enforced in the wizard |
| References in Roman script | required by the author guidelines and enforced at screening |
| Article titles and abstracts in English | mandatory |
| Journal published on schedule | `/issues/` shows an unbroken monthly record |
| Online availability, English home page | the whole site is available in English |
| Publication ethics statement | `/about/publication-ethics/` |
| Content is academically relevant | editorial responsibility |

Apply at <https://suggestor.step.scopus.com/>.

---

## 10. Matomo — analytics (optional)

Self-hosted, cookie-less, and the only analytics this platform supports; Google
Analytics is excluded by policy.

```bash
docker compose -f docker-compose.prod.yml --profile analytics up -d matomo matomo-db
```

Complete the Matomo installer, then set `MATOMO_URL` (with a trailing slash) and
`MATOMO_SITE_ID` in `.env` and restart `web`. The tracking snippet is injected
only when both are set. Article view and download counts are collected by the
platform itself regardless, with salted-hash identifiers and COUNTER-style bot
filtering, so analytics is genuinely optional.

---

## 11. S3-compatible storage — off-site backups (strongly recommended)

Any S3-compatible provider works. Create a bucket, a scoped access key, and a
lifecycle rule that expires objects after 35 days.

```ini
BACKUP_S3_TARGET=s3://arer-backups/prod
AWS_ACCESS_KEY_ID=…
AWS_SECRET_ACCESS_KEY=…
AWS_S3_ENDPOINT_URL=https://…        # for non-AWS providers
```

Until it is set, backups are written only to the server itself — which does not
protect against losing the server. See `docs/BACKUP_RESTORE.md`.

---

## 12. Summary — what to obtain first

| Order | Item | Blocking? |
|---|---|---|
| 1 | Domain and VPS | yes — nothing runs without them |
| 2 | e-ISSN | yes for Crossref and DOAJ |
| 3 | E-mail (Resend + SPF/DKIM) | yes before opening submissions |
| 4 | Crossref membership and prefix | yes before the first publication |
| 5 | ORCID public API keys | no, but expected by indexers |
| 6 | Off-site backup bucket | no, but the first real risk if skipped |
| 7 | CLOCKSS or Portico | no, needed for the DOAJ Seal |
| 8 | Similarity Check | no, the manual provider is sufficient |
| 9 | DOAJ | after 12 months |
| 10 | Scopus | after 24 months |
