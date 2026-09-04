# Editor's guide

**ALGORITHM: Review of Economic Research (ARER)**

This guide walks a section editor, the editor-in-chief and the production editor
through the whole editorial process as the system implements it. Screenshots of
every screen are in [`screenshots/`](screenshots/).

---

## 0. Before you start

**Sign in** at `/accounts/login/` with your e-mail address. On your first sign-in
the system will require you to enrol a **TOTP authenticator** — scan the QR code
with Aegis, Google Authenticator, 1Password or similar and enter the six-digit
code. Store the ten recovery codes somewhere safe: they are shown once. Two-factor
authentication is mandatory for every editorial role and cannot be skipped.

Your dashboard is at `/dashboard/`. The left navigation shows only the queues
your role can act on.

---

## 1. The queues

| Queue | What is in it | What you do |
|---|---|---|
| **New** | Submitted, no editor assigned | Assign a handling editor |
| **Screening** | Editor assigned, not yet in review | Check scope, structure, similarity; desk reject or send to review |
| **In review** | Reviewers invited or reviewing | Watch the reviewer chips, remind, invite replacements |
| **Awaiting decision** | Every review is in | Read the reviews, write the decision |
| **Revisions** | Revision requested or resubmitted | Wait, remind, or send the revision back to review |
| **Accepted / in production** | Accepted | Hand over to the production editor |

Reviewer status is shown as coloured dots on the queue rows: grey = invited,
blue = accepted, green = review submitted, red = overdue.

---

## 2. Screening — within seven days

Open the submission and work through the **Summary** tab.

1. **Scope.** Is this economics research of international interest, in one of the
   nine sections? If not, desk reject with a short reason — quickly, so the
   author can submit elsewhere.
2. **Completeness.** Trilingual title, abstract and keywords; 1–5 JEL codes;
   authors with affiliations and countries; a separate title page; an anonymised
   manuscript.
3. **Similarity.** Run your similarity tool, then fill in the **Similarity
   check** box: the percentage and the report PDF. **The system will not let you
   send a manuscript to review without a recorded result**, and refuses outright
   above 20 % unless the editor-in-chief records a written justification.
4. **Anonymity.** Open the manuscript file and confirm it has no author names,
   affiliations or acknowledgements. If it does, return it to the author rather
   than sending it out.

Then use **Actions → Send to review** (which opens round 1) or
**Record a decision → Desk reject**.

---

## 3. Inviting reviewers

From the submission, click **Find reviewers**. The finder ranks candidates by
expertise, JEL overlap, current workload, number of completed reviews and the
average quality rating editors have given them. It excludes the submitting
author and anyone already invited to this round.

* **Invite** next to a candidate sends the templated invitation with one-click
  accept and decline links.
* To invite someone who has no account, use **Invite someone by e-mail** — the
  system creates an inactive account, sends a password-setting link and issues
  the invitation.

Invite **at least two** reviewers. Because some decline, three invitations for
two reviews is normal practice.

**Conflicts of interest.** Do not invite anyone who has co-authored with an
author in the past three years, works at the same institution, or has a
financial interest. The system blocks the obvious cases; the rest is your
judgement.

**Reminders** go out automatically three days before the deadline, on the
deadline and seven days after. The **Remind** button sends one immediately.
If a reviewer is more than a week late and silent, invite a replacement rather
than waiting.

---

## 4. Reading the reviews

The **Reviews** tab shows, for each completed review: the six criterion scores
(1–5), the recommendation, the comments to the authors and the confidential
comments to you.

Read them critically. A review that is only "the paper is good, accept" or
"reject, the topic is not interesting" is not usable; ask the reviewer for
specifics or invite another. Rate each review from 1 to 5 in the **Review
quality** box — the rating is private and feeds the reviewer finder.

If two reviewers disagree substantially, invite a third before deciding.

---

## 5. The decision

Click **Record a decision**. The letter is pre-filled from a template with the
reviewers' comments to the authors merged in; edit it before sending.

| Decision | Use it when | What the system does |
|---|---|---|
| **Accept** | No further changes are needed | Stamps the acceptance date, creates the six production tasks |
| **Minor revision** | Fixable within 30 days | Opens a 30-day revision request |
| **Major revision** | Substantial rework, outcome uncertain | Opens a 60-day revision request |
| **Reject** | Not publishable here | Cancels outstanding invitations |
| **Reject with resubmission encouraged** | Sound question, unusable execution | As reject; say so explicitly in the letter |
| **Desk reject** | Out of scope or below threshold at screening | Immediate, no review |

Write the letter so the author knows exactly what to do. Name the points that
must be addressed and separate them from the optional ones. The decision, the
letter and the notification are recorded in the audit log.

**Target: the first decision within eight weeks of submission.** The dashboard
shows the median for the last twelve months; if it drifts above eight weeks,
the bottleneck is almost always reviewer invitation, not reviewing.

---

## 6. Revisions

The author uploads a revised manuscript and a response to the reviewers; the
submission moves to **Resubmitted**.

* For a **minor revision**, you can usually decide yourself.
* For a **major revision**, send it back to the original reviewers where
  possible — use **Send to review**, which opens round 2. Give re-reviewers 14
  days rather than 21.

---

## 7. Production (production editor)

Open `/production/`. Each accepted manuscript has a six-stage checklist:
copyediting → author proof → typesetting → metadata → DOI → scheduled.

1. **Copyediting.** Upload the copyedited file; move the stage on.
2. **Author proof.** *Send proof to author* e-mails the corresponding author,
   who approves it from their dashboard. Only typographical and factual
   corrections are accepted at this stage.
3. **Typesetting.** Upload the final PDF as a **galley** on the article page.
   Mark it primary — it is what the `citation_pdf_url` points at, so Google
   Scholar depends on it.
4. **Metadata.** The article page shows a red/green completeness checklist. Every
   red required item blocks publication. ORCID is a warning, not a blocker.
5. **DOI.** Click **Reserve the DOI**. The identifier is
   `10.xxxxx/arer.{year}.{article-id}` and is **independent of the issue**, so it
   never changes when the article later joins one.
6. **Publish Online First** as soon as production finishes — do not wait for the
   issue. The PDF is stamped with the running header and footer, the Crossref
   deposit is queued, and the authors are notified.
7. **Schedule into an issue**: choose the issue and enter the page range. The PDF
   is re-stamped with the volume, issue and pages, and a Crossref metadata
   update is queued for the same DOI.

---

## 8. Publishing an issue

Open **Production → the issue → Issue builder**.

1. Set the order and page ranges for every article, then **Save order and pages**.
2. The right-hand panel refuses to publish while any article fails its
   completeness check; open the offending article and fix it.
3. **Publish the issue.** The system marks the issue current, sets each article
   to published, re-stamps the PDFs, queues the Crossref deposits, notifies the
   authors, refreshes the sitemap and RSS, and clears the public caches.

Afterwards, verify:

```bash
python manage.py crossref_status          # deposits accepted
python manage.py check_metadata           # every article complete
python manage.py export_issue_bundle <id> # preservation bundle
```

Keep the export bundle off-site.

---

## 9. Corrections, retractions and appeals

* **Correction** — an error that does not change the conclusions: edit the
  article, add a note to the article record, and re-deposit the metadata.
* **Retraction** — set the article status to *Retracted* and fill in the
  retraction notice. The article **stays online** with its DOI and is exposed as
  a deleted record through OAI-PMH, as COPE requires.
* **Appeal** — an author may appeal once, in writing, within 30 days. The
  editor-in-chief answers within 30 days and that answer is final. Record the
  appeal and the answer in the submission's discussion thread.

---

## 10. Reports

`/dashboard/reports/` shows acceptance rate, median days to first decision,
median review time, active reviewers and the monthly submission chart, with a
CSV export. These are the numbers Scopus and DOAJ ask for; check them monthly
and keep the export.

---

## 11. Things that trip editors up

* **The queues are empty** — you are a section editor and see only your own
  sections. The editor-in-chief sees everything.
* **"Send to review" is refused** — no similarity result recorded, or it is
  above the threshold without a justification.
* **"Publish" is refused** — open the article's completeness checklist; a red
  required item blocks it.
* **The reviewer says they never received the invitation** — check the
  reviewer's row for the reminder count, then check the e-mail provider's log.
* **The author says they cannot upload a revision** — the submission must be in
  the *Revision requested* state; if you have already moved it on, move it back.
