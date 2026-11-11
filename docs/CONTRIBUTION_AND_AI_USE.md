# Contribution and AI-use statement: Team 7 (Datalynk), Lingala, Track A

## Member contributions
**Tatyana (T07-C), backend and pipeline**
- Ran the starter kit and logged the Python version.
- Baseline run on the first 160 records, logged in docs/BASELINE_LOG.md. Evidence: commit [SHA].
- Wrote split_data.py and produced the 150/50/50 split with group_ids; ran validate.py on the final file.
- Froze the dataset, tag dataset-freeze-v1, commit [SHA].
- Chose settings on dev only (docs/TUNING_LOG.md) and ran the final test evaluation (docs/EVALUATION_LOG.md, results/). Evidence: commits [SHAs].

**Caroline (T07-A), language and documentation**
[Caroline writes: data batches and record ranges, review work, annotation guide, DATA_PLAN, dataset card, quality report, error analysis. Add commit SHAs.]

**Emmah (T07-B), frontend and data upkeep**
[Emmah writes: repo and starter commit, Streamlit app, data-management scripts, volunteer consent and recruitment, README, recording. Add commit SHAs.]

**Volunteers** (credited by code only): [T07-V1 to V3: what each wrote, how many records, permission on file]

## Reused material
Starter code: Strathmore NLP Hub Datathon Starter Kit v2.0, used with its original licence (LICENSE_CODE.txt).

## AI-use declaration
| Tool | Purpose | Human checks |
|---|---|---|
| Claude|debugging pip, PowerShell and encoding errors; drafting split_data.py, tune_dev.py, a readiness-check script and the scratch-data script used for the first baseline run; | Tatyana ran every script, read the validator and evaluation output, compared prediction hashes between evaluation runs, and corrected the AI's mistakes (for example a tag created before the merge) |

[Each member adds any AI use of their own.]

AI was not used to produce Lingala sentences or labels.