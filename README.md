# NCTB Topic Mapping

Extract a **topic map per chapter** from scanned NCTB (National Curriculum and
Textbook Board, Bangladesh) textbooks. For every chapter, produce atomized topics
as a CSV file ready for Google Sheets import.

**This README is the complete spec.** Any LLM or agent picking this up should be
able to execute the full pipeline end-to-end from here alone.

### For an agent: how to run this

The pipeline is 6 steps (§5 runbook). Five are shell scripts you just run; **one
is you** — Step 3/Step 7, where you read the chapter page images and write
`topic_map.json`. That step is fully specified in §7 below (read every page of a
chapter in order, list the body section headings, apply §3.2/§3.5). Between every
step run `python scripts/05_validate.py --stage <extract|topicmap|final>` — it
exits nonzero on any FAIL and names the exact chapter/topic to fix, so you never
have to eyeball for the known failure modes. Windows: prefix every python call
with `PYTHONIOENCODING=utf-8`. **Finance and Banking** (`subjects/finance-and-banking.md`,
`config/finance-and-banking.json`, 13 chapters / 129 topics, all stages green) is
a complete worked example — copy its shape.

---

## 1. Project Goal

Given a scanned Bengali textbook PDF (no text layer), produce a CSV file where
each row is ONE atomized topic:

```csv
"grade","subject","chapter","topic"
"9-10","science","অধ্যায় ১: উন্নততর জীবনধারা","খাদ্য উপাদান"
"9-10","science","অধ্যায় ১: উন্নততর জীবনধারা","আদর্শ খাদ্য পিরামিড"
```

---

## 2. Inputs

- **~15+ NCTB textbooks**, whole curriculum (multiple classes / subjects).
- Each book is **200–300 pages**, **scanned images** (no text layer), **Bengali**
  (some English in science/math).
- Source PDFs live in `books/`, named descriptively
  (e.g. `Secondary (BV)-2026_Class 9-10_Science_compressed.pdf`).

**Before OCR:** check <https://nctb.gov.bd> and official e-textbook portals for
**digital-version PDFs that already have a text layer** (try selecting text in a
viewer). If found for a book, skip OCR — go straight to `pdftotext`.

---

## 3. Output Format

### 3.1 Final deliverable — `output/<book-name>.csv`

**One row per atomized topic.** CSV columns:

| column | description | example |
|---|---|---|
| `grade` | Class/grade level | `9-10` |
| `subject` | Subject name (English lowercase) | `science` |
| `chapter` | Bengali chapter label | `অধ্যায় ১: উন্নততর জীবনধারা` |
| `topic` | Single atomized topic (Bengali noun phrase), scope detail removed | `খাদ্য উপাদান` |
| `scope_note` | sub-items lifted from a trailing `(...)` in the label; **blank for most rows** | `জমি নির্বাচন, জাত, রোপণ, পরিচর্যা, ফসল সংগ্রহ` |
| `topic_raw` | the `topic` exactly as Step 8/9 produced it, before the scope-note split; **equals `topic` when there was no `(...)`** | `ধান চাষপদ্ধতি (জমি নির্বাচন, জাত, রোপণ, পরিচর্যা, ফসল সংগ্রহ)` |

**All six columns are standard** — **Step 10** (§4) runs for every book, and
`config/_TEMPLATE.json` ships `scope_split.enabled = true`. A book whose subject
config sets `"enabled": false` (or has no config file) stays at the four core
columns; everything else is 6-column with `scope_note` empty and
`topic_raw == topic` on rows that had no parenthetical. `--stage final` compares
`topic_raw` against `topic_map.json`, so the split never trips the silent-drop
check (§3.6, §4 Step 10).

### 3.2 Topic rules

**A topic must be a self-contained concept name that still makes sense with the
`chapter` and `subject` columns hidden.** `নীতিমালা`, `সমস্যা`, `চুক্তিপত্র`,
`গঠন প্রক্রিয়া`, `উপযুক্ত ক্ষেত্র`, `দূষণের প্রভাব` are **rejects** — they are bare
attribute nouns with no head concept.

- **Keep the head noun.** Every topic carries the concept it is about:
  `সমবায় সমিতির নীতিমালা`, not `নীতিমালা`; `আত্মকর্মসংস্থানের উপযুক্ত ও লাভজনক ক্ষেত্র`,
  not `উপযুক্ত ক্ষেত্র`; `অংশীদারি ব্যবসায়ের চুক্তিপত্র`, not `চুক্তিপত্র`.
- **Never orphan a fragment when splitting.** When one learning outcome or heading
  reads `<head> <A> ও <B>`, both rows must repeat `<head>`:
  `সমবায় সমিতির গঠন` + `সমবায় সমিতির নীতিমালা` — never `সমবায় সমিতির গঠন` + `নীতিমালা`.
  If repeating the head is awkward, keep it as one row: `সমবায় সমিতির গঠন ও নীতিমালা`.
- **Do not drop meaning-changing qualifiers.** `ব্যবসায়ের কারণে সৃষ্ট বায়ু দূষণ`,
  not `বায়ু দূষণ`; `ব্যবসায়ের উপর পরিবেশের উপাদানের প্রভাব`, not `পরিবেশের উপাদান`
  (which reads as science, not business). Only strip qualifiers that add nothing
  (`বিভিন্ন`, `উল্লেখযোগ্য`, `এই অধ্যায়ের`).
- Strip pedagogy verbs only: ব্যাখ্যা করতে পারব, বর্ণনা করতে পারব, বিশ্লেষণ করতে পারব,
  বলতে পারব, চিহ্নিত করতে পারব, শনাক্ত করতে পারব, তৈরি করতে পারব, করতে পারব, পারব, করব, বলব.
  Stripping the verb must never leave a dangling fragment (see above).
- Split a compound topic **only when each part keeps its own head noun** after the
  split. Split points: standalone এবং, space-surrounded ও (never ও inside words like
  হওয়া), and commas between parallel noun phrases. Never split `X-এর ধারণা,
  বৈশিষ্ট্য ও গুরুত্ব` into three near-duplicate rows — that is a merge target (§3.5),
  not a split.
- Remove experimental/verification items entirely: পরীক্ষণ, শনাক্তকরণ, অনুসন্ধান, প্রয়োগ, প্রদর্শন, পরীক্ষা, স্লাইড, প্রস্থচ্ছেদ.
- Keep only noun concepts (Bengali noun phrases). Preserve English/technical terms as-is.
- All CSV fields are quoted (`csv.QUOTE_ALL`) to prevent commas in Bengali text from breaking structure.

### 3.3 Example chapter names across subjects

**Science (Class 9-10):**
```
অধ্যায় ১: উন্নততর জীবনধারা
অধ্যায় ২: জীবনের জন্য পানি
অধ্যায় ৩: হৃদযন্ত্রের যত কথা
অধ্যায় ৪: নবজীবনের সূচনা
অধ্যায় ৫: দেখতে হলে আলো চাই
অধ্যায় ৬: পলিমার
অধ্যায় ৭: অম্ল, ক্ষারক ও লবণের ব্যবহার
অধ্যায় ৮: আমাদের সম্পদ
অধ্যায় ৯: দুর্যোগের সাথে বসবাস
অধ্যায় ১০: এসো বলকে জানি
অধ্যায় ১১: প্রাতিহাসিক জীবনে তড়িৎ
```

**Physics (Class 9-10):**
```
অধ্যায় ১: পারিপার্শ্বিক পদার্থবিজ্ঞান
অধ্যায় ২: ভেক্টর
অধ্যায় ৩: গতিবিদ্যা
অধ্যায় ৪: নিউটনীয় বলবিদ্যা
অধ্যায় ৫: কাজ, শক্তি ও ক্ষমতা
অধ্যায় ৬: মহাকর্ষ ও অভিকর্ষ
অধ্যায় ৭: পৃথিবীর ঘূর্ণন
অধ্যায় ৮: তাপগতিবিদ্যা
অধ্যায় ৯: স্থির তড়িৎ
অধ্যায় ১০: চলতড়িৎ
অধ্যায় ১১: তড়িৎ প্রবাহের চৌম্বক ক্রিয়া
অধ্যায় ১২: তরঙ্গ
অধ্যায় ১৩: শব্দ
অধ্যায় ১৪: আলো
অধ্যায় ১৫: আলোর প্রতিসরণ
অধ্যায় ১৬: লেন্স ও দর্পণ
অধ্যায় ১৭: পরমাণু ও নিউক্লিয়াস
অধ্যায় ১৮: পারমাণবিক পদার্থবিজ্ঞান
অধ্যায় ১৯: অর্ধপরিবাহী ও ইলেকট্রনিক্স
```

**Mathematics (Class 9-10):**
```
অধ্যায় ১: বাস্তব সংখ্যা ও বীজগণিত
অধ্যায় ২: সমীকরণ
অধ্যায় ৩: সমান্তর ও গুণোত্তর ধারা
অধ্যায় ৪: সূচক ও লগারিদম
অধ্যায় ৫: সমতলীয় জ্যামিতি
অধ্যায় ৬: স্থানাঙ্ক জ্যামিতি
অধ্যায় ৭: ত্রিকোণমিতি
অধ্যায় ৮: সম্ভাবনা
অধ্যায় ৯: পরিসংখ্যান
```

**Bangladesh and Global Studies (Class 9-10):**
```
অধ্যায় ১: বাংলাদেশের মুক্তিযুদ্ধ
অধ্যায় ২: গণতন্ত্রের ধারণা ও বাস্তবায়ন
অধ্যায় ৩: সরকার ব্যবস্থাপনা
অধ্যায় ৪: অর্থনৈতিক উন্নয়ন
অধ্যায় ৫: ভূগোল ও পরিবেশ
```

### 3.4 Intermediate JSON — `ocr/<book-name>/topic_map.json`

Array of chapter objects, this exact schema:

```json
[
  {
    "class": "9-10",
    "subject": "science",
    "chapter_no": 1,
    "chapter_title": "উন্নততর জীবনধারা",
    "learning_outcomes": ["খাদ্য উপাদান ও আদর্শ খাদ্য পিরামিড ব্যাখ্যা করতে পারব"],
    "topics": ["খাদ্য উপাদান", "আদর্শ খাদ্য পিরামিড"],
    "keywords": ["পুষ্টি", "কার্বোহাইড্রেট"],
    "one_line_summary": "খাদ্যের উপাদান ও পুষ্টির গুরুত্ব।",
    "source_pages": "6-37"
  }
]
```

### 3.5 Topic granularity (merge rule — single source of truth)

Target: **each row = one 15–30 minute study / quiz topic.** This rule governs both
Step 7 (produce topics at this granularity directly) and Step 9 (merge if Step 7
over-fragmented). It supersedes any other wording in the `prompts/` files.

- **MERGE** the basic sub-aspects of the *same* concept into one row:
  `X-এর ধারণা` + `X-এর বৈশিষ্ট্য` + `X-এর গুরুত্ব` → `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব`.
- **MERGE** natural pairs: `X-এর ধারণা` + `X-এর প্রকারভেদ` → `X-এর ধারণা ও প্রকারভেদ`.
- **MERGE** multi-line biographies/institutions: `[A]-এর জীবনী` + `[A] প্রতিষ্ঠিত সংস্থা`
  + `[A]-এর শিক্ষণীয় দিক` → `[A]-এর জীবনী, প্রতিষ্ঠিত সংস্থা ও শিক্ষণীয় দিক`.
- **KEEP SEPARATE** distinct concepts (`একমালিকানা ব্যবসায়` ≠ `অংশীদারি ব্যবসায়`),
  direct opposites (`সুবিধা` ≠ `অসুবিধা`), and different entities
  (`পাবলিক কোম্পানি` ≠ `প্রাইভেট কোম্পানি`).
- The merged label must name the head concept once and list its aspects — never a
  bare `ধারণা, বৈশিষ্ট্য ও গুরুত্ব`.

### 3.6 Topic label length & scope notes (single source of truth)

`topic` is a **label**, not a description. Target **3–8 words**; `05_validate.py
--stage final` WARNs above **12**. Short is fine when it is precise
(`কৃষি ঋণ ব্যবস্থাপনা`, `পুইশাক চাষপদ্ধতি`) — there is **no minimum**, and padding a
label to reach one is worse than a 2-word label. This is a style guard: WARN
only, never a gate.

**A trailing `(a, b, c …)` enumeration is a scope note, not part of the label.**
`ধান চাষপদ্ধতি (জমি নির্বাচন, জাত, রোপণ, পরিচর্যা, ফসল সংগ্রহ)` is one topic whose
label is `ধান চাষপদ্ধতি`; the parenthetical is *what it covers*. **Step 10**
(§4) moves it into the `scope_note` column and keeps the untouched original in
`topic_raw`. The scope note has **no length limit**. This is the pipeline
default — `scope_split` is enabled in every subject config.

**When a body heading names a concept and then lists instances/parts, pick by
how many and how heavy:**

| items | do this | result |
|---|---|---|
| 3 or more, or a step list | write `label (a, b, c …)` in `topics[]`; Step 10 lifts it to `scope_note` | `topic` = `label`, `scope_note` = `a, b, c` |
| 1–2 that fold into a phrase | write one flowing label, no brackets | `যানবাহন ও পাহাড়ি রাস্তায় উত্তল দর্পণের ব্যবহার` |
| examples that add nothing | drop them | `উত্তল দর্পণের ব্যবহার` |
| each item is itself a full topic taught in its own right | split into sibling rows in Step 7, head noun repeated on each — **not** a Step 10 job | `উত্তল দর্পণ: যানবাহনের পশ্চাৎ দৃশ্য` + `উত্তল দর্পণ: পাহাড়ি বাঁক` |

- The `scope_note` route is the safe default: nothing is lost, labels stay
  uniform, and `topic_raw` keeps the original for the silent-drop check. Reach
  for a flowing label or a drop only for the small trivial cases above.
- Sub-items may also (or instead) go in the chapter's `keywords[]`.
- An **inline** parenthetical the sentence continues past — `FCR (খাদ্য রূপান্তর
  হার) ও মাছের সম্পূরক খাদ্য তৈরি` — is a gloss, not a scope note. Step 10 leaves
  it alone: it only moves a `(...)` that *closes* the string.

---

## 4. Pipeline (run per book)

> **The validation gate.** `scripts/05_validate.py` has three stages —
> `--stage extract`, `--stage topicmap`, `--stage final` — run after Steps 2, 7
> and 9. Each exits nonzero on any FAIL, so a batch run stops at the first broken
> book instead of producing 15 bad CSVs. It catches every failure mode this
> project has hit: box-only extraction, topics that are verb-stripped learning
> outcomes, one-word / bare-attribute topics, orphaned `ও`/`এবং` fragments,
> ASCII chapter digits, topics silently dropped between `topic_map.json` and
> the CSV, box-only `topic_map.json` (narrow `source_pages`), and OCR reading
> errors in topic labels (lexical check). Never hand-inspect for these — run the
> gate.

> **2026-08-28 — OCR reading-error hardening** (after Science shipped `পাকশল্লি`
> for `পাকস্থলী`, `সংগ্রহলন` for `সঞ্চালন`, a whole chapter of `প্রাত্যহিক`
> forced to `প্রাতিষ্ঠানিক`, etc.). *How it happened:* the 2-page শিখনফল box was
> OCR'd instead of the chapter body, the two were never reconciled, and
> `config` "corrections" were guessed from the garble instead of read off the
> page. *Fixes:* (1) `--stage topicmap` now FAILs a box-only `topic_map.json`
> and runs a Bengali-dictionary lexical check on every topic word (§Step 7 →
> "Lexical check"); (2) `spelling_corrections` are token-boundary-aware
> (`_config.apply_corrections`) and every entry must cite a PDF page; new
> `config` key `lexicon_extra.words` for valid terms the dictionary flags;
> (3) Step 7.2 takes spelling from the **body heading**, not the box; the
> runbook deletes a box-only map and rebuilds it rather than editing it;
> (4) known Science defects are listed in `subjects/science.md`.

### Step 0 — Subject profile (once per subject)

Copy `subjects/_TEMPLATE.md` to `subjects/<subject>.md` and fill it from 2–3
chapters: what a valid topic looks like in this subject (physics → quantity /
law / phenomenon; geography → process / landform / pattern; civics → concept /
institution / right-duty; …), the head-noun rule, the distinct concept pairs the
merge must never collapse, and the canonical spelling of technical terms the OCR
garbles. This file is prepended to the Step 7 prompt so the model maps as a
subject reader, not a generic text splitter. `subjects/accounting.md` is a
worked example.

Also create `config/<subject>.json` from `config/_TEMPLATE.json` (see §6).

### Step 1 — Chapter index

Open the সূচিপত্র (table of contents). Create `chapter-maps/<slug>.csv`
(`<slug>` = `class9-10-<subject>`, e.g. `class9-10-finance-and-banking.csv`):

```csv
chapter_no,chapter_title,start_page,end_page
1,উন্নততর জীবনধারা,6,37
2,জীবনের জন্য পানি,38,61
```

- `start_page`/`end_page` are **PDF page numbers, NOT printed page numbers.** The
  সূচিপত্র lists printed numbers; the front matter (cover, title, preface, TOC)
  shifts them by a fixed offset `k`.
- **Verify `k` before trusting the map.** Dump the first ~12 pages as images and
  look at them:
  ```bash
  python -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); [d[i].get_pixmap(dpi=150).save(f'p{i+1:03d}.png') for i in range(min(12,d.page_count))]" "books/<pdf>.pdf"
  ```
  Find the PDF page that is the chapter-1 opener (প্রথম অধ্যায় + শিখনফল box). If
  that is PDF page 6 and it prints as page 1, then `k = 5`: every
  `start_page`/`end_page` in the map = printed number + 5. Spot-check `k` again at
  the last chapter's opener — the front-matter offset is usually constant, but
  confirm.
- Some NCTB books restart chapter numbering per unit; use a running integer for
  `chapter_no` and note the unit in `chapter_title`.
- If the TOC title and the chapter-opener title differ (OCR or edition drift),
  use the **opener page** spelling in the map.

### Step 2 — Extract images (for scanned books)

```bash
python scripts/01_extract_images.py "<pdf-name>.pdf" "class9-10-<subject>.csv"
python scripts/05_validate.py --stage extract "<book-name>"      # must PASS
```

It extracts the **FULL chapter page range** (`start_page`..`end_page` from
`chapter-maps/<slug>.csv`) into `ocr/<book-name>/chapters/chNN/` (one folder per
chapter, `page_###.png` named by PDF page number), and **exits nonzero** if any
chapter got fewer pages than its range. `--max-pages N` is refused unless you
also pass `--force` — it reproduces the box-only bug and is debug-only.

`05_validate.py --stage extract` FAILs every chapter where
`pages_extracted < end_page − start_page + 1`.

#### Why the FULL body, not just the শিখনফল box (pages 1–2)

**The শিখনফল box is a list of ~5–8 competency statements, not the chapter's topic
list.** It says what a student should be *able to do* ("...বিশ্লেষণ করতে পারব"),
and one bullet routinely spans 3–5 body sections. It is a **cross-check**, never
the source. Mapping from it alone produces three defects, every time:

1. **Missing topics.** Every section / sub-section heading (১.১, ১.২, ১.৩ …) the
   box does not name simply disappears — often the highest-yield exam terms
   (`প্রাপ্য বিল বাট্টাকরণ`, `নিকাশ ঘর`, `Lender of Last Resort`, `DPS`, `RFCD`).
2. **Context-free fragments.** To cover a broad bullet the model shatters it into
   bare nouns (`নীতিমালা`, `পার্থক্য`, `প্রয়োগ`) — §3.2 rejects.
3. **Verb-stripped paraphrase.** `topics` ends up being the outcome bullets with
   "করতে পারব" chopped off. `05_validate.py --stage topicmap` FAILs this at
   ≥75%.

Evidence — **Finance and Banking**, done both ways: the 13 boxes hold ≈70 bullets
total; reading the full bodies produced **129 topics**. Roughly half the content
is not derivable from any box:

| chapter | box bullets | body topics | what the box hides |
|---|---|---|---|
| ch11 ব্যাংকের আমানত | 5 | 15 | "হিসাবের ধরন বিশ্লেষণ" = 9 account types + ATM/mobile/SMS/internet/any-branch |
| ch13 কেন্দ্রীয় ব্যাংক | 6 | 12 | "কার্যাবলি বিশ্লেষণ" = নিকাশ ঘর, শেষ আশ্রয়স্থল, ঋণ নিয়ন্ত্রণ পদ্ধতি, বিভাগসমূহ |
| ch3 শেয়ার/বন্ড | 6 | 11 | বিলম্বিত/রাইট/বোনাস শেয়ার, স্টক এক্সচেঞ্জ সূচক, প্রাথমিক/সেকেন্ডারি বাজার |

The 4 books still in `ocr/` box-only (Science, Accounting, Business
Entrepreneurship, ICT) are the counter-example: their `topic_map.json` reads as
outcome bullets with verbs removed, and `--stage final` shows chapter-defining
concepts (`মূলধন ও মুনাফা জাতীয় লেনদেনের পার্থক্য`) never reached the CSV.

Extraction speed is not a reason to skip the body: reading ~130 chapter images
once is far cheaper than shipping a wrong CSV and redoing it. NCTB OCR is
reliable on the large clean type of headings, which is exactly what Step 7 reads.

### Step 3 — Detect if OCR is needed

```bash
pdftotext -f 20 -l 25 "books/class6-science.pdf" - | wc -c
```

- Output has real Bengali text → **text layer exists**, skip to Step 5.
- Output empty / garbage → **scanned**, continue to Step 4.

### Step 4 — OCR (scanned books only)

**Primary:** OCRmyPDF (wraps Tesseract 5 LSTM)

```bash
pip install ocrmypdf  # install once, plus Tesseract with Bengali data
ocrmypdf --deskew --clean --language ben \
  "books/class6-science.pdf" "ocr/class6-science/ocr.pdf"
pdftotext "ocr/class6-science/ocr.pdf" "ocr/class6-science/full.txt"
```

**Fallback:** [Surya OCR](https://github.com/VikParuchuri/surya) on Kaggle GPU
(30 GPU-hrs/week free) or Google Colab.

**For this project:** pymupdf extracts images, then LLM reads them directly (vision mode).

### Step 5 — Post-OCR cleanup

`scripts/02_clean.py` on `full.txt`:

- Join lines broken mid-sentence; keep paragraph breaks.
- De-hyphenate line-end splits.
- Find/replace recurring Bengali OCR misreads (`scripts/ocr_fixes.json`).
- Normalize Unicode (NFC).

### Step 6 — Slice into chapters

`scripts/03_slice_chapters.py` using `chapter-maps/<book-name>.csv`:

```bash
python scripts/03_slice_chapters.py "<book-name>"
```

Output: `ocr/<book-name>/chapters/ch01.txt` ... per chapter.

### Step 7 — Topic mapping (this is the agent's job, not a script)

**Source of topics = the chapter body** — every section / sub-section heading
plus the concepts those sections actually teach, read across the FULL chapter.
The শিখনফল box is a cross-check only (§Step 2). Do this once per chapter, in
order, then write one JSON file for the whole book.

**Inputs you load per chapter:** all PNGs in `ocr/<book-name>/chapters/chNN/`, in
filename order (they are named `page_###.png` by PDF page number). Also load
`subjects/<subject>.md` (Step 0) and `prompts/topic_map_prompt.md` — the prompt
is the canonical wording; this list is the procedure.

1. **Read every page of the chapter, in order.** Do not skip pages. The last 1–3
   pages are usually নমুনা প্রশ্ন (sample questions) — skim, don't map them.
2. **List the body headings** — every দ্বিতীয়/তৃতীয় স্তরের শিরোনাম (e.g. `২.৩`,
   `২.৩.১`) verbatim, in order of appearance, plus any boxed classification
   charts. **Take the spelling from the body heading, not the box** — running
   body type OCRs cleaner than the small dense শিখনফল box. Where they disagree,
   open the page and read it. Only record a fix in `config/<subject>.json` →
   `spelling_corrections` after confirming it against the page image, and note
   the PDF page beside the entry. Never invent the "right" spelling from the
   garble alone — that is how Science shipped `প্রাত্যহিক` as `প্রাতিষ্ঠানিক`
   and `রক্ত সঞ্চালন` as `রক্ত সংগ্রহলন`.
3. **Turn each heading into a self-contained topic (§3.2).** It must read
   correctly with the `chapter`/`subject` columns hidden. A bare attribute
   heading (`নীতিমালা`, `সমস্যা`, `উৎস`, `কার্যাবলি`) gets the enclosing
   section's concept prefixed: `অর্থায়নের উৎস`, not `উৎস`;
   `বাণিজ্যিক ব্যাংকের কার্যাবলি`, not `কার্যাবলি`. Keep meaning-changing
   qualifiers; keep English/technical terms as-is; never leave a one-word topic.
4. **Set granularity per §3.5.** Emit topics already at 15–30 min study size.
   Merge the basic sub-aspects of one concept (`X-এর ধারণা` + `X-এর বৈশিষ্ট্য` +
   `X-এর গুরুত্ব` → one row). Keep distinct concepts, opposites, and different
   entities separate (use `subjects/<subject>.md` → distinct pairs). A 10–15 page
   chapter typically yields 8–15 topics; ~5 or ~30 both mean the granularity is
   off.
5. **Filter experimental/lab items** (§3.2: পরীক্ষণ, স্লাইড, প্রস্থচ্ছেদ, …).
   This is the ONLY place lab items are filtered — `06_assemble.py` no longer
   keyword-drops.
6. **Cross-check against the box.** Every শিখনফল bullet must map to ≥1 topic. If
   one doesn't, you skipped a section — go back to the body pages and find it. Do
   **not** satisfy the check by pasting the verb-stripped bullet.
7. **Write `ocr/<book-name>/topic_map.json`** — the §3.4 schema, one object per
   chapter, in chapter order. `learning_outcomes` = the box bullets verbatim with
   verbs KEPT; `topics` = per steps 3–6, and NOT a verb-stripped copy of
   `learning_outcomes`. `source_pages` = the actual PDF page range you read.
   `chapter_no` set on every object. `keywords` 5–15 revision terms.

If a chapter's body was not extracted, set `"needs_review": true` on it and don't
map — fix Step 2 first.

```bash
python scripts/05_validate.py --stage topicmap "<book-name>"     # must PASS
```

**FAILs on:** one-word / bare-attribute topics; orphaned `ও`/`এবং` fragments;
≥75% of a chapter's `topics` being verb-stripped `learning_outcomes` (box
paraphrase → you did not read the body); `needs_review: true`; a chapter-map
chapter missing from the JSON; `source_pages` spanning ≤3 pages of a ≥5-page
chapter (box-only map — delete it and redo from the body). **WARNs on:** thin
2-token topics (confirm they carry a head noun — often fine); an outcome bullet
no topic covers; 55–74% outcome-tracking (fine when the chapter genuinely has
few sections); **any topic word a Bengali dictionary does not know** (see the
lexical check below). Fix `topic_map.json` and re-run until 0 FAIL — do **not**
proceed to Step 8 with a FAIL or an unresolved lexical WARN.

#### Lexical check — OCR reading errors the structure checks can't see

A garble that is still a plausible-looking Bengali string — `পাকশল্লি` for
`পাকস্থলী`, `সংগ্রহলন` for `সঞ্চালন`, `কোলেষ্টেরল` for `কোলেস্টেরল`,
`তন্ত্র` for `তন্তু` — passes every structural rule. `--stage topicmap` runs
each topic word through a Bengali spellchecker (`hunspell -d bn_BD`, or
`pyenchant`) and WARNs on unknowns. If no checker is installed it prints one
WARN saying so and the check is skipped — **install one** (`hunspell` +
`hunspell-bn` / a `bn_BD` dict, or `pip install pyenchant`), or set
`NCTB_NO_SPELLCHECK=1` to silence the notice and rely on the Step 6 eyeball.

- A WARN is not proof of an error — Bengali dictionaries miss real technical
  terms. **Open the page**, confirm the word, then either fix `topic_map.json`
  or add the confirmed-correct word to `config/<subject>.json` →
  `lexicon_extra.words`.
- This exists because the box-only Science map shipped with `পাকশল্লি`,
  `সংগ্রহলন`, `কোলেষ্টেরল`, `তন্ত্র` (fibre), `নিষ্কাসন` and a whole chapter of
  `প্রাত্যহিক`→`প্রাতিষ্ঠানিক` — none catchable without a lexicon. Root cause:
  the box (small, dense, highlighted type) was OCR'd instead of the body, the
  two were never reconciled, and `config` "corrections" were guessed from the
  garble rather than read off the page. Prevention = the body is the source
  (§Step 2), spelling comes from the body heading (Step 7.2), every `config`
  entry cites a page, and this check gates the map.

### Step 8 — Assemble CSV

`scripts/06_assemble.py` — converts topic_map.json to CSV:

```bash
python scripts/06_assemble.py "<book_name>" "<grade>" "<subject>"
```

Example:
```bash
python scripts/06_assemble.py "Secondary (BV)-2026_Class 9-10_Science_compressed" "9-10" "science"
```

**What it does:**
- Reads `ocr/<book-name>/topic_map.json`
- Applies spelling corrections from `config/<subject>.json` (falls back to
  `scripts/spelling_corrections.json` if no per-subject config yet) via
  `_config.apply_corrections` — token-boundary-aware, so a rule cannot rewrite
  the middle of an unrelated word
- Converts chapter numbers to Bengali numerals (অধ্যায় ১, অধ্যায় ২, ...) —
  **the `chapter` field must read `অধ্যায় ১`, never `অধ্যায় 1`**; ASCII digits in
  the output mean this step did not run
- Writes CSV with `csv.QUOTE_ALL` (all fields quoted)

**`06_assemble.py` does NOT fix bad topics.** Its atomizer only strips a trailing
verb and splits on standalone `এবং` (never on `ও`, never emitting a <2-token
fragment). It cannot re-attach a head noun or undo an over-split. Topics must
already be correct per §3.2 / §3.5 in `topic_map.json`. If the CSV has
context-free rows, fix `topic_map.json` (Step 7) and re-run.

Output: `output/<book-name>.csv`

### Step 9 — Merge similar topics (non-destructive)

```bash
python scripts/08_merge.py "output/<book-name>.csv"
python scripts/05_validate.py --stage final "<book-name>"        # must PASS
```

**Merge target and rules: §3.5 (single source of truth).** Step 7 should already
emit topics at that granularity; Step 9 is the safety net for over-fragmentation.

**What it does — and does NOT do:**
- Applies the explicit per-chapter rules in `config/<subject>.json` →
  `merge_overrides` (`_merge_`, `_drop_`, or a rename target).
- Deduplicates exact-duplicate rows.
- **Never deletes a topic on its own.** The old fuzzy pass silently swallowed
  distinct concepts (`পণ্যের ক্রয়মূল্য নির্ধারণ` merged into `বিক্রয়মূল্য`,
  `নগদ প্রদান জাবেদা` into `নগদ প্রাপ্তি জাবেদা`). Now it only **reports**
  near-duplicate groups to `output/<book-name>-merge-candidates.txt` for you to
  turn into `merge_overrides` and re-run. Opposite pairs (`ক্রয়`/`বিক্রয়`,
  `প্রাপ্তি`/`প্রদান`, and anything in `distinct_pairs`) are never proposed.

`05_validate.py --stage final` then fails if any `topic_map.json` topic is
missing from the CSV without a `merge_overrides` rule — so a real drop can no
longer pass silently.

**Example `merge_overrides` entry** (`config/<subject>.json`):
```json
"অধ্যায় ২: জীবনের জন্য পানি": {
  "পানির ধর্ম": "পানির ধর্ম, গঠন ও উৎস",
  "পানির গঠন": "_merge_",
  "পানির বিভিন্ন উৎস": "_merge_"
}
```

**Prompt files.** `prompts/topic_map_prompt.md` is canonical for Step 7.
For an LLM-driven merge, `prompts/semantic_merge_prompt.md` is canonical and
follows §3.5. The other merge prompts (`chapter_extract_merge.md`,
`conservative_merge_prompt.md`) are **deprecated** — they contradict §3.5 (one
forbids merging ধারণা/প্রকারভেদ/গুরুত্ব, one over-merges) and must not be used.

### Step 10 — Split scope notes (non-destructive) — standard, run for every book

```bash
python scripts/12_scope_split.py "output/<book-name>.csv"
python scripts/05_validate.py --stage final "<book-name>"        # must PASS
```

Rewrites `output/<book-name>.csv` from 4 columns to 6:
`grade,subject,chapter,topic,scope_note,topic_raw` (§3.1, §3.6).

- `topic_raw` = the Step 8/9 label kept **verbatim**. `topic` = that label with a
  **trailing** `(...)` removed. `scope_note` = what was inside it. On a row that
  had no `(...)`, `scope_note` is empty and `topic_raw == topic` — the 6-column
  schema is the same for every book.
- **Non-destructive:** nothing merged, dropped or reworded; every original string
  survives in `topic_raw`, which is what `--stage final` checks for silent drops.
- **Config** — `config/<subject>.json` → `scope_split`
  (`config/_TEMPLATE.json` ships it **enabled**):
  ```json
  "scope_split": { "enabled": true, "max_core_words": 12 }
  ```
  Set `"enabled": false` (or run a subject with no config file) only when you
  have a specific reason to keep that book at the 4 core columns — then the
  script is a no-op. When enabled, `--stage final` WARNs on any `topic` still
  over `max_core_words` or still ending in `(...)`.
- **Idempotent** — re-derives from `topic_raw`. Re-run it after any re-run of
  Steps 8–9. Steps 8–9 themselves always operate on the 4-column CSV
  (`08_merge.py` drops columns 5–6 on read), so the order is
  assemble → merge → scope-split → `--stage final`.

---

## 5. Runbook — new subject, or recheck an existing one

Same checklist for any subject (physics, chemistry, biology, civics, geography,
…). Every `05_validate.py` call exits nonzero on FAIL — do not proceed past one.
`<book>` = the folder name under `ocr/` (the PDF stem, no `.pdf`). `<slug>` =
`class9-10-<subject>`. On Windows prefix python calls with `PYTHONIOENCODING=utf-8`.

```bash
# 0. Subject scaffold (once per subject) — fill both from 2-3 chapters
cp subjects/_TEMPLATE.md  subjects/<subject>.md
cp config/_TEMPLATE.json  config/<subject>.json

# 1. Chapter map: chapter-maps/<slug>.csv  (chapter_no,chapter_title,start_page,end_page)
#    start/end are PDF page numbers = printed number + offset k.
#    Verify k: extract early pages, find the ch-1 opener, spot-check k at the last chapter too (§Step 1).
python scripts/05_validate.py --stage extract "<book>"   # (run again after step 2)

# 2. Extract the FULL page range of every chapter
python scripts/01_extract_images.py "<pdf>.pdf" "<slug>.csv"
python scripts/05_validate.py --stage extract "<book>"   # PASS = every chapter has its whole range

# 3. Topic mapping — THE AGENT DOES THIS (§7). Per chapter, in order:
#    FIRST: rm any existing box-only ocr/<book>/topic_map.json — do not edit it, rebuild it.
#    load every PNG in ocr/<book>/chapters/chNN/  +  subjects/<subject>.md  +  prompts/topic_map_prompt.md
#    -> list body headings (spelling FROM the body, not the box) -> §3.2 head-noun
#    -> §3.5 granularity -> cross-check vs box
#    Write ocr/<book>/topic_map.json (§3.4 schema, one object per chapter).
python scripts/05_validate.py --stage topicmap "<book>"  # fix topic_map.json, re-run till 0 FAIL + 0 unresolved lexical WARN

# 4. Assemble CSV (Bengali numerals, QUOTE_ALL)
python scripts/06_assemble.py "<book>" "<grade>" "<subject>"

# 5. Merge (non-destructive). Review output/<book>-merge-candidates.txt; add the
#    groups that are truly §3.5 merges to config/<subject>.json -> merge_overrides
#    (leave the distinct-concept ones alone), then:
python scripts/08_merge.py "output/<book>.csv"
python scripts/05_validate.py --stage final "<book>"     # PASS = no topic silently dropped, no ASCII digits

# 5b. Scope-note split (standard — scope_split is enabled by default; skipped
#     only for a subject whose config sets enabled=false). Re-run after any
#     re-run of steps 4-5. See §3.6 / §4 Step 10.
python scripts/12_scope_split.py "output/<book>.csv"
python scripts/05_validate.py --stage final "<book>"

# 6. Eyeball 100% of rows once — read each topic against the chapter page it
#    came from, not against the string. A garbled word "corrected" to a
#    near-by real word (সংগ্রহলন -> সংগ্রহের instead of সঞ্চালন) is the trap.
```

**Rechecking an existing book** = run steps 2→6 as-is, **including deleting a
box-only `topic_map.json` and rebuilding it from the body** (step 3). `--stage
extract` tells you if extraction was box-only; `--stage topicmap` now also FAILs
a box-only `topic_map.json` (narrow `source_pages`) and WARNs on OCR-garbled
topic words; `--stage final` tells you which topics the old pipeline dropped.
Editing a box-only map in place is not a recheck — the reading errors are baked
into it (see `subjects/science.md` → "Known errors still in the shipped
box-only CSV").

**Worked example:** `subjects/finance-and-banking.md` + `config/finance-and-banking.json`
→ `ocr/…Finance and Banking…/topic_map.json` (13 chapters, 129 topics) →
`output/…Finance and Banking….csv`, all three stages green. `accounting` is a
second example (config populated; `topic_map.json` still needs its Step 2+7 redo).

---

## 6. Maintenance files

### 6.1 Per-subject config — `config/<subject>.json`

One self-contained file per subject (template: `config/_TEMPLATE.json`, worked
example: `config/accounting.json`). Read by `scripts/_config.py`, which feeds
`06_assemble.py`, `08_merge.py`, `12_scope_split.py`, and `05_validate.py`.
`_comment` keys are ignored everywhere. It replaces the two global files below,
which mixed all subjects into one namespace and hit the JSON duplicate-key bug
(Physics ch.11).

| key | used by | purpose |
|---|---|---|
| `spelling_corrections` | Step 8, validate | `{wrong: right}` find/replace on `chapter_title` + every `topic`, token-boundary-aware (`_config.apply_corrections`: must start on a word boundary, trailing edge free for inflections). **Cite the PDF page for every entry** (see `_spelling_notes` in `config/science.json`). Never invent the target from the garble — read it off the page. |
| `lexicon_extra.words` | validate | valid subject terms a generic Bengali dictionary flags as unknown — silences the `--stage topicmap` lexical WARN for them. Add a word only after confirming it against the page image. |
| `merge_overrides` | Step 9 | per-chapter `{topic: "_merge_" \| "_drop_" \| "<rename>"}`. Chapter key must match the CSV `chapter` field exactly, Bengali numeral included. Keys unique within a chapter. |
| `scope_split` | Step 10, validate | `{enabled, max_core_words}`, **enabled by default** (`config/_TEMPLATE.json`). `12_scope_split.py` moves a trailing `(a, b, …)` from `topic` into `scope_note` and keeps the verbatim original in `topic_raw` (CSV → 6 columns); `--stage final` WARNs on labels over `max_core_words`. Set `enabled:false` only to keep a specific book at the 4 core columns. |
| `distinct_pairs.pairs` | Steps 9, validate | `[[a,b],…]` opposite concepts the merge must never collapse (e.g. `["ক্রয়মূল্য","বিক্রয়মূল্য"]`). |
| `attribute_nouns_extra.words` | validate | subject-specific bare nouns invalid as a standalone topic. |

Legacy `scripts/spelling_corrections.json` and `scripts/merge_overrides.json`
still load as a fallback and are **merged under** the per-subject file, so
migration can be gradual. New subjects: use `config/<subject>.json` only.

### 6.2 OCR fixes — `scripts/ocr_fixes.json`

Recurring OCR misread corrections for `02_clean.py` (text-OCR path only).

---

## 7. Directory layout

```
nctb-topic-mapping/
├── README.md                              # this file — full spec
├── books/                                 # source PDFs (input)
├── chapter-maps/                          # manual TOC index (Step 1)
│   └── class9-10-science.csv
├── subjects/                              # Step 0 — subject profile, fed into the Step 7 prompt
│   ├── _TEMPLATE.md
│   ├── finance-and-banking.md             # worked example (complete)
│   └── accounting.md                      # worked example
├── config/                               # per-subject config (§6.1)
│   ├── _TEMPLATE.json
│   ├── finance-and-banking.json           # worked example (complete)
│   └── accounting.json                    # worked example
├── ocr/                                   # all intermediate artifacts
│   └── <book-name>/
│       ├── chapters/chNN/page_###.png     # extracted page images (FULL range, PDF-page-numbered)
│       └── topic_map.json                 # Step 7 output (agent-written)
├── output/                                # final deliverables
│   ├── <book-name>.csv                    # 6 cols (grade,subject,chapter,topic,scope_note,topic_raw) after Step 10; 4 if scope_split disabled
│   ├── <book-name>-merge-candidates.txt   # Step 9 suggestions (not auto-applied)
│   └── validation-log.txt                 # every 05_validate.py run
├── prompts/
│   ├── topic_map_prompt.md                # CANONICAL — Step 7 extraction
│   ├── semantic_merge_prompt.md           # CANONICAL — LLM merge (follows §3.5)
│   ├── chapter_extract_merge.md           # DEPRECATED — contradicts §3.5
│   └── conservative_merge_prompt.md       # DEPRECATED — contradicts §3.5
└── scripts/
    ├── _config.py                         # shared per-subject config loader + apply_corrections (boundary-aware spelling fixes)
    ├── 01_extract_images.py               # Step 2: image extraction (full-range guard)
    ├── 05_validate.py                     # GATE: --stage extract|topicmap|final (topicmap: box-only + lexical checks)
    ├── 06_assemble.py                     # Step 8: topic_map.json → CSV
    ├── 08_merge.py                        # Step 9: non-destructive merge + overrides
    ├── 12_scope_split.py                  # Step 10: trailing "(enum)" → scope_note column (standard, run every book)
    ├── 09_semantic_merge.py               # Step 9 alt: LLM merge (Gemini API/manual)
    ├── spelling_corrections.json          # LEGACY global fallback (prefer config/<subject>.json)
    └── merge_overrides.json               # LEGACY global fallback (prefer config/<subject>.json)
```

> Scripts `02_clean.py` / `03_slice_chapters.py` / `04_topic_map.py` and
> `ocr_fixes.json` are referenced by the text-OCR path (Steps 5–6) but are not
> present — this repo has run the vision path only. Add them if you do a
> `pdftotext`-based book.

---

## 8. Prompt template

Canonical prompt lives in **`prompts/topic_map_prompt.md`** — edit it there, not
here. It is prepended with **`subjects/<subject>.md`** (Step 0) at run time. It
must enforce, at minimum:

- If fewer than ~60% of the chapter's pages were supplied → output
  `"needs_review": true`, do not map from the box.
- Topics come from the **chapter body headings across all pages**, not the শিখনফল
  box (box = cross-check only).
- Every topic is **self-contained with its head noun** (§3.2): a bare
  `নীতিমালা` / `সমস্যা` / `চুক্তিপত্র` is invalid; qualify it with its parent concept.
- **Never orphan a fragment** when splitting a compound on ও / এবং / comma — each
  part repeats the head noun, or the row stays compound.
- Emit topics **already at §3.5 granularity** — not `ধারণা`/`বৈশিষ্ট্য`/`গুরুত্ব`
  as separate rows for the same concept.
- **Instances/parts of one concept go in a trailing `(a, b, c …)`** (§3.6), not
  in a 13+ word label — Step 10 lifts it to `scope_note`. Inline glosses stay.
- Output is the §3.4 JSON; `topics` is not a verb-stripped copy of
  `learning_outcomes`.

---

## 9. Cost / budget (all 15 books, ~3,750 pages)

| Phase | Free path | Paid alternative |
|---|---|---|
| OCR | OCRmyPDF local, or Surya on Kaggle GPU | Google Vision ~$6 total |
| Topic mapping (headings-first) | Claude Code sub / Gemini Flash free tier | API + caching ~$2–3 |
| Topic mapping (full text, all chapters) | Heavy on subscription window | API ~$25–30 |

---

## 10. Quality notes

- Bengali OCR fails most on dense body text with যুক্তাক্ষর (conjuncts); it is
  reliable on **large clean type** — chapter titles, section headings, and
  outcome-box bullets. Headings-first exploits this.
- Printed page numbers ≠ PDF page numbers. Always use PDF page numbers in
  `chapter-maps/`.
- Some NCTB books restart chapter numbering per unit/part — record as
  `chapter_no` = running integer, note the unit in `chapter_title` if needed.
- Science/math chapters mix English terms; keep them as-is in `keywords`.
- **Never split on ও inside words** (e.g. হওয়া contains ও but is not a conjunction).
  Only split on ` ও ` (space-surrounded).
- **The শিখনফল box is a summary, not a topic list.** It has ~6–16 outcome bullets;
  a chapter teaches far more. Building `topics` from the box alone is the single
  biggest source of missing content and of context-free fragments. Read the body.
- **A stripped/split topic must never lose its head noun.** `প্রশিক্ষণের প্রয়োজনীয়তা`
  (whose training?), `উপযুক্ত ক্ষেত্র` (for what?), `বায়ু দূষণ` (as a business
  impact?) are failures — carry the subject of the sentence into the topic.
- **Do not delete qualifiers that change the meaning** — `ব্যবসায়ের কারণে`,
  `ব্যবসায়ের উপর প্রভাব বিস্তারকারী` turn a generic noun into the actual business
  topic; dropping them makes the row look like a different subject.
- Chapter labels in the CSV use **Bengali numerals** (`অধ্যায় ১`). ASCII `অধ্যায় 1`
  = Step 8 numeral conversion silently skipped.

---

## 11. Troubleshooting

Run `05_validate.py` first — it names the failing chapter and topic for most of
these.

| Issue | Fix |
|---|---|
| `--stage extract` FAILs "BOX-ONLY" | Re-run `01_extract_images.py` without `--max-pages`; check `start_page`/`end_page` in the chapter map against the PDF. |
| `--stage topicmap` FAILs "verb-stripped copies of learning_outcomes" | Box paraphrase — you mapped from pages 1–2 only. Confirm `chapters/chNN/` has the full range, then redo Step 7 reading every body page (§Step 2, §7). |
| `--stage extract` PASSes but chapter openers look wrong | Page offset `k` is wrong or drifts. Re-derive `k` from the ch-1 opener and re-check at the last chapter; fix `chapter-maps/<slug>.csv` (§Step 1). |
| `--stage topicmap` FAILs "one-word / bare attribute topic" | Head noun dropped. Fix in `topic_map.json` per §3.2 — prefix the enclosing section's concept. |
| `--stage final` FAILs "topic … NOT in the CSV" | A real drop. Either the topic belongs (fix `06_assemble`/dedupe) or it's a deliberate merge — add the rule to `config/<subject>.json` → `merge_overrides`. |
| `chapter` field shows `অধ্যায় 1` not `অধ্যায় ১` | `--stage final` catches this — re-run `06_assemble.py`. |
| Similar topics not merged | Check `output/<book>-merge-candidates.txt`, add the real groups to `config/<subject>.json` → `merge_overrides`, re-run `08_merge.py`. |
| Opposite concepts merged (`ক্রয়`/`বিক্রয়`) | Add the pair to `config/<subject>.json` → `distinct_pairs`. |
| CSV has broken rows with split Bengali text | Ensure `csv.QUOTE_ALL`; check `spelling_corrections` for comma-containing values. |
| Topics like "য়া" as separate rows | The `ও`-inside-word split bug — `06_assemble` now splits only on standalone `এবং`; check `topic_map.json`. |
| Chapter title wrong (`অ্যাস` for `অম্ল`) | Add to `config/<subject>.json` → `spelling_corrections`, verify against the scan first. |
| `topic_map.json` has wrong chapter title | Fix directly in `topic_map.json`, re-run Step 8. |
| UnicodeEncodeError on Windows | Set `PYTHONIOENCODING=utf-8`; CSVs are `utf-8-sig` regardless — cosmetic. |
| Topic looks like the wrong subject (`পরিবেশের উপাদান` in a business book) | Meaning-changing qualifier stripped — restore it in `topic_map.json` (§3.2). |

---

## 12. Glossary

| Bengali | Meaning |
|---|---|
| সূচিপত্র | table of contents |
| অধ্যায় | chapter |
| শিখনফল | learning outcomes |
| এই অধ্যায় শেষে শিক্ষার্থীরা যা শিখতে পারবে | "what students will be able to do by the end of this chapter" |
| যুক্তাক্ষর | Bengali conjunct letters (OCR-hard) |
| দাঁড়ি ( । ) | Bengali full stop |
| NCTB | National Curriculum and Textbook Board |

---

## 13. Status

- [x] Sample book processed (Class 9-10 Science, 11 chapters, 149 topics)
- [x] Pipeline validated: extract → LLM read → assemble → merge → CSV
- [x] **Validation gate** (`05_validate.py --stage extract|topicmap|final`) — 2026-08
- [x] **Per-subject config** (`config/<subject>.json`, `subjects/<subject>.md`,
      `scripts/_config.py`) replacing the global JSON files — 2026-08
- [x] **Non-destructive merge** (`08_merge.py` reports candidates, never
      auto-drops); `06_assemble.py` no longer keyword-drops topics — 2026-08
- [x] **Scope-note split** (`12_scope_split.py`, Step 10) — **pipeline standard**
      (`scope_split` enabled by default in `config/_TEMPLATE.json`, and in the
      agriculture / science / finance-and-banking / accounting configs). A
      trailing `(a, b, …)` in a topic label moves to a `scope_note` column, the
      verbatim original stays in `topic_raw`; every output CSV is 6-column.
      `--stage final` compares `topic_raw` and WARNs on labels > `max_core_words`
      (§3.6). — 2026-08
- [x] **Finance and Banking — DONE from full chapter bodies** (2026-08). 13
      chapters, 129 topics; chapter-map rewritten to PDF pages (printed + 5);
      `subjects/finance-and-banking.md` + `config/finance-and-banking.json`; all
      three validate stages green. Complete worked example for the §5 runbook.
- [x] Accounting: `subjects/accounting.md` + `config/accounting.json` written
      (spelling + distinct pairs); `topic_map.json` still needs its Step 2 + 7 redo.
- [ ] **Re-run the 4 remaining box-only books** (Science, Accounting, Business
      Entrepreneurship, ICT) from full chapter bodies. All fail `--stage extract`
      (2 pages/chapter) and `--stage topicmap` (verb-stripped শিখনফল bullets).
      Run the §5 runbook per book; use Finance and Banking as the template.
- [ ] Write `subjects/<subject>.md` + `config/<subject>.json` for Science,
      Business Entrepreneurship, ICT (accounting done).
- [ ] Batch run remaining classes / subjects
- [ ] Deliver full `output/` with all subjects

### Known-bad in current output (fix on re-run) — `05_validate.py` flags each

- **Accounting** (`--stage final` on the box-only map, before redo): drops
  `মূলধন ও মুনাফা জাতীয় লেনদেনের পার্থক্য` (ch4), `পণ্যের ক্রয়মূল্য নির্ধারণ` (ch11),
  `নগদ প্রদান জাবেদা` (ch6), `দু তরফা দাখিলা পদ্ধতির সুবিধা` (ch3). Misreads now in
  `config/accounting.json`: `দৈত্ব সত্তা`→`দ্বৈত সত্তা`, `চক`→`ছক`, `ক্ষুধন`→`কুঋণ`,
  `নগদ বাক্তি`→`নগদ বাট্টা`, `জেরুর`→`জেরের`. Chapter-map ch12
  `আন্তঃকর্মসংস্থানমূলক` should be `আত্মকর্মসংস্থানমূলক`.
- Chapter labels use ASCII digits (`অধ্যায় 1`) instead of `অধ্যায় ১`.
- Confirmed misreads still to migrate into per-subject configs: `জমিউর ইসলাম`→
  `জহুরুল ইসলাম`, `শিক্ষাদীয়`→`শিক্ষণীয়`, `উত্সাহকরণ`→`উদ্বুদ্ধকরণ`,
  `বর্তনপ্রণালি`→`বণ্টনপ্রণালি`, `বিক্রিয়কতা`→`বিক্রয়িকতা`; `কার্টুমো ছক` unresolved
  (Business Entrepreneurship pp. 78–87).
- Legacy `scripts/merge_overrides.json` Physics ch.11 object has duplicate
  `"ব্যবহার"` / `"কিলো"` keys — migrate to `config/physics.json` when redoing it.
