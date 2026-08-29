---
name: pipeline-architecture-2026-08
description: NCTB topic-mapping pipeline gained a validation gate + per-subject config on 2026-08-28
metadata: 
  node_type: memory
  type: project
  originSessionId: 8b0d60a9-7a93-4549-8efb-addddaf47290
  modified: 2026-08-29T18:18:57.427Z
---

On 2026-08-28 the pipeline was hardened so any subject (physics, chemistry, bio,
civics, geography, …) runs the same way and self-checks.

- `scripts/05_validate.py` is now a 3-stage gate: `--stage extract` (box-only
  detector), `--stage topicmap` (bare/one-word topics, orphaned ও/এবং fragments,
  topics that are just verb-stripped learning_outcomes, uncovered outcomes),
  `--stage final` (topic silently dropped between topic_map.json and CSV). Each
  exits nonzero on FAIL. Run after Steps 2, 7, 9.
- `subjects/<subject>.md` (template + `accounting.md`) — subject profile
  prepended to `prompts/topic_map_prompt.md` at Step 7.
- `config/<subject>.json` (template + `accounting.json`) — replaces the global
  `scripts/spelling_corrections.json` + `scripts/merge_overrides.json` (still a
  fallback when no per-subject file). Holds spelling_corrections, merge_overrides,
  distinct_pairs, attribute_nouns_extra. Loaded by `scripts/_config.py`.
- `08_merge.py` is now NON-DESTRUCTIVE: applies explicit merge_overrides + dedupe
  only; near-duplicate groups go to `output/<book>-merge-candidates.txt` for
  review, never auto-dropped. Opposite pairs guarded.
- `06_assemble.py` no longer keyword-drops topics containing প্রয়োগ/শনাক্তকরণ
  (that was deleting real topics); lab filtering is Step 7's job only.
- `scripts/12_scope_split.py` = **Step 10** (added later 2026-08, opt-in per
  subject via `config/<subject>.json` → `scope_split {enabled, max_core_words}`).
  Non-destructive: a TRAILING `(a, b, …)` in a topic label moves to a new
  `scope_note` column; verbatim original kept in `topic_raw`; CSV goes 4→6 cols.
  Inline glosses (paren not closing the string, e.g. `FCR (...) ও …`) left alone.
  `_config.py` exposes `scope_split`; `05_validate.py --stage final` compares
  `topic_raw` when present and WARNs (never FAILs) on labels > `max_core_words`
  or still ending in `(...)`. `08_merge.py` reads only cols 1–4, so order is
  assemble → merge → scope-split → final. Idempotent (re-derives from topic_raw).
  README §3.6 is the single source of truth for label length (3–8 words ideal,
  WARN >12, no minimum) + a decision table (scope_note default / flowing label
  for 1–2 items / drop / split-into-rows). **Now the pipeline STANDARD**
  (later 2026-08): `config/_TEMPLATE.json` ships `scope_split.enabled=true`;
  turned on in agriculture, science, finance-and-banking, accounting configs;
  Step 10 run for all four (rows split: agri 26/105, science 9/120, finance
  4/129, accounting 0/78 — all 6-col now, `topic_raw==topic` where no `()`),
  every `--stage final` green. prompts/topic_map_prompt.md §5b + subjects/
  _TEMPLATE.md carry the convention so future Step 7 maps emit `label (a,b,c)`.

README rewritten 2026-08-28 to be fully agent-executable: §Step 1 has explicit
page-offset (`k`) verification; §Step 2 has a "Why the FULL body not the শিখনফল
box" subsection with the Finance-and-Banking box-bullets-vs-body-topics evidence
table; §Step 7 is spelled out as the agent's procedure (load every PNG in
chapters/chNN/ in order → list body headings → §3.2 → §3.5 → cross-check → write
JSON); §5 runbook and intro reference Finance and Banking as the complete worked
example.

2026-08-28 (later) — **OCR reading-error hardening** after human review found
spelling/reading errors in the Science CSV (box-only map, never reconciled to
bodies; `config` "corrections" guessed from garble → `প্রাত্যহিক` forced to
`প্রাতিষ্ঠানিক` book-wide, `রাফেজ`→`রেফেক্স`, etc.). Changes:
- `scripts/_config.py` new `apply_corrections(text, corrections)` — token-
  boundary-aware find/replace (pattern must start on a non-Bengali-letter
  boundary; trailing edge free for inflections). `06_assemble.py apply_spelling`
  and `05_validate.py` `corrected()` now call it instead of blind `str.replace`.
- `05_validate.py --stage topicmap`: (a) FAILs when `source_pages` spans ≤3 of a
  ≥5-page chapter (honest box-only tell); (b) `spellcheck_bengali()` lexical
  check — runs every topic + chapter-title word through pyenchant/hunspell
  (`bn_BD`/`bn_IN`/`bn`) or repo-local `scripts/dict/bn_BD.{dic,aff}`, WARNs on
  unknowns; single WARN + skip if no dict; `NCTB_NO_SPELLCHECK=1` to silence.
- New per-subject config key `lexicon_extra.words` (valid terms the dict flags).
  `config/_TEMPLATE.json` + `_config.load()` updated; `scripts/dict/README.md`
  explains adding the dictionary.
- README: §4 dated changelog note; Step 7.2 "spelling FROM the body heading, not
  the box"; new "Lexical check" subsection under Step 7; §6.1 table adds
  `lexicon_extra` + boundary-aware/cite-a-page note; runbook step 3 "rm box-only
  topic_map.json and rebuild", step 6 "read topic vs page not vs string".
- `config/science.json`: fixed `প্রাতিহাসিক→প্রাত্যহিক`, added verified fixes
  (`প্রাতিষ্ঠানিক জীবন→প্রাত্যহিক জীবন`, `সংগ্রহলন→সঞ্চালন`,
  `কোলেষ্টেরল/কোলেষ্টরল→কোলেস্টেরল`, `পাকশল্লি→পাকস্থলী`, `নিষ্কাসন→নিষ্কাশন`),
  `distinct_pairs` তন্ত্র→তন্তু, added `lexicon_extra`, `_spelling_notes` with
  page cites. `subjects/science.md` canonical table rebuilt with citations +
  "Known errors still in the shipped box-only CSV" list.
- `chapter-maps/class9-10-science.csv`: ch7 title `অ্যাস, ফারাক`→`অম্ল, ক্ষারক`;
  ch8 start_page 170→174 (overlapped ch7); ch9 `দূর্যোগের`→`দুর্যোগের`; ch11
  `প্রাতিষ্ঠানিক`→`প্রাত্যহিক`.
- Science CSV regenerated (06→08→validate, all green): 6 topic fixes + ch11 title
  fixed, 120 rows unchanged in count. STILL box-only — full Step 2+7 redo from
  bodies still owed. Not fixed by config (needs body re-run): ch6 তন্ত্র→তন্তু
  (fibre) + সূতা→সুতা, ch3 trailing "পরিবহণ" spurious, ch8 "নদীবাহন" (likely
  নদীভাঙন), ch7 "লবণের প্রাতিষ্ঠানিক অবদান". See [[accounting-issues]] (same box-
  only root cause; Accounting/BE/ICT also still owe the redo).

2026-08-30 — **Step-7 mid-chapter-truncation hardening** after BGS ch3 shipped 8
topics covering only পরিচ্ছেদ ৩.১–৩.২ of a chapter running to ৩.৪, with fabricated
`learning_outcomes`, while `--stage topicmap` stayed 0-FAIL. Root cause: the
Step-7 agent read the first ~6 body pages then wrote the rest from general
knowledge; the gate only checked `source_pages` width, never whether topics
spanned the chapter. Changes:
- **Step 4b is now MANDATORY** — `scripts/04_extract_headings.py` writes
  `ocr/<book>/headings/chNN_info.json` (per-page heading prompt + image list) and
  a stub `chNN.json`; an LLM page-by-page pass fills `chNN.json`
  (`{chapter, chapter_title, headings:[{page,heading}]}`). It reads the chapter
  map for titles; never clobbers an already-filled `chNN.json`.
- `05_validate.py --stage topicmap` new checks (helpers `load_headings`,
  `heading_match`): FAIL when `headings/chNN.json` is missing or an unfilled stub
  (`pending:true` / empty); FAIL "mid-chapter truncation" when earlier headings
  map but the final quarter of the page range has ≥2 headings and NO topic maps
  to any of them; WARN on <60% heading coverage, <0.5 topics/page (span ≥12),
  ≥half of `learning_outcomes` ending in `জানব` (paraphrased not transcribed), and
  topics matching no heading and no outcome (possible invention).
  `NCTB_SKIP_HEADING_GATE=1` downgrades the missing-checklist FAIL to WARN for a
  legacy book mid-migration — NOT for a book being called done.
- `prompts/topic_map_prompt.md`: blocking **STEP 0** per-page heading inventory
  before any topic; new **§1b** (transcribe `learning_outcomes` verbatim, no
  `X সম্পর্কে জানব` paraphrase, no invented bullets); new **§8** coverage
  self-check (every পরিচ্ছেদ represented, last topic on a final page, ≳0.5
  topics/page, nothing invented).
- README: §4 gate blurb + dated changelog note; new "Step 4b" section before
  Step 7; runbook step 2b; §5.1 done-definition adds "filled heading checklist +
  no truncation, NCTB_SKIP_HEADING_GATE unset"; troubleshooting rows; dir tree +
  script list add `04_extract_headings.py` / `07_constrained_prompt.py` /
  `headings/`.
- SIDE EFFECT: the gate now FAILs `--stage topicmap` for ALL previously-green
  books (Finance, Agriculture, Science, Accounting, BE, ICT) until Step 4b is
  backfilled. Finance + Agriculture just need the backfill; the other four still
  owe their body re-run. `ocr/…BGS…/headings/ch03.json` was hand-built as the
  worked example (it makes the ch3 truncation FAIL fire).
- `07_constrained_prompt.py` already existed (bakes `chNN.json` into the Step-7
  prompt as a hard checklist); it was used for BGS ch2 + ch11 only, which is why
  those two chapters are dense/complete and ch3–ch15 are thin. See [[bgs-issues]].

Book status (§5 runbook):
- **Finance and Banking** — DONE 2026-08-28 from full chapter bodies. 13 chapters,
  129 topics. `subjects/finance-and-banking.md` + `config/finance-and-banking.json`
  created; chapter-map rewritten to PDF page numbers (printed + 5). All 3 validate
  stages pass. merge_overrides empty (fuzzy candidates reviewed, all distinct).
- Science, Accounting, Business Entrepreneurship, ICT — still box-only, fail
  `--stage extract`. Redo per runbook. See [[accounting-issues]].
