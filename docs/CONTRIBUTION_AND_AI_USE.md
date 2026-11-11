# Contribution and AI-use statement: Team 7 (Datalynk), Lingala, Track A

## Member contributions
**Tatyana (T07-C), backend and pipeline**
- Ran the starter kit and logged the Python version.
- Baseline run on the first 160 records, logged in docs/BASELINE_LOG.md. Evidence: commit [SHA].
- Wrote split_data.py and produced the 150/50/50 split with group_ids; ran validate.py on the final file.
- Froze the dataset, tag dataset-freeze-v1, commit [SHA].
- Chose settings on dev only (docs/TUNING_LOG.md) and ran the final test evaluation (docs/EVALUATION_LOG.md, results/). Evidence: commits [SHAs].

**Caroline (T07-A), language and documentation**
- Reviewed the Kinshasa Lingala (DRC) language variety and documented spelling and annotation guidance.
- Prepared Kinshasa Lingala sample sentences for the project intents.
- Reviewed 50 sampled train and development records for naturalness, meaning and label accuracy. Accepted 49 records and flagged one label disagreement for review.
- Prepared the language quality report (`docs/QUALITY_REPORT.md`).
- Analysed the two model misclassifications and documented the findings in `docs/ERROR_ANALYSIS.md`.
- Prepared the dataset card (`docs/DATASET_CARD.md`).
- Checked that Lingala examples and documentation reflect natural everyday usage in Kinshasa.

**Emmah (T07-B), frontend and data upkeep**
[Emmah writes: repo and starter commit, Streamlit app, data-management scripts, volunteer consent and recruitment, README, recording. Add commit SHAs.]

**Volunteers** 
**Volunteers** (credited by code only)
- **T07-V1:** Contributed 17 original Lingala sentences across the project intents.
- **T07-V2:** Contributed 17 original Lingala sentences across the project intents.
- **T07-V3:** Contributed 16 original Lingala sentences across the project intents.

All volunteer contributions were reviewed using the project's language and annotation guidelines. Public-release permissions must be confirmed against the private consent records before any release.

## Reused material
Starter code: Strathmore NLP Hub Datathon Starter Kit v2.0, used with its original licence (LICENSE_CODE.txt).

## AI-use declaration
| Tool | Purpose | Human checks |
|---|---|---|
| Claude|debugging pip, PowerShell and encoding errors; drafting split_data.py, tune_dev.py, a readiness-check script and the scratch-data script used for the first baseline run; | Tatyana ran every script, read the validator and evaluation output, compared prediction hashes between evaluation runs, and corrected the AI's mistakes (for example a tag created before the merge) |

## AI-use declaration *Caroline (T07-A)
| Tool | Purpose | Human checks |
|---|---|---|
| 
| ChatGPT | Provided limited support with organising documentation, improving wording and structuring reports. | Caroline independently wrote the Lingala sample sentences, reviewed their naturalness and meanings, checked the intent labels, and made the final language decisions. ChatGPT was not used to generate the sample sentences. |


AI was not used to produce Lingala sentences or labels.