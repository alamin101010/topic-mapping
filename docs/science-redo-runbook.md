# Science (Class 9-10) — body re-run runbook

Hand this file to an LLM agent. It rebuilds `ocr/Secondary (BV)-2026_Class 9-10_Science_compressed/topic_map.json`
from the **chapter body pages** (not the শিখনফল box), regenerates the CSV, and pushes it to the
Google Sheet "Science" tab. Chapters 1-4 heading inventories are already extracted and included
below (verified against page images 2026-08-31) — start from those; do 5-11 from scratch.

---

## 0. Why this exists

`output/Secondary (BV)-2026_Class 9-10_Science_compressed.csv` (== Google Sheet "Science" tab,
117 rows) was built largely from the outcome box, not body headings. Confirmed problems:

- **ch2 "জীবনের জন্য পানি" contains ch8 topics.** Rows `মাটির pH`, `মাটি দূষণের কারণ ও ফলাফল`,
  `মাটি সংরক্ষণ কৌশল`, `খনিজ পদার্থ`, `খনিজ পদার্থের বৈশিষ্ট্য ও ব্যবহার` are verbatim/near dups of
  ch8 rows. ch2 is **water only** (verified: pages cover পানির ধর্ম/উৎস/মানদণ্ড/পুনরাবর্তন/
  বিশুদ্ধকরণ/দূষণ/বৈশ্বিক উষ্ণতা/উৎসে হুমকি/পানি অধিকার). Its real water content is missing.
- **ch4 row `জীবঅভিব্ভের সপক্ষে প্রমাণ`** is OCR garble → `জৈব অভিব্যক্তির সপক্ষে প্রমাণ`
  (verified: that is the printed heading, ch4 p.102).
- **ch10 `স্থিতিস্থাপক জড়তা ও গতিজড়তা`** — wrong term. Inertia of rest is `স্থিতিজড়তা`;
  `স্থিতিস্থাপক` = elastic. Verify on ch10 pages, fix to `স্থিতিজড়তা ও গতিজড়তা`.
- **ch9 `সামুদ্রিক প্রবাল বৃদ্ধি`** — "coral increase" is not a disaster; sits beside
  `সমুদ্রপৃষ্ঠের উচ্চতা বৃদ্ধি`. Likely a misread of জলোচ্ছ্বাস / লবণাক্ততা বৃদ্ধি — verify on page.
- **ch7 `এসিড ছড়ালে শাস্তি`** — `শাস্তি` (punishment) is suspicious; verify against the page
  (may be `এসিড ছিটকে পড়লে করণীয়`, or a real acid-violence-law topic).
- **ch1 `পুষ্টির সমতা`, `খাদ্যের অন্তর্ভুক্তিকরণ`, `প্রধান খাদ্য ও পুষ্টিমূলক ভূমিকা`** — not real
  headings (verified ch1 heading list below). Replace.
- **ch9 `দুর্যোগের ভূমিকম্প / দুর্যোগের ভূমিধস / দুর্যোগের বন্যা / দুর্যোগের খরা`** — ungrammatical
  template prefix. Use plain `ভূমিকম্প`, `বন্যা`, `খরা`, `ভূমিধস` (or `<X> দুর্যোগ`).
- **ch11 `তড়িৎ প্রবাহ` and `বিদ্যুৎ প্রবাহ`** are synonyms → merge to one.
- **ch6 `তন্তু থেকে সুতা তৈরি` + `তন্তু থেকে সুতা তৈরি: স্পিনিং` + `কার্ডিং ও কম্বিং`** — one
  process over-split → merge.
- §3.2 rejects present: ch9 `তাৎক্ষণিক করণীয়`, ch10 `জড়তার ব্যবহারিক অভিজ্ঞতা`,
  ch6 `পরিবেশের ভারসাম্যহীনতা` (loses polymer/plastic head).
- Coverage gaps: ch1 missing খাদ্য পিরামিড is actually present as `সুষম খাদ্য পিরামিড`; ch4 is
  puberty+origin-of-life+evolution (NOT Mendelian genetics — the box has no genetics outcome).

**Definition of done** (README §5.1 + §13):
6-column CSV; `05_validate.py --stage topicmap` and `--stage final` both exit 0 with
`headings/chNN.json` filled for all 11 chapters (NCTB_SKIP_HEADING_GATE unset); no trailing
`(a,b,c)` left inside `topic`; `config/science.json` spelling_corrections/merge_overrides
populated from THIS book with page citations; every topic checked against the page it came from;
Sheet "Science" tab updated.

---

## 1. Environment

- Windows, PowerShell + Git Bash. Prefix every python call with `PYTHONIOENCODING=utf-8`.
- `python` (not `python3`). `gspread` 6.2.1 is installed.
- Book folder: `ocr/Secondary (BV)-2026_Class 9-10_Science_compressed/`
  - `chapters/chNN/page_XXX.png` — the page images (246 total).
  - `headings/` — create `chNN.json` here (Step 3).
  - `topic_map.json` — the box-derived file to REBUILD (delete, don't edit).
- Subject profile: `subjects/science.md` (read it — head-noun rule, distinct-concept pairs,
  canonical spellings with page cites). Config: `config/science.json`.
- Prompt: `prompts/topic_map_prompt.md` (STEP 0 heading inventory, §1b verbatim outcomes,
  §5b scope notes, §8 coverage self-check).
- Orchestrator: `python scripts/run_book.py "Secondary (BV)-2026_Class 9-10_Science_compressed" 9-10 science`
  — runs setup→extract→4b-check→topicmap-check→assemble→merge→scope_split→final and stops at the
  first failed gate. Idempotent; re-run after each manual step.

### Chapter map (PDF page numbers, offset k=5 → printed = img number − 5)

| ch | title (from chapter-maps/class9-10-science.csv) | img range | body pages (rest = নমুনা প্রশ্ন, skip) |
|----|-----------------------------------------------|-----------|-----|
| 1  | উন্নততর জীবনধারা              | 006-037 | 008-035 |
| 2  | জীবনের জন্য পানি              | 038-061 | 040-059 |
| 3  | হৃদযন্ত্রের যত কথা এবং অন্যান্য | 062-089 | 064-087 |
| 4  | নবজীবনের সূচনা                | 090-119 | 092-116 |
| 5  | দেখতে হলে আলো চাই             | 120-133 | 122-131 |
| 6  | পলিমার                        | 134-149 | 136-147 |
| 7  | অম্ল, ক্ষারক ও লবণের ব্যবহার  | 150-173 | 152-171 |
| 8  | আমাদের সম্পদ                  | 170-188 | 176-186  (imgs 170-173 are ch7's tail — ignore; ch8 opener is printed p.169 = img 174) |
| 9  | দুর্যোগের সাথে বসবাস          | 189-216 | 191-214 |
| 10 | এসো বলকে জানি                 | 217-234 | 219-232 |
| 11 | প্রাত্যহিক জীবনে তড়িৎ         | 235-253 | 237-251 |

---

## 2. Cheap page reading (do this first — do NOT read 246 full images one by one)

The `ocr/` folder has no text layer, only PNGs. Reading every page as an image is the costly
part. Instead:

**Option A — local Tesseract (preferred if available):**
```bash
tesseract --version                     # check it exists
tesseract --list-langs | grep -i ben    # need 'ben'; if missing: install tesseract-ocr-ben
# batch OCR every page to text, once:
cd "ocr/Secondary (BV)-2026_Class 9-10_Science_compressed/chapters"
for d in ch*; do for f in "$d"/page_*.png; do
  tesseract "$f" "${f%.png}" -l ben --psm 6 2>/dev/null
done; done
```
Now `page_XXX.txt` sits next to each PNG. Read the **.txt** files (≈10× cheaper than images) to
build the heading list and understand each section.

**Option B — Gemini via the existing service account:** `scripts/11_gemini_auto.py` +
`bright-fastness-397410-e569326fd692.json`. Only if Vision/Gemini is enabled on that GCP project.

**Then, open the actual PNG only for:**
- the শিখনফল box page of each chapter (transcribe outcomes verbatim — Tesseract will mangle them),
- any page whose heading spelling is ambiguous or feeds `config/science.json` spelling_corrections,
- a page where the .txt is too garbled to tell what the section is about.

Expect ~15-30 image reads total instead of ~250. Tesseract Bengali garbles conjuncts, so it is
fine for *structure* (which পরিচ্ছেদ, on which page) but NEVER trust it for a final topic-label
spelling — confirm those against the image.

---

## 3. Step 4b — heading checklist (per chapter, MANDATORY, gates Step 7)

For each chapter NN = 01..11, write `ocr/<book>/headings/chNN.json`:

```json
{
  "chapter": 1,
  "chapter_title": "উন্নততর জীবনধারা",
  "headings": [
    {"page": "page_008", "heading": "১.১ খাদ্য ও পুষ্টি"},
    {"page": "page_008", "heading": "খাদ্যের উপাদান"}
  ]
}
```

Rules: walk pages first-to-last; list every পরিচ্ছেদ `X.Y` line and every named sub-section
(bold/larger font) verbatim, in order, with the page filename it appears on. EXCLUDE: chapter
title, শিখনফল box, `চিত্র X.X:` captions, `কাজ`/`দলগত কাজ`/`একক কাজ` boxes, and the end-of-chapter
নমুনা প্রশ্ন / বহুনির্বাচনি / সৃজনশীল / সংক্ষিপ্ত-উত্তর material.

`scripts/04_extract_headings.py "Secondary (BV)-2026_Class 9-10_Science_compressed"` writes a stub
+ `chNN_info.json` (per-page prompt + image list) for any missing chapter; it never clobbers a
filled `chNN.json`.

### Verified heading inventories for ch1-ch4 (use as-is; confirmed against images 2026-08-31)

**ch1 — উন্নততর জীবনধারা**
```
page_008: ১.১ খাদ্য ও পুষ্টি | খাদ্যের উপাদান
page_009: ১.১.১ শর্করা বা কার্বোহাইড্রেট | উদ্ভিজ্জ উৎস | প্রাণিজ উৎস | পুষ্টিগত গুরুত্ব
page_010: ১.১.২ আমিষ বা প্রোটিন
page_011: ১.১.৩ স্নেহ পদার্থ বা লিপিড | স্নেহ পদার্থের কাজ | অভাবজনিত রোগ ও প্রতিকার
page_012: ১.১.৪ খাদ্যপ্রাণ বা ভিটামিন | স্নেহে দ্রবণীয় ভিটামিন | ভিটামিন A
page_013: ভিটামিন D | ভিটামিন E | পানিতে দ্রবণীয় ভিটামিন | ভিটামিন B কমপ্লেক্স
page_014: ভিটামিন C (অ্যাসকরবিক এসিড)
page_015: ১.১.৫ খনিজ পদার্থ এবং পানি | লৌহ (Fe)
page_016: ক্যালসিয়াম (Ca) | ফসফরাস (P) | পানি (Water)
page_017: শরীরে পানির উৎস | ১.১.৬ রাফেজ বা আঁশ
page_018: রাফেজভুক্ত খাবারের গুরুত্ব | ১.২ বডি মাস ইনডেক্স (BMI) বা দেহের ভরসূচি
page_020: ১.৩ দৈনিক খাবার কেমন হবে
page_021: ১.৩.১ সুষম খাদ্য
page_022: সুষম খাদ্য যেভাবে প্রস্তুত করা হয় | সুষম খাদ্য পিরামিড
page_023: ১.৩.২ উন্নত জীবনযাপনের জন্য খাদ্য উপাদান বাছাই
page_024: ফাস্ট ফুড বা জাঙ্ক ফুড
page_025: ১.৪ খাদ্য সংরক্ষণ | ১.৪.১ খাদ্য সংরক্ষণের বিভিন্ন পদ্ধতি
page_027: ১.৪.২ খাদ্যদ্রব্য সংরক্ষণে রাসায়নিক পদার্থের ব্যবহার ও এর শারীরিক প্রতিক্রিয়া
(then, from earlier verified reads, body continues:)
১.৫ তামাক ও অন্যান্য মাদকদ্রব্য | ১.৫.১ ধূমপানের ক্ষতিকর দিক | ১.৫.২ ধূমপান ও তামাকজাত পদার্থের ব্যবহার নিয়ন্ত্রণে প্রচেষ্টাসমূহ | ১.৬ মাদকাসক্তি | ১.৬.১ মাদকাসক্তির লক্ষণ | ১.৬.২ ড্রাগ আসক্তি নিয়ন্ত্রণ | ১.৭ এইডস (AIDS) | ১.৭.১ AIDS রোগের কারণ | ১.৮ স্বাস্থ্য রক্ষায় শরীরচর্চা এবং বিশ্রাম | মনের বিশ্রাম
  (confirm the ১.৫–১.৮ page numbers by opening pages 028-035.)
```
ch1 outcomes (verbatim, box page_007): খাদ্য উপাদান ও আদর্শ খাদ্য পিরামিড ব্যাখ্যা করতে পারব; খাদ্য
সংরক্ষণের প্রয়োজনীয়তা বর্ণনা করতে পারব; স্বাস্থ্য রক্ষায় প্রাকৃতিক খাদ্য এবং ফাস্ট ফুডের প্রভাব বিশ্লেষণ
করতে পারব; ভিটামিনের উৎস এবং এর অভাবজনিত প্রতিক্রিয়া ব্যাখ্যা করতে পারব; খনিজ লবণের উৎস এবং এর
অভাবজনিত প্রতিক্রিয়া ব্যাখ্যা করতে পারব; পানি ও আঁশযুক্ত খাবারের উপকারিতা বর্ণনা করতে পারব; বডি মাস
ইনডেক্সের প্রয়োজনীয়তা ব্যাখ্যা করতে পারব; খাদ্যে রাসায়নিক পদার্থের ব্যবহার এবং এর শারীরিক প্রতিক্রিয়া
বলতে পারব; শরীরে তামাক ও ড্রাগসের ক্ষতিকর প্রতিক্রিয়া ব্যাখ্যা করতে পারব; এইডস কী ব্যাখ্যা করতে পারব;
শারীরিক ফিটনেস বজায় রাখার কৌশল ব্যাখ্যা করতে পারব

**ch2 — জীবনের জন্য পানি** (WATER ONLY — no soil/mineral)
```
page_040: ২.১ পানি | ২.১.১ পানির ধর্ম | গলনাঙ্ক ও স্ফুটনাঙ্ক | বিদ্যুৎ বা তড়িৎ পরিবাহিতা | পানির গঠন
page_041: ২.১.২ পানির উৎস | বাংলাদেশে মিঠা পানির উৎস
page_042: ২.১.৩ জলজ উদ্ভিদের জন্য পানির প্রয়োজনীয়তা
page_043: ২.১.৪ জলজ প্রাণীর জন্য পানির প্রয়োজনীয়তা | ২.২ পানির মানদণ্ড | বর্ণ ও স্বাদ | ঘোলার পরিমাণ
page_044: তেজস্ক্রিয় পদার্থের উপস্থিতি | ময়লা-আবর্জনা | দ্রবীভূত অক্সিজেন | তাপমাত্রা
page_045: pH | লবণাক্ততা | ২.৩ পানির পুনরাবর্তন ও পরিবেশ সংরক্ষণে পানির ভূমিকা | পানির পুনরাবর্তন
page_046: পরিবেশ সংরক্ষণে পানির ভূমিকা | মানসম্মত পানির প্রয়োজনীয়তা
page_047: ২.৪ পানি বিশুদ্ধকরণ | পরিস্রাবণ | ক্লোরিনেশন
page_048: স্ফুটন | পাতন | ২.৫ বাংলাদেশের পানির উৎস দূষণের কারণ
page_049: ২.৫.১ উদ্ভিদ, প্রাণী এবং মানুষের উপর পানিদূষণের প্রভাব
page_051: ২.৬ বৈশ্বিক উষ্ণতা | ২.৬.১ মিঠা পানিতে বৈশ্বিক উষ্ণতার প্রভাব | সমুদ্রের পানির উচ্চতা বৃদ্ধি
page_052: লবণাক্ততা | বৃষ্টিপাত | ২.৬.২ বাংলাদেশে বৈশ্বিক উষ্ণতার প্রভাব
page_053: ২.৭ বাংলাদেশে পানিদূষণ প্রতিরোধের কৌশল এবং নাগরিকের দায়িত্ব
page_054: জলাভূমি রক্ষা | বৃষ্টির পানি নিয়ন্ত্রণ
page_055: জনসচেতনতা বৃদ্ধি | শিল্পকারখানার বর্জ্যপানির দূষণ প্রতিরোধ
page_056: কৃষিজমি থেকে মাটির ক্ষয়জনিত দূষণ প্রতিরোধ | উন্নয়ন কার্যক্রমে পানির ভূমিকা | ২.৮ বাংলাদেশে পানির উৎসে হুমকি
page_057: নদী দখল | নদীতে বন্যা নিয়ন্ত্রণ বাঁধ নির্মাণ | অপরিকল্পিত বর্জ্য ব্যবস্থাপনা
page_058: পানির গতিপথ পরিবর্তন | পানি একটি মৌলিক অধিকার | পানির উৎস সংরক্ষণ ও উন্নয়ন
page_059: ২.৯ পানিপ্রবাহের সর্বজনীনতা এবং আন্তর্জাতিক নিয়মনীতি | রামসার কনভেনশন | আন্তর্জাতিক নদী কনভেনশন
```

**ch3 — হৃদযন্ত্রের যত কথা এবং অন্যান্য**
```
page_064: ৩.১ রক্ত (Blood) | রক্তের উপাদান ও এদের কাজ
page_065: ৩.১.১ রক্তরস বা প্লাজমা | সিরাম | ৩.১.২ রক্তকোষ
page_066: লোহিত রক্তকোষ | লোহিত কোষের কাজ
page_067: শ্বেত রক্তকোষ বা লিউকোসাইট | (ক) অ্যাগ্রানুলোসাইট
page_068: (খ) গ্রানুলোসাইট | অণুচক্রিকা বা থ্রম্বোসাইট
page_069: ৩.১.৩ রক্তের সাধারণ কাজ
page_070: ৩.১.৪ রক্ত উপাদানের অস্বাভাবিক অবস্থা
page_071: ৩.২ রক্তের গ্রুপ | ৩.২.১ অ্যান্টিজেন এবং অ্যান্টিবডি
page_072: ইউনিভার্সাল ডোনার
page_073: ইউনিভার্সাল অ্যাক্সেপ্টর
page_074: ৩.২.২ Rh ফ্যাক্টর
page_076: ৩.২.৩ রক্তের শ্রেণিবিভাগের গুরুত্ব | রক্তনীতি
page_077: ৩.৩ রক্ত সঞ্চালন | ৩.৩.১ হৃৎপিণ্ড (Heart)
page_078: ধমনি | শিরা
page_079: কৈশিক জালিকা | ৩.৩.২ হৃৎপিণ্ডের কাজ | হার্ট-বিট
page_082: ৩.৩.৩ হার্ট-বিট বা পালসরেট গণনার পদ্ধতি
page_083: ৩.৪ রক্তচাপ | ৩.৪.১ উচ্চ রক্তচাপ
page_084: ৩.৪.২ কোলেস্টেরল
page_085: ৩.৫ হৃদযন্ত্রকে ভালো রাখার উপায়
page_086: ৩.৬ ডায়াবেটিস, বহুমূত্র বা মধুমেহ রোগ | ডায়াবেটিস রোগের লক্ষণ
page_087: ডায়াবেটিস রোগীর পথ্য | ডায়াবেটিস নিয়ন্ত্রণ
```
OCR notes ch3: page_080/084 spell `কোলেস্টেরল` (স্ট, correct); `রক্ত সঞ্চালন` (correct).

**ch4 — নবজীবনের সূচনা**
```
page_092: ৪.১ বয়ঃসন্ধিকাল | ৪.১.১ বয়ঃসন্ধিকালের পরিবর্তনসমূহ    (confirm on img 092-093)
page_094: ৪.১.২ বয়ঃসন্ধিকালে পরিবর্তনের কারণ  (হরমোন: ইস্ট্রোজেন, প্রজেস্টেরন, টেস্টোস্টেরন)
page_096: ৪.১.৩ দৈহিক স্বাস্থ্য ঠিক রাখা
page_097: ৪.১.৪ মানসিক স্বাস্থ্য ঠিক রাখা
page_098: ৪.১.৫ বয়ঃসন্ধিকালীন বিবাহ ও গর্ভধারণ | গর্ভধারণ কী?
page_099: স্বাস্থ্যঝুঁকি | স্বাস্থ্যগত সমস্যা | পারিবারিক সমস্যা | শিক্ষাগত সমস্যা
page_100: আর্থিক সমস্যা | গর্ভপাত কী এবং গর্ভপাতের জটিলতা
page_102: ৪.১.৬ টেস্টটিউব বেবি | ৪.২ সন্তানের লিঙ্গ নির্ধারণ
page_105: ৪.৩ পৃথিবীতে জীবনের উৎপত্তি ও বিকাশ
page_106: ৪.৩.১ জীবনের আবির্ভাব কোথায়, কবে এবং কীভাবে ঘটেছে
page_107: জৈব অভিব্যক্তির সপক্ষে প্রমাণ | ১. অঙ্গসংস্থান সম্পর্কিত প্রমাণ
page_108: (ক) সমসংস্থ অঙ্গ | (খ) সমবৃত্তি অঙ্গ
page_109: (গ) লুপ্তপ্রায় অঙ্গ
page_110: ২. তুলনামূলক শারীরস্থানিক প্রমাণ | ৩. সংযোগকারী জীবন সম্পর্কিত প্রমাণ
page_111: ৪. ভ্রূণতত্ত্বঘটিত প্রমাণ | ৫. জীবাশ্মঘটিত প্রমাণ
page_112: ৬. জীবন্ত জীবাশ্ম
page_113: ৭. আণবিক জীববিজ্ঞান | ৪.৪ জৈব অভিব্যক্তির উপর বিভিন্ন মতবাদ | ৪.৪.১ ল্যামার্কের তত্ত্ব
page_115: ৪.৪.২ ডারউইনবাদ বা ডারউইনের তত্ত্ব
page_116: (ডারউইন: প্রকরণ; যোগ্যতমের জয়; প্রাকৃতিক নির্বাচন; নতুন প্রজাতির উৎপত্তি — isolation/hybridization/polyploidy)
```
ch4 outcomes (verbatim, box page_091): বয়ঃসন্ধিকাল ব্যাখ্যা করতে পারব; বয়ঃসন্ধিকালে শারীরিক
পরিবর্তনের কারণ ব্যাখ্যা করতে পারব; বয়ঃসন্ধিকালের মানসিক ও আচরণিক পরিবর্তনে নিজেকে খাপ খাওয়ানোর
উপায় বর্ণনা করতে পারব; বয়ঃসন্ধিকালে দৈহিক ও মানসিক স্বাস্থ্যরক্ষার কৌশল ব্যাখ্যা করতে পারব;
বয়ঃসন্ধিকালীন বিবাহে স্বাস্থ্যঝুঁকি এবং এর প্রভাব বিশ্লেষণ করতে পারব; টেস্টটিউব বেবির ধারণা ব্যাখ্যা
করতে পারব; লিঙ্গ নির্ধারণের কৌশল ব্যাখ্যা করতে পারব; জীবনের উৎপত্তি এবং জীবজগতে অভিব্যক্তির ধারণা
ব্যাখ্যা করতে পারব; পৃথিবীতে নতুন প্রজাতির উৎপত্তির ধারণা ব্যাখ্যা করতে পারব

Do ch5-ch11 heading inventories the same way from the pages.

---

## 4. Step 7 — rebuild topic_map.json

`rm ocr/<book>/topic_map.json` first (rebuild, don't edit). For each chapter produce one JSON
object; the file is a JSON array of 11 objects in order. Per `prompts/topic_map_prompt.md`:

```json
{
  "class": "9-10",
  "subject": "science",
  "chapter_no": 1,
  "chapter_title": "<Bengali, OCR-corrected>",
  "learning_outcomes": ["<box bullet verbatim, verbs KEPT>", "..."],
  "topics": ["<self-contained topic>", "..."],
  "keywords": ["<5-15 revision terms; keep English/technical as-is>"],
  "one_line_summary": "<one Bengali sentence>",
  "source_pages": "<pdf start-end>"
}
```

Topic rules (README §3.2 / §3.5 / §3.6 + `subjects/science.md`):
- A topic is a self-contained concept name that still makes sense with chapter+subject hidden.
  Attach the head noun: `শর্করার উৎস` not `উৎস`; `পানির ধর্ম` not `ধর্ম`.
- ≤5 words is the goal (3-8 ok). Never drop the head concept to shorten.
- Merge the aspects of one X into one row: `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব` — do NOT emit
  `X-এর ধারণা` / `X-এর বৈশিষ্ট্য` as separate near-duplicate rows.
- Keep distinct concepts / opposites separate (see the `distinct_pairs` list in
  `config/science.json` and `subjects/science.md`: শর্করা≠প্রোটিন≠স্নেহ, দর্পণ≠লেন্স,
  স্থির তড়িৎ≠চলতড়িৎ, মাটি≠খনিজ≠জ্বালানি, তন্তু (fibre, NOT তন্ত্র), ...).
- §5b: when a section names a concept then lists its parts/steps/examples, keep the label short
  and put the list as a trailing `(a, b, c)` — Step 10 lifts it to `scope_note`. Don't inflate
  the label past ~12 words. 1-2 items → fold into a flowing label, no brackets.
- Drop lab/verification items: পরীক্ষণ, শনাক্তকরণ, অনুসন্ধান, প্রয়োগ, প্রদর্শন, পরীক্ষা, স্লাইড,
  প্রস্থচ্ছেদ, ব্যবহারিক অভিজ্ঞতা.
- §1b: `learning_outcomes` = box bullets copied verbatim with verbs; fix only obvious OCR
  spelling; no `X সম্পর্কে জানব` paraphrase; no invented bullets.
- §8 coverage self-check before emitting: every পরিচ্ছেদ / named sub-section in `headings/chNN.json`
  is represented by ≥1 topic; the LAST topic maps to a heading on one of the final pages;
  ≳0.5 topics/page; nothing invented (every topic maps to a heading or an outcome).

Optional: `python scripts/07_constrained_prompt.py "<book>" N` bakes `headings/chNN.json` into a
hard checklist prompt for chapter N.

### Fixes to apply while authoring (verify each against the page):

| chapter | change |
|---|---|
| ch1 | drop `পুষ্টির সমতা`, `পুষ্টির খাদ্যতালিকা`, `খাদ্যের অন্তর্ভুক্তিকরণ`, `প্রধান খাদ্য ও পুষ্টিমূলক ভূমিকা` (not headings). Use: খাদ্য ও পুষ্টির ধারণা; খাদ্যের উপাদান (…); শর্করার উৎস ও পুষ্টিগত গুরুত্ব; খাদ্য ক্যালরি; আমিষের উৎস ও পুষ্টিগত গুরুত্ব; স্নেহ পদার্থের উৎস, কাজ ও অভাবজনিত রোগ; ভিটামিনের শ্রেণিবিভাগ, উৎস ও অভাবজনিত রোগ; খনিজ লবণের উৎস ও অভাবজনিত রোগ (লৌহ, ক্যালসিয়াম, ফসফরাস); দেহে পানির ভূমিকা ও অভাবজনিত সমস্যা; রাফেজ বা আঁশযুক্ত খাবারের উপকারিতা; বডি মাস ইনডেক্স (BMI); সুষম খাদ্য ও সুষম খাদ্য পিরামিড; উন্নত জীবনযাপনের জন্য খাদ্য উপাদান বাছাই; ফাস্ট ফুড ও জাঙ্ক ফুডের প্রভাব; খাদ্য নষ্ট হওয়ার কারণ; খাদ্য সংরক্ষণের পদ্ধতি (শুষ্ককরণ, রেফ্রিজারেশন, ফ্রিজিং, সংরক্ষক দ্রব্য, চিনি-লবণ দ্রবণ); খাদ্য সংরক্ষণে রাসায়নিক পদার্থের ক্ষতিকর প্রতিক্রিয়া; ধূমপান ও তামাকের ক্ষতিকর প্রভাব; মাদকাসক্তির লক্ষণ, কারণ ও নিয়ন্ত্রণ; এইডস ও এইচআইভি সংক্রমণ; এইডস প্রতিরোধ; স্বাস্থ্য রক্ষায় শরীরচর্চা ও বিশ্রাম |
| ch2 | remove all soil/mineral topics. Author from the ch2 heading list above (পানির ভৌত ধর্ম; পানির তড়িৎ পরিবাহিতা; পানির উভধর্মিতা ও pH; পানির আণবিক গঠন; পানির উৎস; বাংলাদেশে মিঠা পানির উৎস; জলজ উদ্ভিদের জন্য পানির প্রয়োজনীয়তা; জলজ প্রাণীর জন্য পানির প্রয়োজনীয়তা; পানির মানদণ্ড (…); পানির পুনরাবর্তন; পরিবেশ সংরক্ষণে পানির ভূমিকা; মানসম্মত পানির প্রয়োজনীয়তা; পানি বিশুদ্ধকরণ পদ্ধতি (পরিস্রাবণ, ক্লোরিনেশন, স্ফুটন, পাতন); বাংলাদেশে পানির উৎস দূষণের কারণ; পানিদূষণের প্রভাব (পানিবাহিত রোগ, ভারী ধাতু); মিঠা পানিতে বৈশ্বিক উষ্ণতার প্রভাব; বাংলাদেশে বৈশ্বিক উষ্ণতার প্রভাব; পানিদূষণ প্রতিরোধের কৌশল ও নাগরিকের দায়িত্ব; উন্নয়ন কার্যক্রমে পানির ভূমিকা; বাংলাদেশে পানির উৎসে হুমকি (নদী দখল, বাঁধ, গতিপথ পরিবর্তন); পানির উৎস সংরক্ষণ ও উন্নয়ন; পানি একটি মৌলিক অধিকার; পানিপ্রবাহের সর্বজনীনতা ও আন্তর্জাতিক নিয়মনীতি (রামসার কনভেনশন, আন্তর্জাতিক নদী কনভেনশন)) |
| ch4 | `জীবঅভিব্ভের সপক্ষে প্রমাণ` → `জৈব অভিব্যক্তির সপক্ষে প্রমাণ`. Add the missing bits: টেস্টটিউব বেবি; সন্তানের লিঙ্গ নির্ধারণ; পৃথিবীতে জীবনের উৎপত্তি ও রাসায়নিক বিবর্তন; সমসংস্থ, সমবৃত্তি ও লুপ্তপ্রায় অঙ্গ; সংযোগকারী জীব ও জীবন্ত জীবাশ্ম; ল্যামার্কের তত্ত্ব; ডারউইনের প্রাকৃতিক নির্বাচন তত্ত্ব; নতুন প্রজাতির উৎপত্তি (পৃথকীকরণ, সংকরায়ণ, পলিপ্লয়ডি). No Mendelian-genetics topics (not in this chapter). |
| ch6 | merge `তন্তু থেকে সুতা তৈরি` + `…: স্পিনিং` + `কার্ডিং ও কম্বিং` → `তন্তু থেকে সুতা তৈরি (কার্ডিং, কম্বিং, স্পিনিং)`. `মনোমার, পলিমার, ডাইমার, ট্রাইমার` → `পলিমারের একক (মনোমার, পলিমার)`. Fix `পরিবেশের ভারসাম্যহীনতা` → `প্লাস্টিক দূষণ ও পরিবেশের ভারসাম্যহীনতা`. Verify তন্তু (not তন্ত্র), সুতা (not সূতা). |
| ch7 | verify `এসিড ছড়ালে শাস্তি` on the page; fix to what's actually printed. Verify পাকস্থলী (not পাকশল্লি), প্রাত্যহিক (not প্রাতিষ্ঠানিক). |
| ch9 | `দুর্যোগের ভূমিকম্প/ভূমিধস/বন্যা/খরা` → `ভূমিকম্প` / `ভূমিধস` / `বন্যা` / `খরা` (or `<X> দুর্যোগ`). Verify `সামুদ্রিক প্রবাল বৃদ্ধি` — likely `উপকূলীয় জলোচ্ছ্বাস` or `লবণাক্ততা বৃদ্ধি`. Drop `তাৎক্ষণিক করণীয়` or attach a head (`দুর্যোগকালীন তাৎক্ষণিক করণীয়`). Verify নদীভাঙন (not নদীবাহন). |
| ch10 | `স্থিতিস্থাপক জড়তা ও গতিজড়তা` → `স্থিতিজড়তা ও গতিজড়তা`. Drop `জড়তার ব্যবহারিক অভিজ্ঞতা`. |
| ch11 | merge `তড়িৎ প্রবাহ` + `বিদ্যুৎ প্রবাহ` → one row `তড়িৎ প্রবাহ`. Verify নিষ্কাশন (not নিষ্কাসন), প্রাত্যহিক in the chapter title. |

---

## 5. config/science.json

- Add any NEW OCR misread you confirmed on a page to `spelling_corrections` as
  `"garbled": "correct"`, and add a one-line cite to `_spelling_notes` (`"fix": "chN body p.XX"`).
  NO entry without a page citation (README §6.1; `subjects/science.md`). Applied as a
  token-boundary find/replace on chapter_title + every topic.
- After Step 8+9, read `output/<book>-merge-candidates.txt`; for each group that is a true §3.5
  merge (not distinct concepts), add a `merge_overrides` entry:
  `"অধ্যায় N: <exact chapter label incl. Bengali numeral>": { "<topic to keep/replace>": "<merged label>", "<topic to fold>": "_merge_" }`.
  Leave distinct pairs alone. Re-run assemble→merge→validate.
- `scope_split.max_core_words` stays 12 unless `--stage final` WARNs a lot of long labels.
- Add valid terms the spell-checker flags to `lexicon_extra.words` — only after confirming
  spelling on a page.

---

## 6. Assemble → merge → scope-split → validate

```bash
B="Secondary (BV)-2026_Class 9-10_Science_compressed"
PYTHONIOENCODING=utf-8 python scripts/06_assemble.py "$B" 9-10 science
PYTHONIOENCODING=utf-8 python scripts/08_merge.py    "output/$B.csv"
PYTHONIOENCODING=utf-8 python scripts/12_scope_split.py "output/$B.csv"
PYTHONIOENCODING=utf-8 python scripts/05_validate.py --stage topicmap "$B"
PYTHONIOENCODING=utf-8 python scripts/05_validate.py --stage final    "$B"
```
Or just: `PYTHONIOENCODING=utf-8 python scripts/run_book.py "$B" 9-10 science` and fix whatever
gate it stops on. Both `--stage topicmap` and `--stage final` must exit 0 with NO
`NCTB_SKIP_HEADING_GATE`. Then do the Step 6 eyeball: read every final CSV topic against the page
image it came from (a garbled word "corrected" to a nearby real word is the trap).

Expected outcome: 6-column CSV, ~120-170 rows (ch2 loses ~5 misassigned, gains its real water
topics; ch1/ch4/ch9 gain coverage).

---

## 7. Push to Google Sheet "Science" tab

Sheet key `11I4QaFd1GZSaFWFCQ9I7UuBBAUpfxZ-jN1y9TZGkmV0`, worksheet title `Science`,
service account `bright-fastness-397410-e569326fd692.json` (already has edit access; it is
git-ignored — keep it that way).

```python
# scripts/push_science_to_sheet.py   (run after the CSV is green)
import csv, gspread
BOOK = "Secondary (BV)-2026_Class 9-10_Science_compressed"
gc = gspread.service_account(filename="bright-fastness-397410-e569326fd692.json")
sh = gc.open_by_key("11I4QaFd1GZSaFWFCQ9I7UuBBAUpfxZ-jN1y9TZGkmV0")
ws = sh.worksheet("Science")
with open(f"output/{BOOK}.csv", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))
ws.clear()
ws.update(rows, "A1", value_input_option="RAW")
print(f"pushed {len(rows)-1} rows x {len(rows[0])} cols to '{ws.title}'")
```
Run: `PYTHONIOENCODING=utf-8 python scripts/push_science_to_sheet.py`
Verify: reopen the tab; header row is `grade,subject,chapter,topic,scope_note,topic_raw`;
chapter labels use Bengali numerals; spot-check 5 rows against the book.

---

## 8. Finish

- Update README §13: move Science to "DONE from full chapter bodies (2026-…), 11 chapters,
  N topics, Step 4b heading checklist filled, all 3 validate stages green".
- Update `docs/agent-memory/accounting-issues.md` (the Science paragraph) and
  `docs/agent-memory/pipeline-architecture-2026-08.md` book-status list.
- `subjects/science.md`: mark the "Known errors still in the shipped box-only CSV" items resolved
  and move any newly-confirmed spelling fixes into the canonical table with page cites.

---

## Guardrails (read before starting)

1. **Never write a heading or topic you did not read off a page.** Machine OCR text is a
   structural aid only; every heading spelling and every topic label must be confirmed against
   the image. Inventing from general knowledge or the old CSV is the exact failure that caused
   this redo.
2. If you were given <60% of a chapter's body pages, set `"needs_review": true` and stop — do
   not map from what you have.
3. Do not touch Higher Math or BGS. This task is Science only.
4. Do not `git commit` or `git push` unless the owner asks.
5. Keep `bright-fastness-397410-e569326fd692.json` out of git (already in `.gitignore`).
