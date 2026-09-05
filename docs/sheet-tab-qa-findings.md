# Google Sheet — Full-Tab QA Findings

Review of every populated tab in the master mapping sheet
(`docs.google.com/spreadsheets/d/11I4QaFd1GZSaFWFCQ9I7UuBBAUpfxZ-jN1y9TZGkmV0`),
looking for spelling errors, meaning/understanding errors, and mis-classification
in the **subject / chapter / topic** columns.

- **Method:** all 32 tabs exported to CSV, run through a structural linter
  (chapter-format, duplicates, encoding, digits, over-long rows), then every
  chapter→topic list read by hand against the NCTB curriculum for that
  subject/grade.
- **Date:** 2026-09-04.
- **Not covered:** 4 empty HSC tabs at the far right
  (`HSC_Accounting 2nd Paper`, `HSC_Business Organization & Management 1st/2nd`,
  `HSC_Finance & Banking 1st/2nd`) — no rows to check.
- Severity: **[H]** breaks meaning / wrong content, **[M]** quality / structural,
  **[L]** cosmetic / consistency.

---

## Tab inventory & health

| Tab | Rows | Verdict |
|---|---|---|
| Class 6 Math | 39 | clean |
| Class 6 Science | 63 | clean |
| Class 6 ICT | 17 | clean (sparse) |
| Class 6 BGS | 38 | minor garbled rows |
| Class 7 Math | 44 | clean, 1 garble |
| Class 7 BGS | 76 | **1 meaning error** |
| Class 7 ICT | 15 | clean (sparse) |
| Class 7 Science | 63 | clean, spelling drift |
| Class 8 Math | 44 | clean |
| Class 8 BGS | 106 | bloat + 1 typo |
| Class 8 ICT | 22 | clean |
| Class 8 Science | 63 | clean |
| SSC \| Finance and Banking | 96 | **several spelling/meaning errors** |
| SSC \| Business Entrepreneurship | 122 | **wrong chapter title + spelling** |
| SSC \| Accounting | 68 | box-only + spelling errors |
| SSC \| Geography | 124 | clean, tiny nits |
| SSC \| BGS | 157 | **Ch2 contaminated + 1 term error** |
| SSC \| Science | 117 | **worst tab — misclassification, garbles, hallucination** |
| SSC \| ICT | 86 | clean |
| SSC \| Physics | 93 | clean |
| SSC \| Higher Math | 156 | **term error + spelling cluster** |
| SSC \| Chemistry | 83 | clean |
| SSC \| Biology | 134 | **1 acronym error** |
| SSC \| General Math | 147 | clean, spelling nits |
| SSC \| Economics | 64 | **every topic duplicated + non-standard chapter format** |
| SSC \| History | 50 | clean, 1 typo |
| HSC Biology | 353 | 1st+2nd paper collision, misfiled rows |
| HSC Chemistry | 392 | 1st+2nd paper collision, bloat |
| HSC Higher Math | 364 | 1st+2nd paper collision, misfiled rows, spelling |
| HSC Physics | 710 | 1st+2nd paper collision, heavy duplication/bloat |
| HSC_Accounting 1st Paper | 159 | raw guide-book dump: meta-rows, run-on topics, missing Ch9 |

---

## Part A — Cross-cutting structural issues

1. **[M] Three different chapter-column formats.** Most tabs use
   `অধ্যায় ১: <title>`. But:
   - `SSC | Economics` uses ordinal words: `প্রথম অধ্যায়:`, `দ্বিতীয় অধ্যায়:` …
   - `HSC_Accounting 1st Paper` uses a hyphen: `অধ্যায়-০১:`
   Any cross-tab sort / dependent-dropdown / join on `chapter` breaks on these.
   Normalise to one format.

2. **[H/M] HSC tabs concatenate 1st- and 2nd-paper into one tab with colliding
   chapter numbers.** `HSC Physics`, `HSC Chemistry`, `HSC Biology`,
   `HSC Higher Math` each contain a full `অধ্যায় ১…N` block for Paper 1 **and
   another** `অধ্যায় ১…N` block for Paper 2, with different titles. The only
   thing distinguishing them is the `subject` cell (`… 1st Paper` /
   `… 2nd Paper`). Filtering "অধ্যায় ২" returns two unrelated chapters.
   Fix: add a `paper` column, or prefix the chapter (`১ম পত্র — অধ্যায় ২`).
   (The structural linter flags these as "CH-VARIANTS"; they are not variants,
   they are collisions.)

3. **[H] `SSC | Economics` — nearly every topic row is duplicated.** ~20 exact
   dupes (each core topic appears twice, sometimes with a stray `Updated Topic`
   column). De-dup before this tab is usable.

4. **[M] `HSC_Accounting 1st Paper` contains non-topic rows.** ~30 rows are
   book-structure artifacts, not teachable topics:
   `বহুনির্বাচনি প্রশ্নাবলি`, `ব্যবহারিক প্রশ্নাবলি`,
   `সৃজনশীল ব্যবহারিক সমস্যা ও সমাধান`,
   `একনজরে এ অধ্যায়ের কতিপয় সংজ্ঞা ও গুরুত্বপূর্ণ তথ্যাবলি`, `ভূমিকা`, `সূচনা`.
   Also its topics are 60–106-char run-on bundles (8+ concepts each) that need
   exploding, and **Chapter 9 (আর্থিক বিবরণী) is missing** (jumps 08 → 10).

5. **[M] Column headers inconsistent.** Standard is
   `grade,subject,chapter,topic,scope_note,topic_raw`. Deviations: `Class 6/7/8`
   tabs and `SSC | Finance and Banking` drop `scope_note,topic_raw`;
   `HSC *` tabs use capitalised `Grade,Subject,Chapter,Topic`;
   `SSC | Biology`, `SSC | Physics`, `SSC | Chemistry` carry a trailing empty
   column; `SSC | Economics` has an extra `Updated Topic` column.

6. **[L] Encoding hygiene.** Many `SSC | Biology`, `SSC | Physics`,
   `SSC | Chemistry`, `SSC | Economics` rows are not NFC-normalised; several have
   trailing spaces (`শ্বসন প্রক্রিয়া `, `রক্ত উপাদানের কাজ `,
   ` ঘর্ষণ হ্রাস-বৃদ্ধির উপায়`). Normalise on write.

---

## Part B — High-severity content errors (fix first)

### SSC | Science  (gid 833821380) — the worst tab
- **[H] Ch2 "জীবনের জন্য পানি" is contaminated with soil topics.** `মাটির pH`,
  `মাটি দূষণের কারণ ও ফলাফল`, `মাটি সংরক্ষণ কৌশল` belong to Ch8 "আমাদের সম্পদ"
  (where they also appear). Remove from Ch2.
- **[H] `জীবঅভিব্ভের সপক্ষে প্রমাণ`** (Ch4) — garbled. Should be
  **`জীবের অভিব্যক্তির সপক্ষে প্রমাণ`** (evidence for evolution).
- **[H] `স্থিতিস্থাপক জড়তা ও গতিজড়তা`** (Ch10) — "স্থিতিস্থাপক" = *elastic*.
  Should be **`স্থিতি জড়তা`** (inertia of rest).
- **[H] `রক্ত ~(রক্তরস, রক্তকোষ, অগুচ্চিকা)`** (Ch3) — **`অগুচ্চিকা` →
  `অণুচক্রিকা`** (platelets).
- **[H] `রক্তের গ্রুপ ~(অ্যান্টিজেন, Rh ফ্যাক্টর, রক্তনীতি)`** (Ch3) —
  `রক্তনীতি` is not a term; expected `অ্যান্টিবডি` / `রক্তদান`.
- **[H] `সামুদ্রিক প্রবাল বৃদ্ধি`** (Ch9, disasters) — "প্রবাল" = *coral*, out of
  place next to sea-level rise. Expected **`জলোচ্ছ্বাস`** (storm surge).
- **[M] `এসিড ছড়ালে শাস্তি`** (Ch7) — incoherent ("if acid is spilled,
  punishment"). Intended either acid-violence law or "করণীয়".
- **[M] Ch1 rows are vague abstractions** (`খাদ্যের অন্তর্ভুক্তিকরণ`,
  `পুষ্টির সমতা`, `প্রধান খাদ্য ও পুষ্টিমূলক ভূমিকা`) — the real Ch1
  (BMI, fast food, মাদকাসক্তি, এইডস, ফিটনেস) is missing. This tab is "box-only"
  and should not receive question-mapping until rebuilt.
- **[M] `কাপাস` → `কার্পাস`** (cotton, Ch6); **`পলিস্টার` → `পলিয়েস্টার`**
  (polyester, Ch6).
- **[M] `তড়িৎ প্রবাহ` and `বিদ্যুৎ প্রবাহ`** are separate rows in Ch11 —
  synonyms, merge.

### SSC | BGS  (gid 1906998603)
- **[H] Ch2 "বাংলাদেশের স্বাধীনতা" is contaminated with post-1971 events.**
  `স্বাধীন বাংলাদেশে গণঅভ্যুত্থান`, `নবইয়ের গণঅভ্যুত্থান`,
  `জুলাই গণঅভ্যুত্থান ও শাসকগোষ্ঠীর পলায়ন`,
  `জুলাই গণঅভ্যুত্থানের সামাজিক, রাজনৈতিক ও অর্থনৈতিক দিক` — 1990 and 2024
  events inside a chapter about the 1971 Liberation War. Also `মুক্তিযুদ্ধে
  পেশাজীবীদের ভূমিকা` appears twice and overlaps `…সাধারণ জনগণ ও পেশাজীবীদের…`
  and `…জনসাধারণের ভূমিকা`. Needs a rebuild / chapter re-assignment.
- **[H] `উপযোগ ও অপ্রাচ্যতা`** (Ch10) — **`অপ্রাচ্যতা` → `অপ্রাচুর্যতা`**
  (scarcity). "অপ্রাচ্যতা" is a corruption.
- **[L] `নারী প্রতি বৈষম্য দূরীকরণে জাতিসংঘ`** (Ch9) → `নারীর প্রতি …`.

### SSC | Business Entrepreneurship  (gid 1227006678)
- **[H] Ch3 title `আর্থিক সংস্থান` is wrong.** Every topic under it is about
  **আত্মকর্মসংস্থান** (self-employment). NCTB Ch3 = "আত্মকর্মসংস্থান".
- **[H] Ch12 title `…থেকে শিক্ষাদীয়`** — `শিক্ষাদীয়` is not a word →
  **`শিক্ষণীয়`**.
- **[H] `বর্তনপ্রণালির ধারণা`** (Ch9) — **`বর্তন` → `বণ্টন`**
  (distribution channel = বণ্টনপ্রণালি).
- **[M] `আর্থায়নের ধারণা` / `আর্থায়নের উৎস`** (Ch8) — NCTB standard is
  **`অর্থায়ন`**, not "আর্থায়ন".
- **[M] `উৎপাদনমূলী শিল্প`** (Ch7) → `উৎপাদনমূলক শিল্প`.
- **[L] scope `আত্তীয়-স্বজন`** (Ch8) → `আত্মীয়-স্বজন`.

### SSC | Finance and Banking  (gid 1184647150)
- **[H] `আদর্শ বিচ্ছিন্নতা ব্যবহারে সিদ্ধান্ত গ্রহণ`** (Ch5) —
  **`বিচ্ছিন্নতা` → `বিচ্যুতি`** (standard deviation = আদর্শ বিচ্যুতি).
- **[H] `খরমশ্রীর নীতি`** (Ch9) — not a word; a garbled bank-principle name
  (list also has গোপনীয়তা, সুনাম, বিনিয়োগ, উন্নয়ন, মিতব্যয়িতা, সাবধানতা…).
  Needs the source heading re-checked.
- **[M] `পরিবারিক অর্থায়ন`** (Ch1) → `পারিবারিক অর্থায়ন`.
- **[M] `উপযুক্তার নীতি`** (Ch1) → `উপযুক্ততার নীতি`.
- **[M] `একক সুদ`** (Ch4) → NCTB term is `সরল সুদ`.
- **[L] `মূদ্রাস্ফীতি`** (Ch13) → `মুদ্রাস্ফীতি`.

### SSC | Higher Math  (gid 438824984)
- **[H] `অবয় ~(Relation)`** (Ch1) — **`অবয়` → `অন্বয়`** (the Bengali term for
  a mathematical *relation*; HSC Higher Math tab spells it correctly).
- **[H] `বর্তনবিধির প্রমাণ`** (Ch12, vectors) — **`বর্তন` → `বণ্টন`**
  (distributive law = বণ্টনবিধি).
- **[M] `শিরংকোণ`** (Ch4, twice) → `শীর্ষকোণ` (vertex angle); `কোন` → `কোণ`
  in `ভূমিসংলগ্ন কোন`, `দুটি কোনের মান`.
- **[M] `বৃত্তস্থের উপপাদ্য ~(Theorem of Intersecting Chords)`** (Ch3) — the
  Bengali label and the English gloss don't match; pick one concept.

### SSC | Biology  (gid 1551211942)
- **[H] `বডি মাস রেশিওর (BMR)`** (Ch5) — **BMR = Basal Metabolic Rate
  (বিপাকীয় হার)**, not "body mass ratio". Wrong expansion of the acronym.

### SSC | Accounting  (gid 1291785113)
- **[H] `খাতিয়ানাভূতকরণ ও হিসাবের জের টানা`** (Ch7) —
  **`খাতিয়ানাভূতকরণ` → `খতিয়ানভুক্তকরণ`**.
- **[M] `হিসাবের চক ~(T-ছক ও চলমান জের ছক)`** (Ch5) — **`চক` → `ছক`**.
- **[L] `আয়-আর্থিক বিবরণীতে প্রয়োগ`** (Ch4) — stray `আয়-` prefix.
- Note: this tab is "box-only" (68 rows for 12 chapters); many body headings
  are missing.

### Class 7 BGS  (gid 1712910354)
- **[H] `৭ই মার্চের গণঅভ্যুত্থানের ঐতিহাসিক ঘটনাবলী`** (Ch1) — 7 March 1971 was
  Bangabandhu's **ভাষণ (speech)**, not a "গণঅভ্যুত্থান". Should be
  **`৭ই মার্চের ভাষণ`**.

### HSC Higher Math  (gid 1965713046)
- **[H] `Argond's Diagram`** (2nd paper Ch2) — misspelled (**Argand's**),
  English inside a Bengali list, **and** misfiled under "যোগাশ্রয়ী প্রোগ্রাম"
  (linear programming) — Argand diagram belongs to জটিল সংখ্যা (Ch3).
- **[M] Misfiled rows:**
  `বিভিন্ন প্রকার ত্রিকোণমিতিক সমস্যা` under বিন্যাস ও সমাবেশ (1st Ch5);
  `ত্রিকোণমিতিক কোণের সম্পর্ক`, `ঘড়ির কাটা সম্পর্কিত সমস্যা` under অন্তরীকরণ
  (1st Ch9); `পরিসরাঙ্ক, চতুর্থক ও গড় ব্যবধানাংক এবং বিভেদাঙ্ক` under
  সমতলে বস্তুকণার গতি (2nd Ch9) — that's statistics, belongs in Ch10.
- **[L] Spelling:** `প্রতিরুপ`/`রুপ` → `প্রতিরূপ`/`রূপ`; `মুলগুলো` → `মূলগুলো`,
  `গুনোত্তর` → `গুণোত্তর`; `তথ্য্যের` → `তথ্যের`; `সম্ভাবতার` → `সম্ভাব্যতার`;
  `ঘড়ির কাটা` → `ঘড়ির কাঁটা`.

---

## Part C — Per-tab notes (everything else)

### Class 6 Math — clean
- [M] `এসব দিয়ে সমস্যা সমাধান` (Ch4) is a context-stripped label (refers to the
  previous row). [M] `বিশদৃশ পদ` (Ch4) → `অসদৃশ পদ`.

### Class 6 Science — clean
- [L] `জীবজগতের শ্রেণীকরণ` (Ch2) → `শ্রেণিকরণ` (current NCTB spelling drops ঈ).
- [L] `গলনাঙ্ক, স্ফুটনাঙ্ক ও শীতলীকরণ` (Ch7) — "শীতলীকরণ" is odd next to
  melting/boiling point; likely `হিমাঙ্ক`.

### Class 6 ICT — clean/sparse
- [L] `তথ্য-যোগাযোগ প্রযুক্তির সম্পর্ক ও গুরুত্ব` sits oddly inside the
  "ওয়ার্ড প্রসেসিং" chapter.

### Class 6 BGS — mostly OK
- Chapter 7 title here is `শিশুর বেড়ে ওঠা ও প্রতিবন্ধকতা: সামাজিকীকরণ` — this is
  **correct** (the repo's `chapter-maps` file has a typo "শিল্পের"; the sheet is
  right).
- [M] `জন্মকথা, সংস্কৃতি, সভ্যতা, ঐতিহ্য, মুক্তিযুদ্ধ` (Ch2) — a scope bundle
  dumped as a topic. [M] `সমস্যার কারণ ও প্রভাব`, `প্রতিরোধ ও নিয়ন্ত্রণে করণীয়`
  (Ch6) — "সমস্যা" unqualified.

### Class 7 Math — clean
- [M] `পরিমাপকে ওজন-তরল পরিমাপ` (Ch3) — garbled, near-dupes
  `ওজন ও তরল আয়তন পরিমাপ`.

### Class 7 ICT — clean/sparse
- [L] `সঠিক পরিভাষায় ওয়ার্ড প্রসেসর কৌশল` (Ch4) — garbled phrasing.

### Class 7 Science — OK
- [L] amoeba spelled three ways: `অ্যামিবা` (Ch1 r5) vs `এন্টামিবা` /
  `এন্টামিবাজনিত` (Ch1 r8-9). Pick one (the book means *Entamoeba*).
- [L] `শ্রেণী` / `নিম্নশ্রেণীর` — old spelling, should be `শ্রেণি`.

### Class 8 Math — clean
- [L] `নিশ্চেদ সেট` (Ch7) → `নিশ্ছেদ সেট` (disjoint). [L] `বৃত্ত ও পাই ($\pi$)`
  (Ch10) — raw LaTeX `$\pi$` left in the cell.

### Class 8 BGS — content OK, structure bloated
- [M] `প্রত্নত্ন ও প্রত্নসম্পদ সংরক্ষণে করণীয়` (Ch2) — **`প্রত্নত্ন` →
  `প্রত্নতত্ত্ব`** (or `প্রত্ননিদর্শন`).
- [M] `ইমারত সরকারি ও বেসরকারি নির্মাণ` (Ch2) — word order garbled.
- [M] Ch6 has 4 near-identical rows (`প্রাকৃতিক পরিবেশের সাথে উন্নয়নের সম্পর্ক`,
  `…উন্নয়নের বৈশিষ্ট্য`, `পরিবেশ ও উন্নয়নের বিভিন্ন দিক`,
  `বাংলাদেশের প্রাকৃতিক পরিবেশ ও উন্নয়ন`).
- [M] Ch8 has 12 rows that are `<group> এর <X>` for X ∈ {ভৌগোলিক অবস্থান,
  জীবনধারা, মিশ্রণ, বিনিময়, সাংস্কৃতিক বৈচিত্র্য} — "মিশ্রণ" and "বিনিময়" rows
  duplicate the same idea. Collapse.
- [M] `সূচক ভিত্তিতে দেশ উন্নয়নে ভূমিকা` (Ch4) — vague/garbled.

### Class 8 ICT — clean.

### Class 8 Science — clean.

### SSC | Geography — high quality
- [L] `শিলা ও খনিজের ধারণা` and `শিলা ও খনিজের ধারণা এবং পার্থক্য` (Ch4) —
  near-dup. [L] `সিন্ডার কোণ` → `সিন্ডার কোন` (cone, not angle).
  [L] `উৎসগতি` (Ch4) — non-standard for river upper-course.

### SSC | ICT — clean
- [L] Ch1 last two rows near-dup (`বিভিন্ন খাতে…প্রয়োগ` /
  `শিক্ষা, স্বাস্থ্য, বাণিজ্যসহ…প্রয়োগ`). [L] `ফাইবারঅপটিক` → `ফাইবার অপটিক`.
  [L] first row of Ch6 repeats the chapter title.

### SSC | Physics — clean
- [L] Ch11 `রোধের শ্রেণি ও সমান্তরাল সমবায়` / `…তুল্য রোধ` — near-dup.
  Scope gap: no Ch14 (জীবন বাঁচাতে পদার্থবিজ্ঞান).

### SSC | Chemistry — clean
- [L] minor near-dups only (`খনিজ সম্পদ… ধারণা` / `…তুলনা`;
  `পরিষ্কারক সামগ্রী` / `…পরিষ্কারকরণ…`).

### SSC | General Math — clean
- [M] parallelogram spelled 3 ways: `সমান্তরিক` (Ch7) / `সমান্তরালিক` (Ch15,
  non-standard) — standard is **`সামান্তরিক`**.
- [L] `সদৃশ বহুভুজ ও সদৃশকোণী` (Ch14) — trailing word dangles.
  [L] `বৃত্তকেন্দ্র ও বৃত্তকলা ক্ষেত্রফল` (Ch16) — likely
  `বৃত্তকলা ও বৃত্তখণ্ডের ক্ষেত্রফল`.

### SSC | History — clean
- [L] `প্রাচীন বিশ্বসভ্যাতার` (Ch2) → `বিশ্বসভ্যতার`. [L] `গ্রীক` → `গ্রিক`.

### SSC | Economics — content fine, see Part A #1 & #3
- Text itself is accurate NCTB content; the problems are the wholesale row
  duplication and the ordinal-word chapter format.

### HSC Biology — see Part A #2
- [M] `মায়োসিস ও এর ধাপ` filed under Ch3 "কোষ রসায়ন" — belongs to Ch2 "কোষ
  বিভাজন"; also spelled `মায়োসিস` here vs `মিয়োসিস` two chapters earlier.
- [L] `গলজি বডি` → `গলগি বডি`.

### HSC Chemistry — see Part A #2
- [M] Ch1 "ল্যাবরেটরির নিরাপদ ব্যবহার" is bloated to 35 rows with many
  near-dups (`…পরিচ্ছন্নকরণ` / `…পরিষ্কারকরণ কৌশল` / `…ধৌতকরণ`;
  `সেমি-মাইক্রো অ্যানালিটিক্যাল পদ্ধতি` / `সেমিমাইক্রো পদ্ধতিতে ব্যবহৃত
  যন্ত্রপাতি`).
- [M] `p-ব্লক মৌলসমূহের সাধারণ ধর্মাবলী` appears twice (Ch3).
- [L] `কেলাসন`/`কেলাসণ`, `সংকরায়ন`/`সংকরায়ণ` inconsistent;
  `রঞ্জিন উপাদান` → `রঞ্জক উপাদান`; `ফাজান এর নীতি` → `ফাযান-এর নীতি`;
  `sp² সংকরায়ণ` uses a superscript while siblings write `sp3` plain.

### HSC Physics — see Part A #2
- [M] Heavy over-granularity + duplication in Ch2 "ভেক্টর" (~50 rows): a run of
  20 one-word rows (`স্বাধীন ভেক্টর`, `সীমাবদ্ধ ভেক্টর`, `সদৃশ ভেক্টর` …) plus
  what looks like two merged extraction passes of the same chapter
  (`স্কেলার গুণন`/`ভেক্টর গুণন` and the যোজন-সূত্র block each recur).
- [L] `স্থানাংক` → `স্থানাঙ্ক`.

### HSC_Accounting 1st Paper — see Part A #1 & #4
- [M] `কন্ট্রিা বা বিপরীত দাখিলা` (Ch2) — **`কন্ট্রিা` → `কন্ট্রা`** (contra).

---

## Part D — Systematic low-severity patterns (fix with a find/replace pass)

| Pattern | Correct | Where |
|---|---|---|
| `বর্তন` (as in বর্তনপ্রণালি / বর্তনবিধি) | `বণ্টন` | SSC Business Entrepreneurship, SSC Higher Math |
| `আর্থায়ন` | `অর্থায়ন` | SSC Business Entrepreneurship |
| `শ্রেণী` / `শ্রেণীবিন্যাস` / `নিম্নশ্রেণীর` | `শ্রেণি` … | Class 6/7 Science, others |
| `কোন` (meaning angle) | `কোণ` | SSC Higher Math Ch4, SSC Geography Ch4 |
| `প্রতিরুপ` / `রুপ` / `মুল` / `গুন` | `প্রতিরূপ` / `রূপ` / `মূল` / `গুণ` | HSC Higher Math |
| `মূদ্রা…` | `মুদ্রা…` | SSC Finance and Banking Ch13 |
| trailing spaces / non-NFC | — | SSC Biology, Physics, Chemistry, Economics |
| raw `$\pi$`, `sp²` vs `sp3` | consistent notation | Class 8 Math, HSC Chemistry |

Also across many tabs: **near-duplicate rows** within a chapter (same concept,
different wording) — the structural linter output
(`scratchpad/structural_report.txt` equivalent) lists every `[DUP]` / `[NEAR-DUP]`
pair; worth a dedup pass tab-by-tab.

---

## Part E — Suggested priority

1. **SSC | Science** and **SSC | BGS Ch2** — rebuild from the book bodies; do not
   map questions onto them. These have genuine misclassification / contamination,
   not just typos.
2. **SSC | Economics** — de-dup rows; normalise chapter format.
3. **HSC Physics / Chemistry / Biology / Higher Math** — add a `paper` column (or
   prefix chapters) so Paper-1/Paper-2 chapters stop colliding; then dedup
   Physics Ch2 and Chemistry Ch1.
4. **HSC_Accounting 1st Paper** — strip meta-rows, explode run-on topics, add the
   missing Chapter 9.
5. **Part B spelling/term fixes** — the [H] items change meaning; safe to fix in
   place (`অবয়→অন্বয়`, `অগুচ্চিকা→অণুচক্রিকা`, `বিচ্ছিন্নতা→বিচ্যুতি`,
   `BMR` expansion, `আর্থিক সংস্থান→আত্মকর্মসংস্থান`, `শিক্ষাদীয়→শিক্ষণীয়`,
   `৭ই মার্চের গণঅভ্যুত্থান→৭ই মার্চের ভাষণ`, `খাতিয়ানাভূতকরণ→খতিয়ানভুক্তকরণ`).
6. **Part D** — one scripted normalisation pass for the systematic spellings and
   encoding.
