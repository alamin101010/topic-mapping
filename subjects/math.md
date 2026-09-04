# Subject profile — math

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `math`
- `grade`: `9-10`
- language mix: Bengali + English mathematical terms (Set, Function, Real Number, Polynomial, Logarithm, Equation, Triangle, Circle, Trigonometric Ratio, etc.) — keep English/mathematical notation as-is.

## What a topic looks like in this subject
A named mathematical concept, theorem, property, formula, method, or construction technique a student revises as one unit:

- GOOD: `বাস্তব সংখ্যা`, `সেটের ধারণা`, `মৌলিক বীজগণিতিক সংক্রিয়া`, `সূচক ও লগারিদম`, `সরল সমীকরণ`, `ত্রিভুজের কোণ`, `বৃত্তের স্পর্শক`, `ত্রিকোণমিতিক অনুপাত`, `ক্ষেত্রফল`, `পরিসংখ্যান`
- NOT a topic: a single worked example, one plugged-in formula calculation, a drill exercise, a proof step, or a table-fill activity.

## Head-noun rule for this subject
When a body heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `প্রমাণ`, `উপপাদ্য`, `সূত্র`, `নিয়ম`, `প্রকারভেদ`, `গুরুত্ব`, `উদাহরণ`, `আলোচনা`, `প্রয়োগ`), prefix the mathematical concept it belongs to: `সেটের ধারণা` not `ধারণা`; `ত্রিকোণমিতিক সূত্র` not `সূত্র`; `সমীকরণের প্রকারভেদ` not `প্রকারভেদ`. In math the enclosing concept is usually the section title or the theorem/property named in the paragraph.

## Label length & staying self-identifying (README §3.6, prompt §5b)
A topic label is a **name — ≤ 5 words is the goal**, 3–8 acceptable, no minimum.
Shorten by cutting words that do no work, **never the head concept**: the short
label must still name a specific taught thing with the chapter title and subject
hidden (not an aspect word like `ধারণা` / `প্রকারভেদ` / `উদাহরণ`; not a fit for
three other chapters; not just chapter-title words). If ≤ 5 words can't pass
those, keep the longer label (WARN only) or split into sibling rows.
`config/<subject>.json → scope_split.max_core_words = 5` holds this subject to the
goal; `--stage final` WARNs on over-long or no-longer-self-identifying labels.

When a heading names a concept and then lists the parts/examples/steps it covers,
keep the label short and put the list in a trailing `(a, b, c …)` — Step 10
(`12_scope_split.py`) lifts it into the `scope_note` column. `scope_split` is on
by default. The `(...)` carries the detail so the label can be a bare name — it
does not license dropping the head concept. Fold 1–2 items into a flowing label
instead; drop examples that add nothing; give each item its own row only if it is
a full topic in its own right. An inline gloss the sentence runs past
(`FCR (…) ও …`) stays as-is.
Example: `বাস্তব সংখ্যা` (not `বাস্তব সংখ্যার ধারণা ও বৈশিষ্ট্য`); `সেটের ধারণা` (not `সেটের ধারণা ও প্রকারভেদ`); `ত্রিকোণমিতিক অনুপাত (সাইন, কোসাইন, ট্যান, কোট, সেক্যান্ট, কোসেক্যান্ট)` with scope note.

## Distinct concepts to KEEP SEPARATE
- `সেট` ≠ `সাবসেট` ≠ `পূরক সেট` ≠ `শক্তি সেট`
- `ইউনিয়ন` ≠ `ইন্টারসেকশন` ≠ `ডিফারেন্স`
- `বহুপদী` ≠ `বহুপদীর মান` ≠ `বহুপদীর মূল`
- `সমীকরণ` ≠ `অসমতা` ≠ `ভূমিকা` (different chapter concepts)
- `সাইন` ≠ `কোসাইন` ≠ `ট্যানজেন্ট`
- `সরলরেখা` ≠ `পরাবৃত্ত` ≠ `উপবৃত্ত` ≠ অধিবৃত্ত
- `সমকোণী ত্রিভুজ` ≠ `সমদ্বিবাহু ত্রিভুজ` ≠ `সমবাহু ত্রিভুজ`
- `সরল সমীকরণ` ≠ `দ্বিঘাত সমীকরণ`
- `সমানুপাত` ≠ `বিপরীত সমানুপাত`
- `সীমা` ≠ `ধারা` ≠ `ধারার সমষ্টি`

## Canonical spellings of technical terms (fill as OCR garble is found)
| garbled | correct | meaning |
|---|---|---|
(Add as OCR errors are discovered — math notation is mostly universal, Bengali headings are the main risk.)

Verify each against the page image before trusting it.

## Chapters where numbering restarts per unit
None — chapters 1–17 run straight through.

## Chapter-map note
`chapter-maps/class9-10-math.csv` uses **PDF page numbers**
(printed page + 5; PDF p.6 = printed p.1 = ch1 opener). Chapter openers
have no printed page number; content starts at printed p.1 on the next page.
