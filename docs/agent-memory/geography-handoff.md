---
name: geography-handoff
description: "Class 9-10 Geography — vision-capable agent handoff. Book downloaded; config/subjects scaffold ready; an earlier 15-chapter Google sheet exists but was NOT pipeline-built and differs from the PDF outline (Forma 1-29). A vision-capable agent must do Steps 1/4b/7."
metadata:
  node_type: memory
  type: task
  modified: 2026-08-30
---

# Geography handoff — run the pipeline's vision steps

The geometry/mechanics are done. **What remains is the three vision steps.**

## Ready now
- `books/Secondary (BV)-2026_Class 9-10_geography_compressed.pdf` — 238 pages,
  scanned, **no text layer** (verified), 68 MB, full download.
- `config/geography.json` — scaffold populated (`subject: geography`,
  `scope_split.max_core_words: 5`, real `distinct_pairs` + `attribute_nouns_extra`).
  `spelling_corrections`/`lexicon_extra` deliberately empty — **enroll each fix ONLY
  after reading the page it came from** and cite the PDF page.
- `subjects/geography.md` — subject profile (prepended to the Step-7 prompt).
  Contains the old-sheet watchlist + a list of old-sheet structural defects NOT to
  re-import.
- `docs/agent-memory/geography-sheet-export.csv` — the earlier Google-sheet export
  (469 rows). **Reference only; not pipeline-built.** Its 15-chapter structure is a
  hypothesis, not ground truth.
- `.vscode/launch.json` note: the Validate/Assemble configs pass a subject name into
  an arg that expects a **book name** under `ocr/` — fix if you use them.

## ⚠️ Structure question — confirm on the TOC before anything else
The PDF's bookmark outline is `Bhugol-9 Forma-1 … Forma-29` (each ~8 pages) plus a
`Bhugol-9-10 (Combine)` cover — i.e. **NOT the sheet's 15-chapter layout**. Open the
সূচিপত্র (TOC) pages on the printed book and decide:

- Is the book actually organized in ~15 অধ্যায় (then `Forma` is just the section
  label of the combined PDF and the sheet's titles are a good starting point)?
- Or is it organized differently (29 অভিজ্ঞতা/সেশন, per-class parts)? Then the sheet
  is from a different edition and you build the chapter list fresh from the TOC.

Either way **the TOC is the source of truth** for chapter titles + page numbers, and
the chapter-opener pages are the authority for spelling.

## What the vision agent must do (in order)

### Step 1 — chapter map
1. Dump the first ~14 pages (`python -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); [d[i].get_pixmap(dpi=150).save(f'p{i+1:03d}.png') for i in range(min(14,d.page_count))]" "books/Secondary (BV)-2026_Class 9-10_geography_compressed.pdf"`) and read them.
2. Find the সূচিপত্র; record `chapter_no,chapter_title,start_page,end_page` with **PDF
   page numbers** (printed + offset k). Derive k from the chapter-1 opener (দ্বিতীয়
   অধ্যায় + শিখনফল box = PDF page N that prints as printed 1), spot-check at the last
   chapter too. See README §Step 1 / bgs chapter-map note (BGS had k=5; verify fresh).
3. Write `chapter-maps/class9-10-geography.csv` (header
   `chapter_no,chapter_title,start_page,end_page`, no BOM, ASCII-safe rows: quoted as needed).
4. If the TOC title and opener title differ, use the **opener** spelling.

### Step 2 — extract (mechanical, but run it)
```
python scripts/05_validate.py --stage setup "Secondary (BV)-2026_Class 9-10_geography_compressed" --subject geography
python scripts/01_extract_images.py "Secondary (BV)-2026_Class 9-10_geography_compressed.pdf" "class9-10-geography.csv"
python scripts/05_validate.py --stage extract "Secondary (BV)-2026_Class 9-10_geography_compressed"
```
`--stage extract` must PASS (every chapter = its full page range).

### Step 4b — heading checklist (MANDATORY)
```
python scripts/04_extract_headings.py "Secondary (BV)-2026_Class 9-10_geography_compressed" [--chapter N]
```
For every chapter: open `ocr/…geography…/headings/chNN_info.json`, then walk the
chapter pages **one page at a time** and REPLACE the stub `chNN.json` with the real
per-page heading list (schema in the info file). Do not skip pages; do not stop early.

### Step 7 — topic map (THE AGENT'S JOB)
Per README §7 + `prompts/topic_map_prompt.md` (STEP 0 inventory first, с§8 coverage
self-check). Load `subjects/geography.md` + every page of `ocr/…geography…/chapters/chNN/`.
Write `ocr/Secondary (BV)-2026_Class 9-10_geography_compressed/topic_map.json` (§3.4
schema, one object per chapter). Then:
```
python scripts/05_validate.py --stage topicmap "Secondary (BV)-2026_Class 9-10_geography_compressed"
```
Fix until **0 FAIL + 0 unresolved lexical WARN**.

Apply, while mapping, the old-sheet lessons (details in `subjects/geography.md`):
- Uniform `chapter` value per chapter (ch3 must not split into two titles).
- Never drop head nouns: `বসতি স্থাপনের প্রাকৃতিক নিয়ামক`, `জনসংখ্যা পরিবর্তনের প্রাথমিক পর্যায়`.
- Merge concept-aspect chains and cause+effect pairs into one row; put instance lists
  in a trailing `(a, b, c …)` (→ scope_note).
- No `মানচিত্রে X` skill/duplicate rows — those are exercises.
- Check every watchlist suspect against its printed page before accepting/refixing.

### Steps 8-10 (mechanical, gates)
```
python scripts/06_assemble.py "Secondary (BV)-2026_Class 9-10_geography_compressed" "9-10" "geography"
python scripts/08_merge.py "output/Secondary (BV)-2026_Class 9-10_geography_compressed.csv"
python scripts/12_scope_split.py "output/Secondary (BV)-2026_Class 9-10_geography_compressed.csv"
python scripts/05_validate.py --stage final "Secondary (BV)-2026_Class 9-10_geography_compressed"
```
Review `output/…-merge-candidates.txt`, promote real merges to
`config/geography.json → merge_overrides`, re-run. End = **6-column CSV, all three
stages 0 FAIL + 0 unresolved lexical WARN**, `max_core_words=5`. Then Step 6 eyeball
(100% of rows vs the page).

## Blocked-on
This session's model cannot read images. The command sequence above is runnable from a
vision-capable model/agent in this repo right now; this file (plus the README, which is
the complete spec) is the full procedure.