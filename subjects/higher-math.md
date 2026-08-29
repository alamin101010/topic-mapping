# Subject profile — higher-math

Prepended to `prompts/topic_map_prompt.md` at Step 7.

---

## Identity
- `subject`: `higher-math`
- `grade`: `9-10`
- language mix: Bengali + English technical terms (Set, Function, Venn Diagram, Polynomial, Coefficient, Degree, Tangent, Secant, Sin, Cos, Log, etc.) — keep English/mathematical notation as-is.

## What a topic looks like in this subject
A named mathematical concept, theorem, property, formula, method, or construction technique a student revises as one unit:

- GOOD: `সেটের ধারণা`, `পূরক সেট`, `শক্তি সেট`, `ভেনচিত্র`, `সংযোগ ও ছেদ`,
  `বহুপদীর ধারণা`, `সূচক ও লগারিদম`, `ত্রিকোণমিতিক অনুপাত`, `সমকোণী ত্রিভুজ`,
  `ভেক্টরের যোগ`, `সমতলীয় সমীকরণ`, `ঘনকেন্দ্রিক সমীকরণ`, `সম্ভাবনার মান`,
  `ভরকেন্দ্র`, `জ্যামিতিক অঙ্কন`
- NOT a topic: a single worked example, one plugged-in formula calculation, a drill exercise, a proof step, or a table-fill activity.

## Head-noun rule for this subject
When a body heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `প্রমাণ`, `উপপাদ্য`, `সূত্র`, `নিয়ম`, `প্রকারভেদ`, `গুরুত্ব`, `উদাহরণ`, `আলোচনা`, `প্রয়োগ`), prefix the mathematical concept it belongs to: `সেটের ধারণা` not `ধারণা`; `ত্রিকোণমিতিক সূত্র` not `সূত্র`; `সমীকরণের প্রকারভেদ` not `প্রকারভেদ`. In higher math the enclosing concept is usually the section title or the theorem/property named in the paragraph.

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
Example: `সেটের ধারণা` (not `সেটের ধারণা ও বৈশিষ্ট্য`); `সংযোগ ও ছেদ` (merged pair);
`ত্রিকোণমিতিক অনুপাত (সাইন, কোসাই, ট্যান, কোট, সেক্যান্ট, কোসেক্যান্ট)` with scope note.

## Distinct concepts to KEEP SEPARATE
- `সেট` ≠ `সাবসেট` ≠ `পূরক সেট` ≠ `শক্তি সেট`
- `ইউনিয়ন` ≠ `ইন্টারসেকশন` ≠ `ডিফারেন্স`
- `বহুপদী` ≠ `বহুপদীর মান` ≠ `বহুপদীর মূল`
- `সমীকরণ` ≠ `অসমতা` ≠ `ভূমিকা` (different chapter concepts)
- `সাইন` ≠ `কোসাইন` ≠ `ট্যানজেন্ট`
- `সরলরেখা` ≠ `পরাবৃত্ত` ≠ `উপবৃত্ত` ≠ অধিবৃত্ত
- `ভেক্টর` ≠ `অভিলম্ব` ≠ `সমান্তরাল`
- `সমতলীয় সমীকরণ` ≠ `বিপরীত ত্রিকোণমিতি`
- `ক্রমিক সম্ভাবনা` ≠ `একচেটিয়া সম্ভাবনা` ≠ `শর্তাধীন সম্ভাবনা`
- `স্থূলক` ≠ `লগারিদমীয়` (different function types)
- `অসীম ধারা` ≠ `সীমা` ≠ `ধারার সমষ্টি`
- `সমকোণী ত্রিভুজ` ≠ `সমদ্বিবাহু ত্রিভুজ` ≠ `সমবাহু ত্রিভুজ`

## Canonical spellings of technical terms (fill as OCR garble is found)
| garbled | correct | meaning |
|---|---|---|
(Add as OCR errors are discovered — math notation is mostly universal, Bengali headings are the main risk.)

Verify each against the page image before trusting it.

## Chapters where numbering restarts per unit
None — chapters 1–14 run straight through.

## Chapter-map note
`chapter-maps/class9-10-higher-math.csv` uses **PDF page numbers**
(printed page + 5; PDF p.6 = printed p.1 = ch1 opener). Chapter openers
have no printed page number; content starts at printed p.1 on the next page.
