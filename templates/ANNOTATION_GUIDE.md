# Lingala Intent Classification Annotation Guide

## 1. Task and exact label set

Team: 7 (Datalynk)
Track: A - Intent Classification
Primary language: Lingala

The purpose of this task is to identify what a person wants when they enter a sentence in Lingala. Each sentence must receive one intent label.

The ten supported labels are:

- weather_query
- datetime_query
- alarm_set
- calendar_set
- calendar_query
- lists_createoradd
- lists_query
- play_music
- news_query
- qa_definition

## 2. Primary language and spelling conventions

All contributed sentences should be written in natural Lingala.

Guidelines:
- Use words and expressions that Lingala speakers commonly understand.
- Keep the original meaning of the sentence.
- Avoid unnecessary English or Kiswahili words.
- Use consistent spelling throughout the dataset.
- Use correct accents where they are part of the chosen spelling.
- Avoid sentences that sound like direct translations from English.
- Ask a fluent Lingala reviewer to check unfamiliar expressions.

## 3. Positive examples for each label

The following are initial examples for discussion and review. They must be checked by a fluent Lingala speaker before being accepted into the dataset.

| Intent | Lingala example | English meaning |
|---|---|---|
| weather_query | Mbula ekobeta lobi? | Will it rain tomorrow? |
| datetime_query | Ngonga ezali boni? | What time is it? |
| alarm_set | Tya alarme na ngonga ya motoba. | Set an alarm for six o'clock. |
| calendar_set | Bakisa likita na ngai na kalandriye. | Add my meeting to my calendar. |
| calendar_query | Nazali na makita nini lelo? | What meetings do I have today? |
| lists_createoradd | Bakisa mapa na liste ya biloko ya kosomba. | Add bread to the shopping list. |
| lists_query | Nini ezali na liste na ngai ya kosomba? | What is on my shopping list? |
| play_music | Yemba miziki. | Play music. |
| news_query | Yebisa ngai bansango ya sika. | Tell me the latest news. |
| qa_definition | Liloba biodiversité elimboli nini? | What does the word biodiversity mean? |

## 4. Boundaries and counterexamples

- weather_query: Asking about weather or forecasts. Asking about a storm in the news is news_query.
- datetime_query: Asking for the current date or time. Setting an alarm is alarm_set.
- alarm_set: Asking to set an alarm. Creating a scheduled meeting is calendar_set.
- calendar_set: Creating a calendar event or reminder. Checking existing events is calendar_query.
- calendar_query: Asking about existing calendar events. Creating a new event is calendar_set.
- lists_createoradd: Creating a list or adding an item. Reading an existing list is lists_query.
- lists_query: Asking what is already in a list. Adding an item is lists_createoradd.
- play_music: Requesting music playback. Asking about a singer or song meaning is not play_music.
- news_query: Asking for news updates. Asking about the weather is weather_query.
- qa_definition: Asking for the meaning of a word or concept. General factual questions are outside this label's scope.

## 5. Ambiguous cases to exclude or adjudicate

- Exclude sentences whose intended meaning is unclear.
- Exclude sentences that mix several unrelated requests.
- Do not guess a label when the sentence does not provide enough information.
- Ask a Lingala reviewer to resolve uncertain wording.
- Record excluded examples and the reason for exclusion.
- If reviewers disagree, discuss the intended meaning before accepting a label.

## 6. Annotation process

1. Read the complete sentence.
2. Identify the main action or information being requested.
3. Compare the request with the ten supported labels.
4. Select the single most appropriate label.
5. Check that the Lingala sentence sounds natural.
6. Submit the sentence for independent review.
7. Correct errors before accepting the example.

## 7. Independent review and disagreement resolution

Each test example must receive independent review.

Reviewers should check:
- Whether the sentence is natural Lingala.
- Whether spelling is consistent.
- Whether the intent label matches the sentence.
- Whether the sentence is clear and understandable.

Disagreements should be discussed and resolved before the example is accepted.

## 8. Data quality requirements

- Use newly authored or permitted human-localised examples.
- Do not count practice examples as contributions.
- Avoid duplicate sentences and simple paraphrases.
- Use group_id for sentences derived from shared sources or paraphrases.
- Keep private permission records separate from public project files.
- Maintain the required train, development and test splits.

## 9. Version and date

Team: Team 7 - Datalynk
Document: Version 1.0
Date: 4 November 2026

This guide may be updated following feedback from Lingala reviewers and the Datathon organisers.
