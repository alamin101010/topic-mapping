# Subject profile — science

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `science`
- `grade`: `9-10`
- language mix: Bengali + English technical terms (protein, carbohydrate, lipid,
  vitamin, pH, DNA, Newton, force, polymer, etc.) — keep English/technical terms
  as-is.

## What a topic looks like in this subject
A named scientific concept, process, law, phenomenon, substance, structure, or
system — something a student revises as one unit:

- GOOD: `খাদ্যের উপাদান`, `কার্বোহাইড্রেটের পুষ্টিগত গুরুত্ব`, `নিউটনের গতির প্রথম সূত্র`,
  `পানির ধর্ম`, `হৃদযন্ত্রের গঠন`, `পলিমারকরণ প্রক্রিয়া`, `জলবায়ু পরিবর্তনের প্রভাব`
- NOT a topic: a single worked calculation, a lab experiment step, a slide
  preparation procedure, a verification/observation activity.

## Head-noun rule for this subject
When a heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `গুরুত্ব`, `প্রকারভেদ`,
`উৎস`, `কাজ`, `প্রভাব`, `প্রক্রিয়া`, `পার্থক্য`, `উপাদান`), prefix the concept /
substance / system it belongs to: `শর্করার উৎস` not `উৎস`; `প্রোটিনের পুষ্টিগত
গুরুত্ব` not `গুরুত্ব`; `পানির ধর্ম` not `ধর্ম`.

## Distinct concepts to KEEP SEPARATE
- `উদ্ভিজ্জ উৎস` ≠ `প্রাণিজ উৎস` (food sources)
- `শর্করা` ≠ `প্রোটিন` ≠ `স্নেহ পদার্থ` ≠ `ভিটামিন` ≠ `খনিজ লবণ` (nutrient types)
- `স্থিতি` ≠ `গতি` (state of matter / motion)
- `বল` ≠ `জড়তা` ≠ `ভর` ≠ `ওজন` (distinct physical quantities)
- `অম্ল` ≠ `ক্ষারক` ≠ `লবণ` (acid/base/salt)
- `প্রাকৃতিক পলিমার` ≠ `কৃত্রিম পলিমার`
- `প্রাকৃতিক তন্তু` ≠ `কৃত্রিম তন্তু` (fibre — the word is `তন্তু`, NOT `তন্ত্র`
  "system"; ch6 box p.130); `প্রাকৃতিক বস্ত্র` ≠ `কৃত্রিম বস্ত্র`
- `দর্পণ` ≠ `লেন্স` (mirror vs lens)
- `স্থির তড়িৎ` ≠ `চলতড়িৎ` (static vs current electricity)
- `তাপ` ≠ `তাপমাত্রা` ≠ `তাপগতিবিদ্যা`
- `মাটি` ≠ `খনিজ` ≠ `জ্বালানি` (soil/mineral/fuel)
- `জলবায়ু পরিবর্তন` ≠ `পরিবেশগত সমস্যা` ≠ `দুর্যোগ`
- `বয়ঃসন্ধিকাল` ≠ `প্রজনন` (puberty vs reproduction)
- `তড়িৎ বিশ্লেষণ` ≠ `তড়িৎ প্রলেপন` (electrolysis vs electroplating)
- `কিলোওয়াট` ≠ `কিলোওয়াট-ঘণ্টা` (power vs energy unit)

## Canonical spellings of technical terms (OCR tends to garble)

**Rule: no row without a citation.** Every entry is verified against the page
image and gives the PDF page it was confirmed on. A "correction" invented from
OCR output — not read off the book — is how the 2026-08-28 defects happened
(`প্রাত্যহিক` forced to `প্রাতিষ্ঠানিক`; roughage mislabelled "reflex"). If you
cannot cite a page, do not add the row.

| garbled | correct | meaning | verified |
|---|---|---|---|
| অ্যাস | অম্ল | acid | — |
| ফারাক | ক্ষারক | base/alkali | — |
| এইউদস | এইডস (AIDS) | acquired immunodeficiency syndrome | — |
| বড়ি মাস ইনডেক্স | বডি মাস ইনডেক্স (BMI) | body mass index | — |
| প্রাতিহাসিক / প্রাতিষ্ঠানিক জীবন | প্রাত্যহিক জীবন | everyday life | ch7 box p.146; ch11 title+body p.235 |
| সংগ্রহলন | সঞ্চালন | (blood) circulation | ch3 box p.58; body p.62 |
| কোলেষ্টেরল / কোলেষ্টরল | কোলেস্টেরল | cholesterol (স্ট, not ষ্ট) | ch3 body p.80 |
| পাকশল্লি | পাকস্থলী | stomach | ch7 box p.146 |
| নিষ্কাসন | নিষ্কাশন | extraction | ch11 body p.240 |
| তন্ত্র (textile context) | তন্তু | fibre | ch6 box p.130 — see distinct-concepts list |

**Do NOT "correct" `রাফেজ`** — it is roughage / dietary fibre (ch1, আঁশযুক্ত
খাবার), a real term. An earlier table mapped it to "reflex", which is wrong.

## Known errors still in the shipped box-only CSV

`ocr/…Science…/topic_map.json` is the **box-only** extract (topics = OCR of the
2-page শিখনফল box, not body section headings) and was never reconciled against
the pages. Confirmed defects as of 2026-08-28 (fix by redoing Steps 2+7 from the
bodies — README Step 7 / §5 runbook):

- ch3 `রক্ত সংগ্রহলন প্রক্রিয়া` → `রক্ত সঞ্চালন প্রক্রিয়া`
- ch3 `রক্তে কোলেষ্টেরল …` → `… কোলেস্টেরল …`
- ch3 last topic `হৃদযন্ত্রের স্বাস্থ্য রক্ষায় পরিবহণ` — "পরিবহণ" is spurious;
  section heading p.80 is `৩.৫ হৃদযন্ত্রকে ভালো রাখার উপায়`
- ch6 `প্রাকৃতিক/কৃত্রিম তন্ত্রের …`, `তন্ত্র হতে সূতা …` → `তন্তু` (fibre);
  also `সূতা`→`সুতা`. Not added to `spelling_corrections` (a blind `তন্ত্র→তন্তু`
  rule mangles inflected forms and hits `গণতন্ত্র`); fix in the body re-run.
- ch7 `পাকশল্লিতে …` → `পাকস্থলীতে …`; `প্রাতিষ্ঠানিক জীবনে …` (×4) →
  `প্রাত্যহিক জীবনে …`; `… লবণের প্রাতিষ্ঠানিক অবদান` → `প্রাত্যহিক`
- ch8 `নদীবাহনের মাধ্যমে মাটি ক্ষয় প্রতিরোধ` — "নদীবাহন" is not a standard word;
  likely `নদীভাঙন` (riverbank erosion). Unverified — check the body.
- ch11 chapter title `প্রাতিষ্ঠানিক জীবনে তড়িৎ` → `প্রাত্যহিক জীবনে তড়িৎ`;
  `ধাতু নিষ্কাসন` → `ধাতু নিষ্কাশন`

The `spelling_corrections` in `config/science.json` patch the shipped CSV for the
whole-word cases; they are a stop-gap, not the fix.

## Chapters where numbering restarts per unit
None — chapters 1–11 run straight through.

## Chapter-map note
`chapter-maps/class9-10-science.csv` uses PDF page numbers. Printed page 1 =
PDF page 6 (front-matter offset k=5). Verify by checking ch1 opener at PDF p.6.
