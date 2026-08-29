---
name: bgs-issues
description: "BGS (Bangladesh & Global Studies) class 9-10 — partial run; no hallucinated chapters, but page-range bug + 2 fixed OCR errors + fabricated ch1 outcomes"
metadata: 
  node_type: memory
  type: project
  originSessionId: aec5bfa1-e5ed-47d8-9302-8081e9b18458
  modified: 2026-08-29T18:19:22.030Z
---

Checked 2026-08-29 for "hallucinated chapters" in BGS.

**No hallucinated chapters.** All 15 chapters in `chapter-maps/class9-10-bgs.csv`,
`ocr/…BGS…/topic_map.json`, and `output/…BGS…_compressed.csv` match the book's
সূচিপত্র (প্রথম–পঞ্চদশ), titles included. Chapter *topics* spot-check as real
body headings (verified ch1 against pages).

Defects found (see README "Known-bad" → BGS and [[higher-math-partial-run]] for
the same "partial run, deliberate finish pass only" handling):

- **FIXED 2026-08-29** in CSV + chapter-map + topic_map.json + `config/bgs.json`
  `spelling_corrections` (`১৮৪৭-১৯৭০`→`১৯৪৭-১৯৭০`, `যুক্তপ্রম`→`ষড়যন্ত্র`), all
  verified against page images:
  - ch1 title date `(১৮৪৭-১৯৭০)` → `(১৯৪৭-১৯৭০)` (book reads 1947 on TOC, chapter
    opener, running header). Was in 13 CSV rows.
  - ch1 topic `আগরতলা যুক্তপ্রম মামলা` → `আগরতলা ষড়যন্ত্র মামলা` (body heading,
    printed p.10).
- **Chapter-map page-range bug, NOT yet fixed** (needs re-extract + Step 7 for
  ch13/14/15): ch13/14/15 cells were entered as printed numbers, missing the
  constant +5 PDF offset (k=5). Should be ch13 `169,182`, ch14 `183,189`,
  ch15 `190,205` (currently `169,177` / `178,189` / `190,200`). Effect: ch13 &
  ch15 lose their last ~5 pages; ch14 ingests ch13's tail. TOC printed ranges:
  ch13 164-177, ch14 178-184, ch15 185-200. PDF has 206 pages, ends "সমাপ্ত" at
  PDF 205 = printed 200.
- **topic_map.json ch1 `learning_outcomes` are fabricated** — cite বঙ্গভঙ্গ ১৯০৫
  and ১৮৫৭-৫৮ সিপাহি বিপ্লব, neither in the real শিখনফল box (printed p.6, which is
  ভাষা আন্দোলন / বৈষম্য / ১৯৫৪→৬৯ / ১৯৭০ নির্বাচন / কর্মসূচি প্রণয়ন). Not in the
  CSV. Other chapters' outcomes look like terse "X সম্পর্কে জানব" paraphrases
  (`05_validate.py --stage topicmap` WARNs "outcome not covered by any topic" for
  ch3-15). Re-transcribe boxes on the redo.
- CSV is 4-column (no Step 10 scope-split, no Step 6 eyeball); `merge_overrides`
  `{}`; `output/…BGS…-merge-candidates.txt` unreviewed. README checkbox
  downgraded from "DONE" to partial.

General guard added to `subjects/bgs.md` ("Verified factual points" section) so a
future Step-7 run doesn't reintroduce the ১৮৪৭ date or the ১৯০৫/১৮৫৭ ch1 outcomes,
and the chapter-map note now documents the k=5 offset + the ch13-15 bug.
This is the 2026 edition: ch2's ১৯৯০ ও ২০২৪ (জুলাই) গণঅভ্যুত্থান topics are real.

**2026-08-30 — the truncation is now caught automatically** (see
[[pipeline-architecture-2026-08]] 2026-08-30 note). `05_validate.py --stage
topicmap` FAILs BGS on: missing Step-4b heading checklist for ch1,4-10,12-15
(ch2/ch11 have theirs; ch3 hand-built as the worked example → fires
"mid-chapter truncation: topics stop around page 40 … pages 45-49 carry 9
unmapped headings"). The BGS finish pass = run `04_extract_headings.py` for the
whole book, fill every `headings/chNN.json`, regenerate each chapter's topic_map
with `07_constrained_prompt.py` + the STEP-0/§8 prompt rules, then 06→08→10→
validate. The ~10/15 chapters with "outcome not covered" + "N/N learning_outcomes
end in জানব" WARNs are all suspected truncations, not just ch3.
