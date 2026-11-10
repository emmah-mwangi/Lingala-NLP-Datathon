# Lingala Intent Classification Dataset Quality Report

## 1. Introduction

This report presents the language quality review of the Team 7 Lingala Intent Classification dataset. The review focused on checking whether the sentences use natural Kinshasa Lingala, whether their meanings are clear, and whether they match their assigned intents.

The review was conducted by the Language and Documentation Lead.

## 2. Dataset Overview

The frozen dataset contains 250 records covering 10 intents. Each intent has 25 records divided as follows:

- Training: 15 records per intent (150 total).
- Development: 5 records per intent (50 total).
- Testing: 5 records per intent (50 total).

The review focused on a sample of 50 records from the training and development sets. Five records were selected from each intent: three training records and two development records.

## 3. Review Method

Each sampled sentence was checked for:

- Naturalness in Kinshasa Lingala.
- Correct spelling and understandable wording.
- Whether the sentence communicates the intended meaning.
- Whether the assigned intent matches what the sentence asks the system to do.

The review decisions and comments were recorded in `data/caroline_t25_sample.csv`. The frozen dataset was not modified during this review.

## 4. Review Results

A total of 50 records were reviewed.

| Result | Number |
|---|---:|
| Accepted | 49 |
| Flagged for label review | 1 |
| Language corrections | 0 |
| Total reviewed | 50 |

Most of the reviewed sentences were natural and understandable in Kinshasa Lingala. No wording or spelling corrections were identified in this sample.

### Label Disagreement

One record was flagged:

- Record ID: `T07-088`
- Original intent: `lists_createoradd`
- Suggested intent: `lists_query`
- Reason: The sentence asks the assistant to open an existing shopping list. It does not ask the assistant to create a list or add an item.

The sentence itself is natural Lingala. The issue concerns the assigned intent, not the language.

This is a recommendation for the dataset team to review before changing the frozen dataset.

## 5. Language Quality Observations

The reviewed records generally used understandable Kinshasa Lingala. The sentences included common French loanwords and everyday expressions used in normal communication.

The reviewed examples covered different everyday requests, including setting alarms, checking dates, managing calendars and lists, playing music, asking for news, and requesting definitions.

The language review did not identify any spelling or wording corrections in the 50-record sample.

## 6. Limitations

This review covered only 50 of the 200 training and development records. Therefore, the findings should not be treated as proof that every record in the dataset is error-free.

The testing records were not part of this language review because they had already undergone independent review.

The suggested label change for T07-088 also requires agreement from the team before the frozen dataset is updated.

## 7. Recommendations

1. Review the suggested label change for T07-088 with the dataset and pipeline team.
2. Keep using Kinshasa Lingala as the reference variety for future contributions.
3. Continue checking both sentence naturalness and intent correctness during annotation.
4. Preserve the frozen dataset until any approved changes are made through the team's agreed process.
5. Carry out further quality checks if additional time is available.

## 8. Conclusion

The sample review found that 49 out of 50 records were acceptable, while one record had a possible intent-label mismatch. No language corrections were needed in the reviewed sample.

Overall, the reviewed examples showed good language quality and generally matched their intended intents. Further checks are still necessary before making claims about the quality of the entire dataset.