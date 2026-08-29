---
name: higher-math-partial-run
description: Higher Math book has a partial pipeline run on disk — do not auto-run or ad-hoc fix it
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 05b4d3d8-7d1b-45e7-a060-23759d7ec74b
  modified: 2026-08-29T18:24:22.469Z
---

The Higher Math book (`…Class 9-10_Higher Math_compressed`) has a **Step-4
artifact** committed: `ocr/…/topic_map.json` + a 4-column `output/…Higher
Math_compressed.csv`. Step 9 (merge), Step 10 (scope-split) and Step 6 (eyeball)
were never run; `config/higher-math.json` `spelling_corrections` and
`merge_overrides` are still `{}`.

**Why:** the user wants it left for one deliberate owner-scheduled redo pass
(same handling as the box-only books), not patched piecemeal and not kicked off
as a side effect of another task.

**How to apply:** do not run the pipeline for Higher Math or edit its
CSV/config/chapter-map unless the user explicitly asks for the Higher Math redo.
Issues found (2026-08-29) are catalogued in README §13 "Known-bad in current
output": trailing `(a,b,c)` lists still in `topic`, over-long ch4 construction
labels, `max_core_words` 12 (should be 5), chapter-map ch10 `দৈপদী বিন্যাস` →
`দ্বিপদী বিস্তৃতি`, topic `গুণোত্তর সম্প্রসারণ (Binomial Theorem)` → `দ্বিপদী উপপাদ্য`,
OCR misreads (`অবয়`→`অন্বয়` confirmed; others to verify on the page).

README got a new **§5.1 "Definition of done"** (2026-08-29): a book's output is
finished only when 6-column, all 3 validate stages exit 0, no trailing `(…)`
comma-list in `topic`, config populated from that book, `max_core_words`
reviewed, Step 6 eyeball done. A 4-column CSV / empty-stub config = pipeline
stopped early, not a deliverable. See [[pipeline-architecture-2026-08]],
[[accounting-issues]].

**2026-08-30 update — state on disk has moved, policy has NOT.** Someone ran
partial redo work on 2026-08-29 ~15:55: `output/…Higher Math….csv` is now
**6-column, 150 rows**; `config/higher-math.json` is **fully populated**
(`spelling_corrections`, `merge_overrides`, `distinct_pairs`, `lexicon_extra`,
`scope_split.max_core_words: 5`); all 3 validate stages exit 0 (`--stage final`
= 22 WARN, 0 FAIL — the ch4 জ্যামিতিক অঙ্কন labels still run 7–15 words). These
files are all UNTRACKED in git. The "do NOT auto-run or ad-hoc fix — one
deliberate owner-scheduled pass only" instruction is unchanged; treat the
6-column CSV as still-not-a-deliverable until an owner signs off. The
2026-08-30 heading-gate (see [[pipeline-architecture-2026-08]]) also FAILs
`--stage topicmap` for Higher Math now (no `headings/chNN.json`).
