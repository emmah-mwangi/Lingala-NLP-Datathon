# Volunteer Authoring Guidelines — Lingala Intent Dataset
Team 7 (Datalynk) | Strathmore NLP Hub Datathon 2026 | Track A: Intent Classification

---

## Before you begin

Read the consent notice (docs/VOLUNTEER_CONSENT.md) and confirm your consent with the team lead before writing any sentences. Read this entire document before writing your first sentence.

---

## 1. What you are writing

You are writing short, natural Lingala sentences that a person might say to a voice assistant or type into a chat interface. Each sentence must clearly express one of the ten intent categories listed in section 3.

You are not translating English sentences. You are imagining real situations and writing what a Lingala speaker would naturally say in that situation.

---

## 2. How to write natural Lingala sentences

**Start from a situation, not from English.**
Think of a real moment: you wake up and want to know the time, you are at the market and want to add something to your list, you want to hear music while cooking. Write what you would actually say in that moment in Lingala.

**Vary your sentences.**
Do not write the same sentence with only one word changed. Vary the structure, the vocabulary, the level of formality, and the context. A short direct request and a longer polite request for the same intent are both useful.

**Use both short and longer forms.**
"Loba ngonga" (Tell me the time) and "Nakosepela koyeba ngonga ezali nini sikoyo" (I would like to know what time it is now) are both valid for the same intent.

**Write sentences of different lengths.**
Aim for a mix: some very short (3–6 words), some medium (7–12 words), some longer where natural.

---

## 3. The ten intent categories

Use exactly these label names in your submission form. Do not invent new labels.

| Label | What it means | Example situation |
|---|---|---|
| `weather_query` | Asking about weather conditions or forecast | You want to know if it will rain before going out |
| `datetime_query` | Asking the current date or time | You want to know what time it is |
| `alarm_set` | Asking to set an alarm to ring at a specific time | You want to be woken up tomorrow morning |
| `calendar_set` | Creating a new calendar event or scheduled reminder | You want to add a meeting to your calendar |
| `calendar_query` | Asking about existing calendar events | You want to know what is on your schedule today |
| `lists_createoradd` | Creating a new list or adding an item to an existing list | You want to add something to your shopping list |
| `lists_query` | Reading or checking an existing list | You want to hear what is on your shopping list |
| `play_music` | Requesting music playback | You want to listen to music |
| `news_query` | Asking for news updates or headlines | You want to hear the latest news |
| `qa_definition` | Asking for the meaning of a word or concept | You want to know what a word means |

**Important boundaries (do not confuse these):**
- Asking about a storm in the news → `news_query`, not `weather_query`
- Setting an alarm → `alarm_set`; scheduling a meeting → `calendar_set`
- Adding to a list → `lists_createoradd`; reading a list → `lists_query`
- Asking who wrote a song → not `play_music` (out of scope)
- General factual questions that are not definitions → out of scope

If you are unsure which label fits, write a note and ask the team lead before submitting.

---

## 4. Avoiding duplicates and near-duplicates

- Do not write two sentences that differ only in a single name or number (for example, two alarm-set sentences that are identical except for the time).
- Do not write paraphrases of sentences you have already written in the same batch.
- If two sentences are very similar, group them with the same `group_id` value in your submission so the validator can keep them in the same split.
- The validator will reject exact duplicates after basic normalisation. Near-duplicates that pass the validator but are semantically identical are still a quality problem — use your judgement.

---

## 5. Spelling and language conventions

**⚠ PENDING CONFIRMATION — Caroline (T07-A) must confirm the team's approved spelling conventions before volunteers begin writing.**

The following are placeholders. Do not treat them as final until Caroline confirms:

- [ ] Diacritic conventions (tonal marks, if used): *[Caroline to specify]*
- [ ] Preferred orthographic standard or reference: *[Caroline to specify]*
- [ ] Accepted regional variety: *[Caroline to specify]*
- [ ] Any specific vocabulary preferences or exclusions: *[Caroline to specify]*

**What is confirmed:**
- Preserve natural spelling. Do not simplify or anglicise Lingala words to make them easier to type.
- Do not invent spellings. If you are unsure how to spell a word, flag it for Caroline's review.
- NFC Unicode normalisation is applied automatically by the validator. You do not need to worry about this.

---

## 6. French code-switching

**⚠ PENDING CONFIRMATION — Caroline (T07-A) must confirm the team's approved code-switching convention.**

Lingala speakers frequently mix French words into everyday speech. The team needs to decide:

- [ ] Whether French code-switching is permitted in contributed sentences.
- [ ] If permitted, which French words or patterns are acceptable.
- [ ] How to mark or handle code-switched tokens in the dataset.

**Until Caroline confirms the convention:**
- Write primarily in Lingala.
- If a French word feels completely natural and unavoidable in context, you may include it, but flag the sentence clearly in your submission notes so Caroline can review it.
- Do not inject French words artificially to increase variety.

---

## 7. Avoiding personal and identifying information

Your sentences must not contain:

- Real names of any person (including yourself, friends, or family).
- Phone numbers, email addresses, or any contact details.
- Student registration numbers, admission numbers, or ID numbers.
- Real addresses or location details that could identify a specific person.

Use generic or fictional references where needed. For example:
- Instead of a real person's name, use a generic role: "my friend", "the teacher", "my colleague".
- Instead of a real address, use a generic place: "in town", "at the market", "at school".

---

## 8. How to submit your contribution

1. Write your sentences in the submission form or template provided by the team lead.
2. For each sentence, record:
   - The sentence text (in Lingala).
   - The intent label (from the table in section 3).
   - A `group_id` if two or more of your sentences are closely related paraphrases.
   - Any notes or flags (for example, uncertain label, code-switching, spelling query).
3. Send your completed submission to the team lead (Emmah, T07-B) through the agreed channel.
4. Do not submit sentences you are not confident about without flagging them. A flagged uncertain sentence is more useful than an unflagged wrong one.

Your sentences will be assigned a record ID and a pseudonymous contributor code (T07-V1, T07-V2, or T07-V3) by the team lead. You do not need to add these yourself.

---

## 9. What happens after you submit

1. The team lead assigns record IDs and enters your sentences into the dataset.
2. Caroline (T07-A) reviews each sentence for language quality, label accuracy, and spelling.
3. Sentences that pass review are marked `independently_reviewed` in the dataset.
4. You may be asked to revise or replace sentences that do not pass review.
5. Test-set sentences require independent review by someone who did not author them.

---

## 10. Quick checklist before submitting

- [ ] I have read the consent notice and confirmed my consent.
- [ ] Each sentence is natural Lingala, not a word-for-word English translation.
- [ ] Each sentence has exactly one intent label from the approved list.
- [ ] No two sentences in my batch are near-identical paraphrases (unless grouped).
- [ ] No sentence contains real names, phone numbers, email addresses, or ID numbers.
- [ ] I have flagged any sentences with uncertain labels or code-switching.
- [ ] I have flagged any spelling uncertainties for Caroline's review.

---

*Document version: 1.0 | Prepared by T07-B (Emmah) | Spelling conventions and code-switching sections pending confirmation by T07-A (Caroline)*
