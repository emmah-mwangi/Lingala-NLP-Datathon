# Baseline log (T18)

Owner: Tatyana | Date: 8 Nov 2026

## Run 1: pipeline check on batches 1-2
- **Data:** batch_1_working.csv + batch_2_working.csv, 160 Lingala sentences. This was a scratch copy made outside the repo and not committed.
- **Split:** temporary random 60/20/20 per label. No group_id handling.
- **Mode:** --practice, because there are fewer than 250 records. This is a pipeline check and not a contribution.
- **Review status:** language-lead review only (self-reviewed). Nothing here counts as independently reviewed.
- **Model:** character TF-IDF (2-5 grams) + logistic regression, starter kit v2.0, unchanged.
- **Python:** 3.13.13

| | Accuracy | Macro-F1 |
|---|---|---|
| Model (dev, 30 rows) | 0.833 | 0.831 |
| Majority baseline (dev) | 0.100 | 0.018 |

Weakest labels (F1 0.667): datetime_query, lists_createoradd, lists_query.
Main confusions: lists_createoradd and lists_query mixed up with each other; weather_query predicted as datetime_query; calendar_set predicted as calendar_query.

## Caveats
Dev has 3 rows per label, so scores are noisy. The temporary split may leak near-paraphrases, so the score is likely optimistic. evaluate.py was not run, and the test split stays untouched until the freeze. The real split and the independent review come at T23 and T24.
