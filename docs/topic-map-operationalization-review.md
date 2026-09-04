# Topic Map — Operationalization Review

Senior topic-mapping review of what happens *after* the OCR pipeline: using the
map to drive live-class indexing, an in-video AI chatbot, a reusable exam
service, multi-cadence exams, and PRD/asset generation — and running the whole
mapping operation out of Google Sheets with teachers in the loop.

Sheet reviewed: `gid=1227006678` = `business-entrepreneurship` tab, 180 rows,
columns `grade, subject, chapter, topic, scope_note, topic_raw` (same schema the
pipeline emits for every subject).

---

## 1. What exists today

- **One flat hierarchy:** `subject → chapter → topic`. `scope_note` +
  `topic_raw` are display/scoping helpers, not structure.
- **Grain = section heading** (পরিচ্ছেদ / body heading), ~3–15 words. Uneven:
  some rows are whole sub-chapters (`...সুবিধা-অসুবিধা`), some are single terms,
  some `scope_note` cells hold 11-item lists.
- **Key = Bengali label text.** No stable IDs anywhere.
- **~491+ topics** across the finished books; more per the 9–10 set.
- **Known integrity gaps** (from pipeline memory, not yet cleared):
  Science / Accounting / Business-Entrepreneurship / ICT maps are **box-only**
  (built from the শিখনফল box, never reconciled to bodies); **BGS** truncates
  mid-chapter; **Higher Math** is a partial run; chapter-map page-offset bugs
  and OCR misreads fixed in some books, open in others.
- **No** difficulty, question-type, Bloom/cognitive level, marks, prerequisite
  edges, cross-subject links, edition/version, coverage status, or
  question/video counts.

---

## 2. Structural loopholes & bottlenecks (ranked)

### A. No stable `topic_id` — the load-bearing problem

Everything is keyed by Bengali label text. Consequences:

- A spelling fix or wording tweak to a topic **silently detaches** every
  question, video segment, and exam item mapped to it.
- Edition changes (2026 → 2027 NCTB) that merge/split/rename topics break **all**
  historical mappings — directly kills "reuse exam service for years".
- OCR-misread labels have already caused book-wide wrong replacements; the same
  fragility carries into every downstream join.

**Fix:** immutable ID per row, e.g. `BE-9-C01-T07`, assigned once and never
reused. Label becomes a display field. Keep `aliases[]` for old/variant strings.
Version the taxonomy. Retired IDs stay retired.

### B. Flat single-parent tree can't serve both consumers

- RAG / chatbot / asset generation want **fine** grain (one testable idea).
- Teachers / classes / exam blueprints want **coarse** grain (a manageable list).
- A question often spans 2 topics; a concept (e.g. মুদ্রাস্ফীতি) recurs across
  chapters and across subjects (BGS + Finance). A single-parent tree can't say so.

**Fix:** two levels in one tree —
- **Teachable Unit** (coarse): what a class, a video segment, an exam blueprint
  targets. Roughly today's `topic` row, sometimes merged.
- **Concept** (fine): one exam-questionable idea; what RAG chunks, what the
  chatbot cites, what one MCQ hits, what an image/sim brief is built from. Rolls
  up to exactly one Unit.
- Question ↔ Concept is many-to-many; Concept → Unit is a rollup.
- Teachers only ever see Units. Tooling sees Concepts. Exams can target either.

### C. Grain is derived from headings, not from assessment need

Uneven question counts per topic; some topics unassessable, some too broad to
tag precisely; the big `scope_note` bundles are really 6–11 concepts each.

**Fix:** grain rule — *"Can I write a distinct question that is wrong if you
don't know this specific thing?"* → it's a Concept. Explode the `scope_note`
bundles into Concept rows. Tag each Unit `teach_priority` (core / supplementary /
skip) and `assessable` (y/n); tag Concepts `rag_only` where they're needed for
retrieval but never taught or examined. This is exactly the "teachers can't
cover every topic, but RAG can" requirement, made explicit in data.

### D. No question metadata model

Auto-assembling weekly/monthly/daily papers from a blueprint needs, per question:
type (MCQ / CQ / SBA / short), difficulty (3 levels is enough), marks, estimated
time, cognitive level, source (board+year / custom / AI), answer, explanation,
media. None of it exists.

**Fix:** a separate **question-bank** table (schema in §7), never columns bolted
onto the topic sheet.

### E. No coverage / provenance tracking

The map already contains known-weak books, but nothing in the sheet flags
"verified vs box-only vs truncated", "0 questions attached", "not yet on video",
"last reviewed by whom".

**Fix:** per-topic `map_status`, `qbank_count`, `video_count`, `last_reviewed`,
`reviewer`. Refuse mass question-mapping onto any subject whose `map_status` is
`box-only` / `truncated`.

### F. Google Sheets as the system of record

Sheets is fine as an editing surface, fatal as the database: no referential
integrity, no type validation, no audit trail, a deleted row silently orphans
IDs, concurrent teacher edits collide, cross-tab formulas rot past a few tens of
thousands of cells.

**Fix:** source of truth = a real datastore (Postgres / Airtable / any DB).
Google Sheets becomes (a) a **generated read-only taxonomy view** and (b) a
**structured intake + review surface**. A sync job with a validation gate — same
spirit as `scripts/05_validate.py` — moves rows between them.

### G. No teacher mapping workflow or QA loop

"10 questions per class × thousands of classes, teacher free-picks a topic" is an
unbounded manual operation with no second check, no inter-rater agreement, no
backlog plan. Free-typed topic names will fragment the taxonomy within weeks.

**Fix:** §5 (workflow) + §6 (legacy backlog).

### H. Language / encoding fragility

Pure-Bengali keys + OCR noise + zero-width chars + নুকতা variants + English-term
transliteration variants (জিএনপি / GNP / G.N.P.). Any of these detaches a
label-keyed join.

**Fix:** NFC-normalise on write; store canonical + display separately; join on
ID only, so a label typo is cosmetic, never structural.

### I. Multi-edition / curriculum drift

NCTB moved 2013 → 2022 competency curriculum → 2026 partial rollback. The map is
edition-bound; exams "for years" will cross editions.

**Fix:** `curriculum_version` on every row + a **crosswalk table**
(`old_topic_id, new_topic_id, relation ∈ {same, split, merge, new, dropped}`).

### J. No prerequisite / sequence graph

The in-video chatbot ("what should I revise first?") and any adaptive exam need
"what comes before / after this concept". Not captured.

**Fix:** optional `prereq_ids[]` edges, filled incrementally, never blocking a
release.

---

## 3. The five pointers — problem & solution each

### 1. Recorded LIVE class, chaptered like YouTube

- **Need:** time-coded segments → `topic_id`s.
- **Problem:** a 90-min class wanders across 3–8 topics plus revision and Q&A;
  hand-segmenting every class doesn't scale; Bengali ASR is imperfect.
- **Solution:** `video_segment` table (§7). Pre-fill with Bengali ASR + an LLM
  pass that segments the transcript against that subject's Unit list; the teacher
  only nudges boundaries and confirms. Store `mapping_source` (manual / asr /
  llm) + `confidence`.
- **Loophole guarded:** ID-keyed, so later label edits don't orphan timestamps.

### 2. In-video AI chatbot suggestions

- **Need:** current timestamp → `topic_id`s → RAG chunks + suggested questions +
  "watch next".
- **Problem:** Unit grain is too coarse to retrieve precisely; needs Concept-level
  chunks that are actually embedded.
- **Solution:** RAG index keyed by `concept_id`; every chunk carries
  `{subject, chapter, unit_id, concept_id, page, source_type}`. Chatbot context =
  the active segment's Concepts + their `prereq_ids`. Quality gate: a Concept is
  "chatbot-ready" only with ≥ N chunks.

### 3. Reusable exam service, by topic, for years

- **Need:** stable topic identity across years + question metadata + "don't
  repeat within X months per student".
- **Problem:** label-keyed + no difficulty + no exposure tracking + edition
  drift = can't guarantee non-repetition or balanced papers.
- **Solution:** `topic_id` (§2A) + question-bank schema (§2D) + per-student
  `exposure_count` / exposure log + crosswalk (§2I). A `blueprint` object maps
  exam type → `topic_id` weights + difficulty mix.

### 4. Weekly / monthly / daily exams over many topics

- **Need:** automatic paper assembly from a blueprint + syllabus windows
  ("this week = ch3 Units 4–9").
- **Problem:** no blueprint object, no topic weights, no marks/time model;
  teachers can't hand-build a daily paper.
- **Solution:** `blueprint = {cadence, topic_id filter, n_questions, type_mix,
  difficulty_curve, total_marks, duration}`. Generator samples the question bank
  respecting `exposure_count` + difficulty curve; teacher approves. A "syllabus
  window" is a saved `topic_id` set with start/end dates.

### 5. PRD content — educational images, simulations

- **Need:** per-Concept generation briefs; know which Concepts are visual /
  simulation-worthy.
- **Problem:** not every Concept needs an asset; no field marking need or type;
  no dedupe across grades (same concept in Class 6 and Class 9).
- **Solution:** Concept flags `asset_need ∈ {none, diagram, animation,
  interactive, sim}`, `asset_status`, `asset_ids[]`. Generation pipeline consumes
  Concepts where `asset_need ≠ none AND asset_status = absent`. Reuse is by
  `concept_id`, so shared concepts are generated once.

---

## 4. Where the competitors land (for the "what type of topics" question)

- **Chorcha** — Subject → Chapter → **Topic**-wise online exams, "unlimited
  questions" per chapter/topic, gamified (badges, points, leaderboard). Grain:
  chapter + topic; heavy on MCQ volume per node.
- **ই-টেস্টপেপার (etestpaper.net)** — অধ্যায় + টপিক-tagged both **সৃজনশীল (CQ)**
  and **MCQ**; positioned as the digital replacement for printed test papers.
- **SATT Academy E-Question Builder** — custom paper generation filtered by
  **chapter, board question, question type, topic**; CQ + MCQ + math/science
  types.
- **Live MCQ** — subject-wise + chapter-wise practice, plus a **Routine** (exam
  schedule) tool and a retained **question bank of past model tests** for future
  prep — i.e. the "reuse for years" pattern already productised.

Common denominator: everyone keys on **subject → chapter → topic**, tags each
question with **type (MCQ/CQ) + chapter + topic**, and keeps a **retained bank**
for repeat exams. None expose a finer concept layer publicly — that finer layer
is your RAG/asset advantage, not something to copy.

---

## 5. Types of nodes / fields the sheet(s) need (bullet points only)

**Taxonomy tab (one row per Unit or Concept):**

- `topic_id` — immutable, e.g. `BE-9-C01-T07`
- `grade`
- `subject` — slug (`business-entrepreneurship`)
- `chapter_id` + `chapter_title`
- `level` — `unit` | `concept`
- `parent_id` — Unit's `topic_id` for a Concept row; blank for a Unit
- `label` — display (Bengali)
- `aliases` — `;`-joined old/variant strings
- `scope_note` — kept, but bundles exploded into Concept rows
- `order_index` — sequence within chapter
- `curriculum_version` — e.g. `NCTB-2026`
- `teach_priority` — `core` | `supplementary` | `skip`
- `assessable` — `y` | `n`
- `rag_only` — `y` | `n`
- `prereq_ids` — `;`-joined `topic_id`s (optional, incremental)
- `asset_need` — `none` | `diagram` | `animation` | `interactive` | `sim`
- `map_status` — `verified` | `provisional` | `box-only` | `truncated`
- `qbank_count`, `video_count` — auto-filled counters
- `source_pages`
- `last_reviewed`, `reviewer`
- `notes`

**Question-bank tab (separate, one row per question):**

- `qid`
- `topic_ids` — `;`-joined; 1–3 Concept ids
- `stem`, `options`, `answer`, `explanation`
- `type` — `MCQ` | `CQ` | `SBA` | `short`
- `difficulty` — `1` | `2` | `3`
- `marks`, `est_time_sec`
- `cognitive_level` — `recall` | `understand` | `apply` | `analyze`
- `source` — `board:2019` | `custom` | `ai`
- `media_ids`
- `mapping_method` — `auto` | `assisted` | `manual`
- `mapper`, `mapped_date`, `confidence`
- `status` — `pending` | `approved` | `retired`
- `exposure_count`

**Video-segment tab (separate):**

- `segment_id`, `video_id`, `class_date`
- `t_start`, `t_end`
- `topic_ids` — `;`-joined
- `mapping_source` — `manual` | `asr` | `llm`
- `confidence`, `reviewer`

**Exam-blueprint tab (separate):**

- `blueprint_id`, `name`
- `cadence` — `daily` | `weekly` | `monthly` | `term`
- `topic_id_filter`
- `n_questions`, `type_mix`, `difficulty_curve`
- `total_marks`, `duration_min`
- `no_repeat_window_days`

**Crosswalk tab (edition changes):**

- `old_topic_id`, `new_topic_id`
- `relation` — `same` | `split` | `merge` | `new` | `dropped`
- `note`

---

## 6. Running the mapping operation from Google Sheets

**Teachers never free-type a topic.** Structured intake instead:

1. Pick `subject` → `chapter` (dependent dropdown, sourced from the read-only
   taxonomy tab).
2. Pick 1–3 `topic_id`s from a searchable list showing `label` + `id`.
3. Paste the question / upload the image / paste the video timestamp.
4. Pick `type`, `difficulty`, `marks`.
5. Submit → lands in `mapping_inbox` with `status = pending`.

**Validation gate** (a script in the spirit of `05_validate.py`) runs on the
inbox: rejects unknown `topic_id`, empty stem, duplicate, subject/chapter
mismatch — and writes the reason back into the row.

**Review queue:** a second teacher confirms; only `status = approved` rows sync
to the master datastore / question bank. Track `mapper` vs `reviewer` for
inter-rater disagreement rate.

**Sheets holds:** the generated read-only taxonomy tab, the intake inbox, the
review queue, and an auto-refreshed metrics tab (questions per topic, unmapped
topics, pending count, reviewer throughput, disagreement rate). Master data lives
in the DB.

---

## 7. Mapping the existing question backlog

1. Export the current bank → `qid, raw_text, existing_chapter?, image?`.
2. **Auto-suggest pass:** embed each question and each Concept
   (`label` + `scope_note`); return top-5 candidate `topic_id`s with scores.
   Gets 60–80% of the way cheaply.
3. **Teacher UI:** show the 5 candidates as radio buttons + "none / search" —
   mapping becomes one click.
4. **Confidence routing:** score > high → auto-approve as `provisional`;
   mid → human queue; low → manual.
5. **Record** `mapping_method` + `mapper` + `confidence` so the auto rows can be
   re-audited later.
6. **Order:** start with subjects whose `map_status = verified` (Math 9–10,
   Finance and Banking). Mapping questions onto a box-only / truncated map
   (Science, BGS, Accounting, Business-Entrepreneurship, ICT, Higher Math) bakes
   the map's gaps into the question bank. **Fix those maps first.**

---

## 8. Priority order

1. **Freeze a `topic_id` scheme and stamp IDs on every existing row.** Nothing
   downstream is safe until this exists.
2. **Move source-of-truth off Sheets** into a real datastore; regenerate the
   Sheet as a view + intake/review surface with a validation gate.
3. **Fix the known-weak maps** (Science, BGS, Accounting, Business-
   Entrepreneurship, ICT, Higher Math) — per pipeline memory these are
   box-only / truncated / partial — *before* mass question-mapping.
4. **Add the Unit / Concept `level` split** + `teach_priority` / `assessable` /
   `rag_only`; explode the big `scope_note` bundles into Concept rows.
5. **Stand up the question-bank schema** + the embedding auto-suggest mapper for
   the legacy backlog.
6. **Then** layer on: video segments → exam blueprints → RAG index → asset
   generation.

---

## Sources

- Chorcha — <https://play.google.com/store/apps/details?id=com.chorcha.main>,
  <https://apps.apple.com/sg/app/chorcha/id6450657679>
- ই-টেস্টপেপার — <https://www.etestpaper.net/>,
  <https://www.etestpaper.net/features/subjects>
- SATT Academy E-Question Builder — <https://sattacademy.com/e-question-builder>,
  <https://sattacademy.com/test-papers>
- Live MCQ — <https://play.google.com/store/apps/details?id=com.livemcq.livemcq>,
  <https://mwm.ai/apps/live-mcq-tm/1644524044>
