# Data Management Guide — Team 7 (Datalynk)
Maintained by T07-B (Emmah) | Lingala Intent Classification | Track A

---

## Files created by this workflow

| File | Location | Git-tracked? |
|---|---|---|
| Master contribution dataset | `data/contribution.csv` | ✓ Yes |
| Private per-record Record Log | `private/source_log/record_log.csv` | ✗ No (`private/` is gitignored) |
| Data quality checker | `data_quality.py` | ✓ Yes |
| Batch ingestion script | `ingest_batch.py` | ✓ Yes |
| Reconciliation script | `reconcile.py` | ✓ Yes |
| Dataset status report | `dataset_status.py` | ✓ Yes |
| Tests | `tests/test_data_management.py` | ✓ Yes |

---

## Contribution schema (do not change without team approval)

`data/contribution.csv` uses exactly these 15 columns, matching `data/template.csv`:

```
record_id, language, text, label, source_dataset, source_version,
source_record_id, source_url, source_method, licence_or_permission,
contributor_code, reviewer_code, review_status, group_id, split
```

- `language` must be `ln` (ISO 639-1 for Lingala) for all real contributions.
- `label` must be one of the 10 approved intents (see taxonomy.csv).
- `source_method` must be `original_human` for volunteer-authored sentences.
- `split` is left blank until Tatyana assigns it — do not fill it yourself.
- `reviewer_code` and `review_status` are filled after Caroline's review.

---

## Ten approved intent labels

```
weather_query    datetime_query   alarm_set        calendar_set
calendar_query   lists_createoradd  lists_query    play_music
news_query       qa_definition
```

---

## Batch collection schedule

| Batch | Date | Cumulative target |
|---|---|---|
| batch-01 | Thursday 5 November | ~80 records total |
| batch-02 | Friday 6 November | ~150 records total |
| batch-03 | Saturday 7 November | 250 records total, 25 per label |

These are **cumulative** totals, not additions per batch.

---

## Step-by-step: receiving and ingesting a batch

### 1. Receive contributions

Collect sentences from volunteers (T07-V1, T07-V2, T07-V3) and team members.
Save them as a CSV with at minimum these columns:

```
text, label, contributor_code, source_method, language
```

Other columns are optional in the incoming batch — the ingestion script fills defaults.
Save the file as e.g. `data/incoming/batch-01.csv`.

### 2. Run a dry-run first

```
python ingest_batch.py --batch data/incoming/batch-01.csv --batch-id batch-01 --date 2026-11-05 --dry-run
```

Read the output carefully. Check that accepted/flagged counts look right.

### 3. Ingest for real

```
python ingest_batch.py --batch data/incoming/batch-01.csv --batch-id batch-01 --date 2026-11-05
```

The script will:
- Assign `T07-NNN` record IDs to any row that lacks one.
- Append accepted rows to `data/contribution.csv`.
- Append log entries to `private/source_log/record_log.csv`.
- Write flagged rows to `data/review/batch-01_flagged.csv`.

### 4. Review flagged records

Open `data/review/batch-01_flagged.csv`. The `_flags` column explains each issue.
For each flagged row, decide:
- Correct the issue and re-ingest, OR
- Manually add to `data/contribution.csv` after resolving the issue, OR
- Reject the record and note the reason in the Record Log.

Never delete flagged records silently. Document every decision.

### 5. Run the quality checker

```
python data_quality.py --data data/contribution.csv
```

Address any new flags before the next batch.

### 6. Check dataset status

```
python dataset_status.py
```

This shows progress against batch milestones, label distribution and volunteer allocation.

### 7. Update the private Record Log

Open `private/source_log/record_log.csv` and update:
- `review_status` once Caroline has reviewed a record.
- `correction_status` if a record was corrected.
- `approval_status` once a record is approved (`approved` / `rejected`).

### 8. Run reconciliation

```
python reconcile.py
```

Run this after every batch and before handing over to Tatyana.
Fix any discrepancies it reports before the handover.

---

## Record ID format

All records use the format `T07-NNN` (e.g. `T07-001`, `T07-042`, `T07-250`).
The ingestion script assigns IDs automatically. Never reuse a retired ID.

---

## Author codes

| Code | Role |
|---|---|
| T07-A | Caroline (annotation and review lead) |
| T07-B | Emmah (data upkeep lead) |
| T07-C | Tatyana (pipeline lead) |
| T07-V1 | Volunteer 1 |
| T07-V2 | Volunteer 2 |
| T07-V3 | Volunteer 3 |

Never record real names, phone numbers, email addresses or student numbers anywhere in these files.

---

## Volunteer test record targets

| Volunteer | Target records |
|---|---|
| T07-V1 | 17 |
| T07-V2 | 17 |
| T07-V3 | 16 |
| **Total** | **50** |

These 50 records are part of the 250-record dataset, not additional to it.
Every volunteer test record must be independently reviewed by Caroline (T07-A).

---

## Review workflow (Caroline's responsibility)

1. Caroline reviews records authored by volunteers.
2. She sets `reviewer_code = T07-A` and `review_status = independently_reviewed`.
3. Emmah updates the Record Log: `review_status` and `approval_status`.
4. The reviewer code must differ from the contributor code — the validator enforces this.

---

## Privacy rules

- `private/` is excluded from Git (see `.gitignore`). Never commit anything under it.
- Do not record real identities anywhere in any tracked file.
- Do not include phone numbers, emails or student numbers in `text` fields.
- The PII checker in `data_quality.py` and `ingest_batch.py` flags common patterns but is not exhaustive — human review is still required.

---

## Handover to Tatyana (T07-C)

Before handing over `data/contribution.csv` to Tatyana for splitting:

1. Run `python reconcile.py` — resolve all reported issues.
2. Run `python data_quality.py --data data/contribution.csv` — no unresolved flags.
3. Confirm 250 records are present with 25 per label.
4. Confirm all 50 volunteer records have `review_status = independently_reviewed`.
5. Confirm `split` column is blank for all records (Tatyana fills this).
6. Confirm `group_id` is set correctly so related records stay together.
7. Tell Tatyana which records are volunteer-authored (by `contributor_code`) so she can ensure they land in the test split.

Tatyana will then run:
```
python validate.py --track intent --data data/contribution.csv
python train.py --track intent --data data/contribution.csv
python evaluate.py --track intent --data data/contribution.csv
```

Do not run these yourself with the final dataset — Tatyana owns the frozen commit.

---

## Quick-reference commands

```bash
# Check dataset status
python dataset_status.py

# Quality check
python data_quality.py --data data/contribution.csv

# Ingest a batch (dry run first)
python ingest_batch.py --batch data/incoming/batch-01.csv --batch-id batch-01 --date 2026-11-05 --dry-run
python ingest_batch.py --batch data/incoming/batch-01.csv --batch-id batch-01 --date 2026-11-05

# Reconcile CSV against Record Log
python reconcile.py

# Run tests
python -m pytest tests/test_data_management.py -v
```
