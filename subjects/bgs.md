# Subject profile — bgs (Bangladesh and Global Studies)

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `bgs`
- `grade`: `9-10`
- language mix: Bengali + English historical/political terms — keep English terms as-is.

## What a topic looks like in this subject
A named historical event, political concept, geographic feature, economic system,
social institution, or civic process — something a student revises as one unit:

- GOOD: `ভাষা আন্দোলনের পটভূমি`, `বাংলাদেশের স্বাধীনতা ঘোষণা`, `সৌরজগতের গঠন`,
  `বাংলাদেশের ভূপ্রকৃতি`, `নদ-নদীর প্রাকৃতিক সম্পদ`, `গণতন্ত্রের ধারণা`
- NOT a topic: a single date/fact drill, a map-reading exercise, a discussion question.

## Head-noun rule for this subject
When a heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `গুরুত্ব`, `প্রকারভেদ`,
`উদ্দেশ্য`, `সুবিধা`, `পদ্ধতি`, `প্রভাব`, `কারণ`, `�লাফল`), prefix the concept it
belongs to: `গণতন্ত্রের ধারণা` not `ধারণা`; `বাংলাদেশের ভূপ্রকৃতির বৈশিষ্ট্য` not `বৈশিষ্ট্য`.

## Distinct concepts to KEEP SEPARATE
- `ভাষা আন্দোলন` ≠ `সাংস্কৃতিক আন্দোলন`
- `স্বাধীনতা ঘোষণা` ≠ `মুক্তিযুদ্ধ` ≠ `চুক্তিপত্র`
- `সৌরজগৎ` ≠ `মহাকাশ`
- `ভূপ্রকৃতি` ≠ `জলবায়ু` ≠ `প্রাকৃতিক সম্পদ`
- `নদী` ≠ `খাল` ≠ `বন্যা`
- `গণতন্ত্র` ≠ `স্বৈরাচার`
- `আমদানি` ≠ `রপ্তানি`
- `কৃষি` ≠ `শিল্প` ≠ `সেবা`
- `জনসংখ্যা` ≠ `জনঘনত্ব`

## Canonical spellings of technical terms (OCR tends to garble)
| garbled | correct | meaning |
|---|---|---|
| মুক্তিযুদ্ধ | মুক্তিযুদ্ধ | Liberation War |
| স্বাধীনতা | স্বাধীনতা | Independence |
| গণতন্ত্র | গণতন্ত্র | Democracy |
| সংবিধান | সংবিধান | Constitution |
| নির্বাচন | নির্বাচন | Election |
| প্রশাসন | প্রশাসন | Administration |
| অর্থনীতি | অর্থনীতি | Economy |
| যুক্তপ্রম | ষড়যন্ত্র | conspiracy (আগরতলা ষড়যন্ত্র মামলা — ch1 body heading, printed p.10) |

## Verified factual points (do NOT let OCR/paraphrase drift here)
- Chapter 1 title date span is **১৯৪৭–১৯৭০** (1947), NOT ১৮৪৭. Confirmed on the
  TOC (printed p.i), the chapter opener, and the running header of every ch1 page.
- Chapter 1 real শিখনফল box (printed p.6) is about ভাষা আন্দোলন, পশ্চিম
  পাকিস্তানের বৈষম্য, ১৯৫৪→উনসত্তরের গণঅভ্যুত্থান, ১৯৭০-এর নির্বাচন ও তার প্রভাব,
  স্বার্থরক্ষায় কর্মসূচি প্রণয়ন. It does **not** mention বঙ্গভঙ্গ ১৯০৫ or ১৮৫৭-৫৮
  সিপাহি বিপ্লব — if a topic_map lists those as ch1 outcomes they are hallucinated,
  drop them and re-read the box.
- This is the 2026 edition: ch2 legitimately covers the ১৯৯০ ও ২০২৪ (জুলাই)
  গণঅভ্যুত্থান — those topics are real, not hallucinations.

## Chapters where numbering restarts per unit
None — chapters 1–15 run straight through.

## Chapter-map note
`chapter-maps/class9-10-bgs.csv` uses PDF page numbers. Printed page 1 =
PDF page 6 (front-matter offset k=5, constant across the whole book — verified at
the ch12/13, ch13/14 and ch14/end boundaries). The TOC lists printed pages 1-200
(PDF 6-205; the PDF has 206 pages, last page = "সমাপ্ত").

### KNOWN BUG in the current chapter-map (fix on re-extract)
Three cells were entered as PRINTED numbers instead of PDF (printed + 5), so the
+5 offset is missing:
| ch | current | should be | effect |
|---|---|---|---|
| 13 end_page  | 177 | **182** | ch13 loses its last ~5 pages (printed 173-177) |
| 14 start_page | 178 | **183** | ch14 currently ingests ch13's tail (printed 173-177) |
| 15 end_page  | 200 | **205** | ch15 loses its last ~5 pages (printed 196-200) |
TOC ranges (printed): ch13 164-177, ch14 178-184, ch15 185-200. After fixing,
re-run Step 2 extract + Step 7 for ch13/14/15 (topic bleed + missing tail topics
are likely in the current output).
