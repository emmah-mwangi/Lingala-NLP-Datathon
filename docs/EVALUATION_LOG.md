# Final test evaluation 

Owner: Tatyana | Date: 10 Nov 2026

- **Data:** frozen dataset v1 (tag dataset-freeze-v1), 250 records: 150 train / 50 dev / 50 test, 5 test rows per intent.
- **Settings:** chosen on dev only (see docs/TUNING_LOG.md). Dev macro-F1 from train.py: 0.921.
- **Command:** python evaluate.py --track intent --data data/contribution.csv
- **Run count:** evaluate.py was run twice on identical data, model and settings. The first run printed its scores and then stopped on a Windows display-encoding error (cp1252) before per_label_report.csv was rewritten. The second run, with PYTHONUTF8=1, completed. test_predictions.csv was byte-identical across the two runs (SHA-256 hashes compared). Nothing was changed or tuned in between.
- **Result (test, 50 rows):** accuracy 0.960, macro-F1 0.960, majority-baseline macro-F1 0.018.

| Intent | F1 |
|---|---|
| weather_query, calendar_set, calendar_query, play_music, news_query, qa_definition | 1.000 |
| alarm_set, lists_createoradd | 0.909 |
| datetime_query, lists_query | 0.889 |

- **Errors:** 2 of 50 test sentences were misclassified (see test_predictions.csv; analysis in T31).
- **Files:** results/test_metrics.json, results/per_label_report.csv, results/test_predictions.csv. The bar characters in results/evaluate_console.txt are garbled by console encoding; per_label_report.csv is the clean source.
- **Caveats:** the test set is small, so one sentence moves accuracy by 2 points. Related-sentence grouping was done by script, and Caroline's confirmation is [pending / done].