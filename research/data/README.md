# Dataset for the department classifier

All experiments read **one CSV** that you build, split once with `split_dataset.py`.

## Format

`dataset.csv` (UTF-8):

| column | required | values |
|---|---|---|
| `text` | yes | full document text (digital text or OCR output) |
| `label` | yes | `FINANCE`, `HR`, `LEGAL`, `OPERATIONS` |
| `language` | recommended | `English`, `Hindi`, `Mixed` |
| `source` | recommended | where the document came from (needed for the paper's data section) |
| `id` | optional | stable identifier; generated from the text if absent |

`smoke_test.csv` is an 8-row sanity file only. It is far too small to report any result.

## How much data

- Minimum for a credible paper: **~250 documents per class (1,000 total)**, with at least 150 test documents.
- For the bilingual research question: at least **100 Hindi and 100 Mixed documents per class** across the whole set, so the per-language test numbers have meaningful sample sizes.

## Labelling guideline (decide by the department that must act)

| Label | Belongs here | Typical examples |
|---|---|---|
| FINANCE | money moves or is accounted for | invoices, purchase orders, budgets, expense claims, payment reminders, tax/audit statements |
| HR | concerns an employee or candidate | resumes, offer letters, leave requests, appraisals, grievances, payroll queries, HR policies |
| LEGAL | creates or disputes rights and obligations | contracts, NDAs, legal notices, court summons, compliance and regulatory filings |
| OPERATIONS | running day-to-day work | logistics, incident/maintenance reports, schedules, inventory, IT tickets, general memos |

Tie-breaks: label by the **action needed** (an invoice dispute that threatens litigation is LEGAL; an employee's reimbursement claim is FINANCE). Record any rule you add here so it can be cited in the paper.

## Quality steps reviewers will ask about

1. **Two annotators** label a random 10–20% sample independently; report **Cohen's kappa**. Resolve disagreements and document how.
2. **No leakage:** `split_dataset.py` removes duplicate texts; also keep near-identical templates (same form with different names) in the same split.
3. **Disclose synthetic data.** If you translate or generate any documents (for example to create Hindi samples), mark them in `source`, and keep the **test set real, human-written documents**, or report results on real and synthetic test data separately.
4. **Remove personal data** (names, phone numbers, IDs) before sharing the dataset.

## Candidate sources

- Your institution's or a partner company's anonymised documents (best: real distribution).
- Public legal text such as contract clauses from SEC EDGAR filings (LEGAL).
- Publicly posted government circulars, tenders and notices, many of which are bilingual Hindi/English (all four classes).
- Human-verified documents exported from this app (`research/export_feedback.py`).

Check each source's licence before redistributing the dataset.
