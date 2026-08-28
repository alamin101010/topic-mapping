# Subject profile — agriculture

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `agriculture`
- `grade`: `9-10`
- language mix: Bengali +少量 English technical terms (FCR, pH, salinity) — keep
  English/acronyms as-is.

## What a topic looks like in this subject
A named agricultural concept, technique, process, system, crop type, or
equipment a student revises as one unit:

- GOOD: `ফসল নির্বাচন`, `ভূমিক্ষয়ের প্রকারভেদ`, `বীজ সংরক্ষণের পদ্ধতি`,
  `মাছের খাদ্য সম্পূরক`, `পলি দোআঁশ মাটি`, `কৃষি সম্বায়ের উদ্দেশ্য`,
  `পারিবারিক খামারের সুবিধা`
- NOT a topic: a single worked example, a specific crop yield number, a
  student activity (কাজ) box, or a picture caption.

## Trailing "(...)" enumerations → scope notes
When a body heading names a concept and then lists its parts —
`ধান চাষপদ্ধতি (জমি নির্বাচন, জাত, রোপণ, পরিচর্যা, ফসল সংগ্রহ)` — keep the label in
`topics[]` short (`ধান চাষপদ্ধতি`) and let **Step 10** lift the list into
`scope_note`, or carry the parts in `keywords` instead. Do not inflate the label
to 13+ words (README §3.6). An inline gloss the sentence runs past
(`FCR (খাদ্য রূপান্তর হার) ও …`) stays as-is — only a `(...)` that *closes* the
string is a scope note. `config/agriculture.json` → `scope_split.enabled` is on.

## Head-noun rule for this subject
When a heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `গুরুত্ব`, `প্রকারভেদ`,
`উদ্দেশ্য`, `কার্যাবলি`, `সুবিধা`, `প্রয়োজনীয়তা`, `পার্থক্য`, `কারণ`, `ধাপ`,
`পদ্ধতি`), prefix the concept it belongs to: `ভূমিক্ষয়ের কারণ` not `কারণ`;
`বীজ সংরক্ষণের গুরুত্ব` not `গুরুত্ব`.

## Distinct concepts to KEEP SEPARATE
- `ফসল নির্বাচন` ≠ `বীজ নির্বাচন` ≠ `বীজ সংরক্ষণ`
- `ভূমিক্ষয়` ≠ `ভূমি ক্ষয়রোধ`
- `দোআঁশ মাটি` ≠ `কাদা মাটি` ≠ `বেলে দোআঁশ মাটি`
- `বৃষ্টিপাতজনিত ভূমিক্ষয়` ≠ `বায়ুপ্রবাহজনিত ভূমিক্ষয়`
- `মাছ চাষ` ≠ `পোল্ট্রি চাষ` ≠ `গবাদি পশু পালন`
- `হ্যাচারি` ≠ `পুকুর` ≠ `আঁটুড় পুকুর`
- `সম্পূরক খাদ্য` ≠ `প্রাকৃতিক খাদ্য`
- `বনায়ন` ≠ `কৃষি সম্বায়` ≠ `পারিবারিক খামার`
- `সেচন` ≠ `নিষ্কাশন`
- `ভূমি কর্ষণ` ≠ `ভূমি প্রস্তুতি`

## Canonical spellings of technical terms (fill as OCR garble is found)
| garbled | correct | meaning |
|---|---|---|
| (to be filled after first extraction) | | |

Verify each against the page image before trusting it.

## Chapters where numbering restarts per unit
None — chapters 1–7 run straight through.

## Chapter-map note
`chapter-maps/class9-10-agriculture.csv` uses **PDF page numbers**
(printed page + 5; PDF p.6 = printed p.1 = ch1 opener). The Bengali TOC is on
PDF page 5. Chapter content spans Bengali pages ১–২২৮ (PDF pages 6–233).
