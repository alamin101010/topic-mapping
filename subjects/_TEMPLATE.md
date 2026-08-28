# Subject profile — <subject>

Prepended to `prompts/topic_map_prompt.md` at Step 7 so the model maps this
chapter as a **subject-matter reader**, not a generic text splitter. Copy this
file to `subjects/<subject>.md` and fill every section from 2–3 real chapters
before the first run.

---

## Identity
- `subject` (english lowercase, goes in every CSV row): `<e.g. physics>`
- `grade`: `<e.g. 9-10>`
- language mix: `<Bengali only | Bengali + English technical terms>`

## What a topic looks like in this subject
One line describing the concept shapes a valid topic can take here. Examples:

- **physics** — a named quantity, law, principle, phenomenon, or device
  (`নিউটনের গতির সূত্র`, `রৈখিক ভরবেগের সংরক্ষণ`, `সরল দোলকের পর্যায়কাল`).
  NOT a derivation step, a worked example, or a lab reading.
- **chemistry** — a substance/class, reaction type, property, or process
  (`জারণ-বিজারণ বিক্রিয়া`, `পর্যায় সারণিতে ইলেকট্রন বিন্যাস`). NOT a single
  experiment or a test-tube observation.
- **biology** — a structure, system, process, or organism group
  (`উদ্ভিদের সালোকসংশ্লেষণ প্রক্রিয়া`, `মানব পরিপাকতন্ত্রের গঠন`). NOT a slide
  prep or a dissection step.
- **civics / bgs** — a concept, institution, right/duty, or political-social
  process (`সংসদীয় সরকারব্যবস্থার বৈশিষ্ট্য`, `নাগরিকের মৌলিক অধিকার`). NOT a
  date or a single event unless it is itself the taught concept.
- **geography** — a process, landform, region, resource, or spatial pattern
  (`নদীর ক্ষয় ও সঞ্চয় প্রক্রিয়া`, `বাংলাদেশের জলবায়ুর বৈশিষ্ট্য`).

## Head-noun rule for this subject
When a body heading is a bare attribute (`ধারণা`, `বৈশিষ্ট্য`, `প্রভাব`,
`প্রকারভেদ`, `গুরুত্ব`, `প্রয়োজনীয়তা`, `পার্থক্য`, `কারণ`, `ধাপ` …), prefix the
enclosing section's concept. In this subject the enclosing concept is usually
`<the section title | the phenomenon named in the paragraph>`.

## Label length & staying self-identifying (README §3.6, prompt §5b)
A topic label is a **name — ≤ 5 words is the goal**, 3–8 acceptable, no minimum.
Shorten by cutting words that do no work, **never the head concept**: the short
label must still name a specific taught thing with the chapter title and subject
hidden (not an aspect word like `শ্রেণিবিভাগ` / `ধারণা` / `উদাহরণ`; not a fit for
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
`<subject-specific example, e.g. উত্তল দর্পণের ব্যবহার (নিরাপদ ড্রাইভিং, পাহাড়ি রাস্তা)>`

## Distinct concepts to KEEP SEPARATE (never let the merge collapse these)
List the opposite / near-string pairs specific to this subject, e.g.
`উত্তল লেন্স` ≠ `অবতল লেন্স`; `তড়িৎ চালক বল` ≠ `বিভব পার্থক্য`;
`সমীকরণ` ≠ `অসমতা`. These also go in `config/<subject>.json → distinct_pairs`.

## Canonical spellings of technical terms
The correct Bengali spelling of terms the OCR tends to garble, so a heading can
be fixed against this list. e.g. `দ্বৈত সত্তা` (not দৈত্ব সত্তা), `ছক` (not চক).
These also go in `config/<subject>.json → spelling_corrections`.

## Chapters where numbering restarts per unit (if any)
`<none | unit II restarts at 1; record chapter_no as running integer>`
