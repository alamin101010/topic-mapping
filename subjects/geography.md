# Subject profile — geography

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `geography`
- `grade`: `9-10`
- language mix: Bengali + English technical terms (geology/geomorphology/science terms, SDG/GIS/GPS acronyms) — keep English terms as-is.

## What a topic looks like in this subject
A named **landform, earth process, spatial pattern, region, resource, or map concept** — something a student revises as one unit:

- GOOD: `নদীর ক্ষয় ও সঞ্চয় প্রক্রিয়া`, `বাংলাদেশের জলবায়ুর বৈশিষ্ট্য`, `সৌরজগতের গঠন`,
  `বায়ুমণ্ডলের স্তরবিন্যাস`, `সমুদ্রস্রোতের কারণ ও প্রভাব`, `জনসংখ্যা পিরামিড`,
  `বাংলাদেশের পর্যটন শিল্প`, `দুর্যোগ ব্যবস্থাপনা চক্র`
- NOT a topic: a single fact/drill (টারশিয়ারি যুগের একটি নাম), a map-reading or
  identification exercise (`মানচিত্রে দূরত্ব মাপা`, `মানচিত্র পরিদর্শন`, `মানচিত্রে
  সময় সংক্রান্ত প্রশ্ন`), a stage of a process with its head concept dropped
  (`প্রাথমিক পর্যায়`, `মধ্য গতি`).

## Head-noun rule for this subject
The enclosing concept is almost always **the landform / process / region / resource
the section is about**. Prefix bare attribute headings accordingly:

- `নদীর উৎসগতি`, not `উৎসগতি`; `অভিবাসনের কারণ`, not `কারণ`
- `বসতি স্থাপনের প্রাকৃতিক নিয়ামক`, not `প্রাকৃতিক নিয়ামক`
- `শিল্প গড়ে ওঠার অর্থনৈতিক নিয়ামক`, not `অর্থনৈতিক নিয়ামক`
- `জনসংখ্যা পরিবর্তনের প্রাথমিক পর্যায়`, not `প্রাথমিক পর্যায়`
- `ভূমিকম্পের কারণ ও প্রভাব`, not separately `কারণ` / `প্রভাব` / `ফলাফল` rows for
  the same phenomenon

## Label length & staying self-identifying (README §3.6, prompt §5b)
Same rules as the general profile; `config/geography.json → scope_split.max_core_words =
5`. Process chains (ধারণা / বৈশিষ্ট্য / প্রকারভেদ / গুরুত্ব / কারণ / প্রভাব of the same
concept) merge into one row: `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব`.

When a heading names a concept and then lists its instances/parts (rock types,
projections, atmosphere layers, migration types, flood types, mountain types),
write them as a trailing `(a, b, c …)` so Step 10 lifts them to `scope_note`:
`আগ্নেয় শিলা (গ্র্যানাইট, ব্যাসল্ট)`; `মানচিত্র প্রণালী (ইকুয়েটরিয়াল, কোণীয়, সমতলীয়, আর-মেরকাটর, ...)`.
Give each item its own row only when it is a full topic taught in its own right
(e.g. `ভঙ্গিল পর্বত` vs `স্তূপ পর্বত` vs `ল্যাকোলিথ পর্বত` as distinct landforms).
Do NOT emit dozens of `মানচিত্রে X` skill rows — those are exercises, not concepts.

## Distinct concepts to KEEP SEPARATE (never let the merge collapse these)
- `প্রাকৃতিক ভূগোল` ≠ `মানব ভূগোল` ≠ `উপকৃত ভূগোল`
- `প্রাকৃতিক পরিবেশ` ≠ `মানবসৃষ্ট পরিবেশ`
- `আগ্নেয় শিলা` ≠ `পাললিক শিলা` ≠ `রূপান্তরিত শিলা`
- `আগ্নেয় পর্বত` ≠ `ভঙ্গিল পর্বত` ≠ `স্তূপ পর্বত` ≠ `ল্যাকোলিথ পর্বত`
- `উৎস` ≠ `মধ্যগতি` ≠ `নিম্নগতি` (river course stages) — distinct but all keep `নদীর`
- `জোয়ার` ≠ `ভাটা`; `নদী` ≠ `খাল` ≠ `সমুদ্র`; `মহাদেশ` ≠ `মহাসাগর`
- `বন্যা` ≠ `খরা` ≠ `ঘূর্ণিঝড়` ≠ `নদীভঙ্গন` ≠ `ভূমিকম্প` ≠ `সুনামি` (disaster types)
- `জনসংখ্যা` ≠ `জনঘনত্ব` ≠ `জনসংখ্যা কাঠামো`; `আমদানি` ≠ `রপ্তানি`
- `নবায়নযোগ্য সম্পদ` ≠ `অনবায়নযোগ্য সম্পদ`
- `গ্রামীণ বসতি` ≠ `নগর বসতি`; `আকর্ষণমূলক কারণ` ≠ `বিকর্ষণমূলক কারণ`
- `ট্রপোস্ফিয়ার` ≠ `স্ট্র্যাটোস্ফিয়ার` ≠ `মেসোস্ফিয়ার` (layers stay separate)
- `উন্নত দেশ` ≠ `উন্নয়নশীল দেশ` ≠ `অনুন্নত দেশ`
- `স্থানীয় মানচিত্র` ≠ `আন্তর্জাতিক মানচিত্র` (and `জিপিএস` ≠ `জিআইএস`)

## Canonical spellings of technical terms
**Verify every fix against the page image before enrolling it in
`config/geography.json → spelling_corrections` (cite the PDF page).** Known-correct
references (confirmed by domain, not yet by page): `ইক্ষু` (sugarcane, not `ইখু`),
`নবায়নযোগ্য সম্পদ` (renewable, not `পুনর্ব্যবহারযোগ্য`), `পলল শঙ্কু` (alluvial fan).

### Watchlist — OCR garble SUSPECTED in the earlier Google-sheet export, VERIFY on the page
The `docs/agent-memory/geography-sheet-export.csv` is an earlier **hand-built sheet
that did NOT come from this pipeline** — treat it as a hypothesis list, never as
ground truth. Suspects to confirm/rule out against the printed book:

| suspect (in sheet) | likely correct | where |
|---|---|---|
| মানচিত্র **পর্ন** ও ব্যবহার | মানচিত্র **পঠন** ও ব্যবহার | ch3 chapter title (sheet rows split mid-chapter) |
| রিচার্থ মানচিত্র প্রণালী | ? (some map projection) | ch3 |
| থিম্পোসো মানচিত্র প্রণালী | ? | ch3 |
| জ্যোতির্বৃন্দ | জ্যোতিষ্কমণ্ডল? | ch2 (§আমাদের ... ও দূরত্ব) |
| পৃথিবীর বর্তন | আবর্তন / বিস্তরণ? | ch2 |
| বিচ্চীভবন | অপচয়ীভবন? | ch4 |
| নগ্নীভবন | ? | ch4 |
| সিঁড়ার কোণ (আগ্নেয়গিরি) | সিন্ডার কোণ / সিন্ডার শঙ্কু | ch4 |
| প্রাবন (সমতলভূমি) | ? | ch4 |
| স্তৃতি-স্তূপ (পর্বত) | ? | ch4 |
| নদীর উৎসর্গতি | নদীর উৎস/মধ্যগতি? | ch4 |
| অ্যারোনমোস্ফিয়ার | ? | ch5 |
| বায়ু বাহু | ? | ch5 |
| বারিমণ্ডল (chapter is জলমণ্ডল) | জলমণ্ডল | ch6 |
| জলমণ্ডলের মহীতল | ? | ch6 |
| জনসংখ্যা বর্তন | জনসংখ্যা বিতরণ? | ch7 |
| দুর্যোগ উন্নয়ন (6th DRM phase) | not a standard phase — likely invented | ch14 |
| টেকসই উন্নয়ন অভীক্ষা | টেকসই উন্নয়ন লক্ষ্যমাত্রা (SDG)? | ch15 title |

### Old-sheet structural defects to NOT re-import (fix at the source, in the book)
- ch3 was emitted under TWO chapter titles (`পর্ন` then `পঠন`) — meaning two runs got
  concatenated. The `chapter` value must be byte-identical for all rows of a chapter.
- Bare-fragment topics (head nouns dropped): ch7 `প্রাথমিক/মাধ্যমিক/সাম্প্রতিক পর্যায়`;
  ch8 + ch9 `প্রাকৃতিক/সামাজিক-সাংস্কৃতিক/অর্থনৈতিক/প্রযুক্তিগত নিয়ামক` (identical
  strings in both chapters → not self-identifying); ch1 `পাঠের গুরুত্ব`; ch15
  `চ্যালেঞ্জ মোকাবিলায় করণীয় পদক্ষেপ`.
- Over-fragmentation (ch3 ~104 rows): dozens of `মানচিত্রে X` skill/duplicate rows
  (`দূরত্ব মাপা/নির্ণয়/পরিমাপ`, `সময়/সময় পার্থক্য/সময়কাল/সময় সংক্রান্ত`, `ক্ষেত্রফল` +
  `ক্ষেত্রফল মাপার প্রতীক`, `সরলরেখা` + `সরলরেখা ও বক্ররেখা`, GPS/GIS split into 5
  rows). These belong merged or as a scope note.
- Cause+effect emitted both combined AND split: `ভূমিকম্পের কারণ ও প্রভাব` next to
  `ভূমিকম্পের প্রধান কারণ/অপ্রধান কারণ/ফলাফল`; `সমুদ্রস্রোতের কারণ ও প্রভাব` next to
  `সমুদ্রস্রোতের কারণ/প্রভাব`.

## Verified factual points (do NOT let OCR/paraphrase drift here)
- None confirmed against the printed book yet — the sheet above is unverified.
  Before writing `topic_map.json`, confirm the book's actual chapter structure on
  the TOC (see the handoff note about the PDF outline showing `Forma 1–29` vs the
  sheet's 15 অধ্যায় — the book may be organized differently than the sheet).

## Chapters where numbering restarts per unit
Unknown pending TOC read; earlier sheets used a plain 1–15 running order. Confirm
on the সূচিপত্র; if the book uses a different grouping (e.g. per-Forma units), use
a running integer for `chapter_no` and note the unit in `chapter_title`.