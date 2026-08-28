# Topic-map extraction prompt (CANONICAL — Step 7)

You are mapping the syllabus of one chapter of a Bangladeshi NCTB school textbook,
from scanned page images (Bengali, some English). OCR-style errors are expected —
infer through minor garbling, never invent content.

**`subjects/<subject>.md` is prepended to this prompt.** It tells you what a valid
topic looks like in this subject, the head-noun rule to apply, the distinct
concept pairs to keep separate, and the canonical spelling of technical terms.
Follow it.

You are given **every page image of one chapter**, in order. Use all of them.

**If you were given fewer than ~60% of the chapter's pages** (page count in
`source_pages` vs the chapter's range), do NOT map from what you have. Output the
JSON with `"needs_review": true`, `topics` empty or minimal, and a note that the
body was not supplied. A topic list built from the শিখনফল box alone is the
single biggest defect this project has — the validator (`05_validate.py
--stage topicmap`) will reject it.

---

## What a "topic" is

A topic is a **self-contained concept name that still makes sense on its own**, with
the chapter name and subject hidden. It is a Bengali noun phrase that names *what is
taught*, carrying the concept it is about.

- GOOD: `সমবায় সমিতির নীতিমালা`, `অংশীদারি ব্যবসায়ের চুক্তিপত্র`,
  `আত্মকর্মসংস্থানের উপযুক্ত ও লাভজনক ক্ষেত্র`, `ব্যবসায়ের কারণে সৃষ্ট বায়ু দূষণ`
- BAD (bare attribute, head noun missing): `নীতিমালা`, `চুক্তিপত্র`, `সমস্যা`,
  `উপযুক্ত ক্ষেত্র`, `গঠন প্রক্রিয়া`, `দূষণের প্রভাব`, `বায়ু দূষণ`
- BAD (meaning-changing qualifier dropped): `পরিবেশের উপাদান` for
  "ব্যবসায়ের উপর প্রভাব বিস্তারকারী পরিবেশের উপাদান" — now reads as science, not business

---

## Procedure

### 1. Read the body, not just the box
The শিখনফল / "এই অধ্যায় পাঠ শেষে আমরা —" box (usually page 1–2) is a **summary of
6–16 outcomes**, not the topic list. Derive topics from the **section and
sub-section headings across the whole chapter** and the concepts each section
actually develops. Use the box only to (a) confirm you missed nothing and (b)
correct the spelling of a garbled heading.

### 2. Collect headings
List every দ্বিতীয়/তৃতীয় স্তরের শিরোনাম verbatim, in order of appearance.

### 3. Attach the head noun
For each heading/concept, write the topic so it carries its parent concept. If a
heading is a bare attribute (`নীতিমালা`, `সমস্যা`, `গঠন প্রক্রিয়া`), prefix the
concept from the enclosing section (`সমবায় সমিতির নীতিমালা`). Keep
meaning-changing qualifiers (`ব্যবসায়ের কারণে`, `ব্যবসায়ের উপর প্রভাব বিস্তারকারী`).
Only drop empty words (`বিভিন্ন`, `উল্লেখযোগ্য`, `এই অধ্যায়ের`).

### 4. Split compounds without orphaning
Split on standalone `এবং`, space-surrounded ` ও ` (never ও inside a word like
হওয়া), or commas between parallel noun phrases — **only if each part keeps its own
head noun after the split**.
- `সমবায় সমিতির গঠন ও নীতিমালা` → `সমবায় সমিতির গঠন` + `সমবায় সমিতির নীতিমালা`
- never → `সমবায় সমিতির গঠন` + `নীতিমালা`
- if repeating the head is clumsy, leave it as one compound row.

### 5. Granularity — one row = one 15–30 min study/quiz topic
Do **not** emit `X-এর ধারণা`, `X-এর বৈশিষ্ট্য`, `X-এর গুরুত্ব` as separate rows for
the same X. Merge into `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব` (name X once, list its
aspects). Merge natural pairs (`ধারণা` + `প্রকারভেদ`). Merge multi-line
biography/institution outcomes into one structured row. Keep distinct concepts,
direct opposites (`সুবিধা` ≠ `অসুবিধা`), and different entities
(`পাবলিক কোম্পানি` ≠ `প্রাইভেট কোম্পানি`) separate.

### 5b. Instances/parts of one concept → scope note, not a longer label
A topic label is a name (target 3–8 words), not a description. When a heading
names a concept and then lists the parts/examples/steps that section covers,
keep the label short and record the list as a **trailing `(a, b, c …)`** — a
later step (`12_scope_split.py`) lifts it into a separate `scope_note` column.
- 3+ items or a step list → `ধান চাষপদ্ধতি (জমি নির্বাচন, জাত, রোপণ, পরিচর্যা, ফসল সংগ্রহ)`
- 1–2 that fold into a phrase → one flowing label, no brackets:
  `যানবাহন ও পাহাড়ি রাস্তায় উত্তল দর্পণের ব্যবহার`
- examples that add nothing → drop them
- each item is itself a full topic taught in its own right → separate rows, head
  noun repeated on each (step 4), not a `(...)`
Do NOT inflate the label to 13+ words to fit the list in. An **inline**
parenthetical the sentence runs past (`FCR (খাদ্য রূপান্তর হার) ও …`) is a gloss —
leave it; it is not a scope note. Sub-items may also go in `keywords`.

### 6. Filter
Drop experimental/lab/verification items: পরীক্ষণ, শনাক্তকরণ, অনুসন্ধান, প্রয়োগ,
প্রদর্শন, পরীক্ষা, স্লাইড, প্রস্থচ্ছেদ, ব্যবহারিক.

### 7. Cross-check against the box
Every outcome bullet must correspond to at least one topic. If one doesn't, you
skipped a section — return to the body and find it. Do **not** satisfy the check by
pasting the verb-stripped bullet.

---

## Output

Return ONLY this JSON object (no commentary, no code fences):

```json
{
  "class": "<e.g. 9-10>",
  "subject": "<english lowercase>",
  "chapter_no": <int>,
  "chapter_title": "<Bengali, OCR-corrected>",
  "learning_outcomes": ["<box bullet verbatim, verbs KEPT>", "..."],
  "topics": ["<self-contained topic per rules above>", "..."],
  "keywords": ["<5–15 revision terms; keep English/technical terms as-is>"],
  "one_line_summary": "<one Bengali sentence>",
  "source_pages": "<pdf start-end>"
}
```

`topics` is NOT a verb-stripped copy of `learning_outcomes`. `learning_outcomes`
keeps its verbs; `topics` follows every rule above.

If you were given only the outcome-box pages and no chapter body, set every topic
you can from the box, add `"needs_review": true`, and note that the body was not
available.

IMAGES: the chapter's pages follow, in order.
