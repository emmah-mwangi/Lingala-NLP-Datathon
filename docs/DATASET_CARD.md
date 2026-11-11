# Dataset Card: Lingala Intent Classification

## 1. Dataset Overview

The Lingala Intent Classification dataset was created by Team 7 (Datalynk) for the Strathmore NLP Hub Datathon 2026, Track A.

The purpose of the dataset is to train and evaluate a machine-learning model that identifies the intended action in a Lingala sentence.

The project is an academic exercise and is not a commercial product.

## 2. Language and Variety

- Language: Lingala
- Language code: `ln`
- Reference variety: Kinshasa Lingala (DRC)
- Writing style: Natural everyday Lingala, including commonly used French loanwords and code-switching where appropriate.

The dataset aims to represent sentences that people would naturally use rather than direct word-for-word translations from English.

## 3. Dataset Size and Structure

The frozen dataset contains 250 records across 10 intent categories.

Each category contains 25 records:

- Training set: 15 records per intent (150 total).
- Development set: 5 records per intent (50 total).
- Test set: 5 records per intent (50 total).

The dataset uses CSV format. Each record includes information such as its ID, language, sentence, intent label, source information, contributor code, review status and split.

## 4. Intent Categories

The dataset covers the following 10 intents:

1. `weather_query`
2. `datetime_query`
3. `alarm_set`
4. `calendar_set`
5. `calendar_query`
6. `lists_createoradd`
7. `lists_query`
8. `play_music`
9. `news_query`
10. `qa_definition`

These labels represent different actions that a user may request from an assistant.

## 5. Data Collection

The dataset was developed using original human-authored Lingala sentences contributed by team members and volunteers.

Volunteers were assigned pseudonymous codes (`T07-V1`, `T07-V2` and `T07-V3`) to protect their identities.

Contributors were guided to write natural sentences based on everyday situations, with variation in vocabulary, sentence structure and context.

The project also used language review to check sentence naturalness and intent-label accuracy.

## 6. Consent and Permissions

Volunteer participation was voluntary. Contributors were informed about the purpose of the project and how their sentences would be used.

Real names and personal identifying information are excluded from the public dataset.

Participation consent and permission for public dataset release are separate choices. Public release requires explicit permission from each volunteer.

The dataset's public distribution is subject to the consent records, team decisions and datathon organiser requirements.

## 7. Data Processing and Quality Control

The dataset went through batch ingestion, validation, duplicate checks, review and reconciliation.

The Language and Documentation Lead reviewed language naturalness, spelling, meaning and intent labels.

A sample of 50 training and development records was reviewed separately. In that sample, 49 were accepted and one had a suggested intent-label correction.

The final test evaluation also included an error analysis of the model's incorrect predictions.

## 8. Intended Uses

The dataset is intended for:

- Academic research and learning.
- Training Lingala intent classification models.
- Evaluating how well a model recognises different user requests.
- Studying language technology for Lingala.

It should not be treated as a production-ready dataset for systems that perform real-world actions without further testing.

## 9. Limitations

- The dataset contains only 250 records.
- It covers 10 predefined intent categories.
- It focuses on Kinshasa Lingala and may not represent all Lingala varieties.
- The sentences may not cover every way people express the same request.
- Model performance on this dataset does not guarantee performance in real-world conversations.
- The dataset is not suitable for general speech recognition because it contains text records rather than audio recordings.

## 10. Privacy and Ethical Considerations

Contributions should not contain real names, contact details, student numbers, addresses or sensitive personal information.

Contributor identities are represented using pseudonymous codes.

Private consent records and identity mappings must remain outside the public repository.

## 11. Maintenance and Contact

Team: Team 7 (Datalynk)

Project: Strathmore NLP Hub Datathon 2026, Track A

Language and Documentation Lead: T07-A

Frontend and Data-Upkeep Lead: T07-B

Backend and Pipeline Lead: T07-C

For questions about the dataset, contact the team through its agreed communication channel.