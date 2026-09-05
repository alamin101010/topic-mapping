# Subject profile — bgs8 (Bangladesh and Global Studies, Class 8)

Prepended to `prompts/topic_map_prompt.md` at Step 7 so the model maps this
chapter as a **subject-matter reader**, not a generic text splitter.

---

## Identity
- `subject`: `bgs8`
- `grade`: `8`
- language mix: Bengali + English technical/historical terms — keep English terms as-is.

## What a topic looks like in this subject
A named historical event, political concept, geographic feature, economic
system, social institution, or civic process — something a student revises
as one unit. Class 8 BGS covers colonial history, Liberation War, economy,
government, culture, socialization, ethnic groups, social problems,
population, climate, natural resources, and international cooperation.

- GOOD: `ঔপনিবেশিক যুগের প্রাতিষ্ঠানিক ব্যবস্থা`, `বাংলাদেশের মুক্তিযুদ্ধের পটভূমি`,
  `বাংলাদেশের অর্থনৈতিক বিভিন্নতা`, `সামাজিকীকরণের ধারণা`, `বাংলাদেশের নৃগোষ্ঠীসমূহ`,
  `জলবায়ু পরিবর্তন ও দুর্যোগ`
- NOT a topic: a single date/fact drill, a map-reading exercise, a discussion question.

## Head-noun rule for this subject
When a body heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `গুরুত্ব`,
`প্রকারভেদ`, `উদ্দেশ্য`, `সুবিধা`, `পদ্ধতি`, `প্রভাব`, `কারণ`, `ফলাফল`),
prefix the concept it belongs to: `সামাজিকীকরণের ধারণা` not `ধারণা`;
`বাংলাদেশের অর্থনীতির বৈশিষ্ট্য` not `বৈশিষ্ট্য`.

## Distinct concepts to KEEP SEPARATE
- `ঔপনিবেশিক যুগ` ≠ `মুক্তিযুদ্ধ`
- `স্বাধীনতা সংগ্রাম` ≠ `মুক্তিযুদ্ধ`
- `অর্থনীতি` ≠ `অর্থব্যবস্থা`
- `সাংস্কৃতিক পরিবর্তন` ≠ `সামাজিকীকরণ`
- `নৃগোষ্ঠী` ≠ `জাতিগোষ্ঠী`
- `সামাজিক সমস্যা` ≠ `দুর্যোগ`
- `জনসংখ্যা` ≠ `জনঘনত্ব`
- `জলবায়ু` ≠ `দুর্যোগ`
- `প্রাকৃতিক সম্পদ` ≠ `জলবায়ু`

## Canonical spellings of technical terms (OCR tends to garble)
| garbled | correct | meaning |
|---|---|---|
| মুক্তিযুদ্ধ | মুক্তিযুদ্ধ | Liberation War |
| স্বাধীনতা | স্বাধীনতা | Independence |
| ঔপনিবেশিক | ঔপনিবেশিক | Colonial |
| প্রত্নতাত্ত্বিক | প্রত্নতাত্ত্বিক | Archaeological |
| সামাজিকীকরণ | সামাজিকীকরণ | Socialization |
| নৃগোষ্ঠী | নৃগোষ্ঠী | Ethnic group |
| সামাজিক | সামাজিক | Social |
| জনসংখ্যা | জনসংখ্যা | Population |
| জলবায়ু | জলবায়ু | Climate |
| প্রাকৃতিক | প্রাকৃতিক | Natural |
| সম্পদ | সম্পদ | Resources |
| সহযোগী | সহযোগী | Associate/Cooperative |

## Verified factual points (do NOT let OCR/paraphrase drift here)
- 2026 edition, 13 chapters + skill verification section.
- Chapter 1 covers Colonial Age and Liberation War of Bengal (not just 1971).
- Chapter 3 is specifically the Liberation War of Bangladesh (বাংলাদেশের মুক্তিযুদ্ধ).
- Chapter 5 covers State and Government System (রাষ্ট্র ও সরকার ব্যবস্থা).
- Chapters 11-12 cover Climate/Disasters and Natural Resources respectively.

## Chapters where numbering restarts per unit
None — chapters 1-13 run straight through.

## Chapter-map note
`chapter-maps/class8-bgs.csv` uses PDF page numbers. Printed page 1 = PDF page 6
(front-matter offset k=5, constant across the whole book). The book has 149 pages
(PDF pages 6-154 = printed 1-149). Verify k by checking the chapter 1 opener on
PDF page 6.
