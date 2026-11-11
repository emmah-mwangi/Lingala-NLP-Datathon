# T31: Model Error Analysis

## 1. Introduction

This report analyses the errors made by the Lingala Intent Classification model during final test evaluation. The test set contained 50 records across 10 intents.

The model achieved 96% accuracy and a macro-F1 score of 0.960. It incorrectly classified 2 records.

## 2. Identified Errors

### Error 1: T07-002

- **Sentence:** Ngonga ezali ngonga nini?
- **Actual intent:** `datetime_query`
- **Predicted intent:** `alarm_set`

**Likely cause:** The model may have relied too much on the word `ngonga` (time/hour), which appears in both time-related questions and alarm requests.

**Suggested improvement:** Include more examples that distinguish asking for the current time from setting an alarm.

### Error 2: T07-231

- **Sentence:** Lakisa ngai liste ya biloko ya kosala na ndako.
- **Actual intent:** `lists_query`
- **Predicted intent:** `lists_createoradd`

**Likely cause:** The model may have associated words such as `liste` and `biloko` with creating or adding to lists instead of recognising that the user is asking to view an existing list.

**Suggested improvement:** Add more examples that clearly distinguish viewing an existing list from creating a new list or adding items.

## 3. Language Review

Both sentences were reviewed by the Language and Documentation Lead and confirmed as natural Kinshasa Lingala. Their intended meanings and original labels were also confirmed.

Therefore, the two errors appear to be classification mistakes rather than language or annotation problems.

## 4. Conclusion

The model correctly classified 48 out of 50 test records. The two errors involved confusion between related intents: `datetime_query` and `alarm_set`, and `lists_query` and `lists_createoradd`.

Future improvements should include more varied examples that help the model distinguish between these similar requests.