# Settings chosen on dev only (T29)

Owner: Tatyana | Date: 10 Nov 2026

- **Data:** frozen dataset v1 (tag dataset-freeze-v1), fit on train (150 rows), compared on dev (50 rows). The test split was not used.
- **Grid:** analyzer (char, char_wb) x ngram range ((1,4), (2,4), (2,5), (3,6)) x C (0.5, 1, 5, 10, 50). 40 combinations, all results in docs/dev_tuning_results.csv.
- **Rule set before looking:** change from the starter default only if dev macro-F1 improves by 0.02 or more.
- **Result:** default dev macro-F1 = ___ ; best = ___ (setting).
- **Decision:** KEEP DEFAULT / CHANGED to ___.
- **Caveat:** dev has 5 rows per intent, so differences are noisy. Test is evaluated once in T30.