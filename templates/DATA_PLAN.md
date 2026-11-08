# Data Plan - Team 7 (Datalynk)

## 1. Team / task / primary language / variety

Team number: 7
Team name: Datalynk
Track: A - Intent Classification
Primary language: Lingala
Language variety: Kinshasa Lingala (Democratic Republic of Congo).
## 2. Reviewer and capacity

The team will work with Lingala-speaking volunteers to check sentence quality and annotation accuracy.

Volunteer reviewers will be identified using pseudonymous codes:
- T07-V1
- T07-V2
- T07-V3

Their private contact details will not be included in public project files.

## 3. Dataset source and collection plan

The team will create a dataset using newly authored Lingala sentences and human-reviewed examples.

The English practice dataset will only be used to understand the starter kit. It will not be counted as a contribution.

All newly collected sentences must be checked for natural Lingala expressions and correct intent labels.

## 4. Contribution type and record target

Contribution type: Human-authored Lingala examples and reviewed human-localised sentences.

Minimum target: 250 accepted examples. This is the team's target and has not yet been achieved.

Each of the ten intent labels must have at least 25 accepted examples.

Required distribution per label:
- Training: 15 examples
- Development: 5 examples
- Testing: 5 examples

Total:
- Training: 150 examples
- Development: 50 examples
- Testing: 50 examples

## 5. Labels and edge cases

The dataset will use the ten labels in taxonomy.csv:

1. weather_query
2. datetime_query
3. alarm_set
4. calendar_set
5. calendar_query
6. lists_createoradd
7. lists_query
8. play_music
9. news_query
10. qa_definition

Sentences with unclear meanings, multiple unrelated requests or uncertain labels will be excluded until reviewed.

## 6. Train/dev/test grouping and independent review

The dataset will be divided into training, development and testing groups.

Sentences from the same source or closely related paraphrases will share a group_id to reduce data leakage.

All test examples must receive independent review.

The team will check for:
- Duplicate sentences.
- Incorrect intent labels.
- Unnatural Lingala expressions.
- Inconsistent spelling.
- Missing or incorrect data fields.

## 7. Team responsibilities

- Caroline (T07-A): Lingala language review, spelling conventions, annotation guide, dataset card, quality report and error analysis.
- Emmah (T07-B): Streamlit frontend, Record Log, contribution.csv upkeep, README and volunteer permissions.
- Tatyana (T07-C): Backend, validation, model training, evaluation, data splits and final testing.
- Lingala volunteers (T07-V1 to T07-V3): Language review and feedback on contributed examples.

## 8. Access, compute risks and help needed

The team will use the provided Python starter kit and CPU-based baseline model.

Potential challenges include:
- Limited availability of fluent Lingala reviewers.
- Differences in Lingala spelling and expressions.
- Incorrect or ambiguous intent labels.
- Duplicate or closely related examples.

The team will address these challenges through language review, annotation guidelines and independent testing.

## 9. Organiser confirmation and date

Team: Team 7 - Datalynk
Task: Lingala Intent Classification
Document version: 1.0
Date: 4 November 2026

Organiser confirmation: Pending.
