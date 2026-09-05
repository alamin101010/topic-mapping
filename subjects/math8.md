# Subject profile — math8 (Mathematics, Class 8)

Prepended to `prompts/topic_map_prompt.md` at Step 7 so the model maps this
chapter as a **subject-matter reader**, not a generic text splitter.

---

## Identity
- `subject`: `math8`
- `grade`: `8`
- language mix: Bengali + English mathematical terms (Set, Function, Equation,
  Circle, Pythagoras, Quadrilateral, etc.) — keep English/mathematical notation as-is.

## What a topic looks like in this subject
A named mathematical concept, theorem, property, formula, method, or construction
technique a student revises as one unit. Class 8 Math covers: pattern, profit/compound
interest, measurement, algebraic formulas, factorization, algebraic fractions,
simultaneous equations, sets, quadrilateral, Pythagoras theorem, circle, and data.

- GOOD: `প্যাটার্ন`, `সেটের ধারণা`, `সূচক ও লগারিদম`, `বীজগণিতীয় ভগ্নাংশ`,
  `সহ-সমীকরণ`, `চতুর্ভুজের ধর্ম`, `পিথাগোরাসের উপপাদ্য`, `বৃত্তের স্পর্শক`,
  `তথ্য ও উপাত্ত`
- NOT a topic: a single worked example, one plugged-in formula calculation,
  a drill exercise, a proof step, or a table-fill activity.

## Head-noun rule for this subject
When a body heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `প্রমাণ`, `উপপাদ্য`,
`সূত্র`, `নিয়ম`, `প্রকারভেদ`, `গুরুত্ব`, `উদাহরণ`, `আলোচনা`, `প্রয়োগ`),
prefix the mathematical concept it belongs to: `সেটের ধারণা` not `ধারণা`;
`ত্রিকোণমিতিক সূত্র` not `সূত্র`. In math the enclosing concept is usually
the section title or the theorem/property named in the paragraph.

## Label length & staying self-identifying (README §3.6, prompt §5b)
A topic label is a **name — ≤ 5 words is the goal**, 3–8 acceptable, no minimum.
Shorten by cutting words that do no work, **never the head concept**.
`config/math8.json → scope_split.max_core_words = 5` holds this subject to the goal.

## Distinct concepts to KEEP SEPARATE
- `সেট` ≠ `সাবসেট` ≠ `পূরক সেট` ≠ `শক্তি সেট`
- `ইউনিয়ন` ≠ `ইন্টারসেকশন` ≠ `ডিফারেন্স`
- `বহুপদী` ≠ `বহুপদীর মান` ≠ `বহুপদীর মূল`
- `সমীকরণ` ≠ `অসমতা`
- `সাইন` ≠ `কোসাইন` ≠ `ট্যানজেন্ট`
- `সরল সমীকরণ` ≠ `দ্বিঘাত সমীকরণ`
- `সমানুপাত` ≠ `বিপরীত সমানুপাত`
- `মুনাফা` ≠ `চক্রবৃদ্ধি মুনাফা`
- `বৃত্ত` ≠ `চাপ` ≠ `জ্যা` ≠ `স্পর্শক`

## Canonical spellings of technical terms (fill as OCR garble is found)
Math notation is mostly universal; Bengali headings are the main risk.
Verify each against the page image before trusting it.

## Chapters where numbering restarts per unit
None — chapters run straight through. Sub-chapters use decimal notation (e.g., 4.1, 4.2, 5.1, 5.2).

## Chapter-map note
`chapter-maps/class_8_math_compressed.csv` uses PDF page numbers
(printed page + 5; PDF p.6 = printed p.1 = ch1 opener).
190 pages, 11 chapters covering 20 sections.
