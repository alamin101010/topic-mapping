---
name: accounting-issues
description: Known defects in the Class 9-10 Accounting topic map / CSV as of 2026-08-28
metadata: 
  node_type: memory
  type: project
  originSessionId: 8b0d60a9-7a93-4549-8efb-addddaf47290
  modified: 2026-08-29T18:24:36.380Z
---

`ocr/…Accounting…/topic_map.json` was built box-only (2 pages/chapter) — topics
are verb-stripped শিখনফল bullets, missing all body section headings.

Old `08_merge.py` fuzzy pass silently dropped distinct concepts (now fixed by
non-destructive merge, see [[pipeline-architecture-2026-08]]): ch4
`মূলধন ও মুনাফা জাতীয় লেনদেনের পার্থক্য` (chapter's core concept), ch11
`পণ্যের ক্রয়মূল্য নির্ধারণ`, ch6 `নগদ প্রদান জাবেদা`, ch3
`দু তরফা দাখিলা পদ্ধতির সুবিধা`.

Confirmed OCR misreads — now in `config/accounting.json` spelling_corrections:
`দৈত্ব সত্তা`→`দ্বৈত সত্তা`, `চক`→`ছক` (T-form), `ক্ষুধন`→`কুঋণ` (bad debts),
`নগদ বাক্তি`→`নগদ বাট্টা` (cash discount), `জেরুর`→`জেরের`,
`মূলধন হিসাবে পরিবর্তন`→`মূলধন হিসাবের পরিবর্তন`, `প্রতিষ্ঠানিক`→`প্রাতিষ্ঠানিক`.

`chapter-maps/class9-10-accounting.csv` ch12 title has `আন্তঃকর্মসংস্থানমূলক`;
the scan (PDF p.200) reads `আত্মকর্মসংস্থানমূলক` — fix the chapter map.

Fix path: run README §5 runbook — re-extract full ranges, redo Step 7 from bodies.

**2026-08-30 update.** Accounting extraction is no longer box-only — all 12
chapters have their full page range on disk (216 PNGs), and `--stage topicmap`
now passes 0 FAIL (down from the box-paraphrase FAILs). CSV is 6-column, 68 rows.
BUT the topic_map still tracks the outcome box closely in several chapters
(`--stage topicmap` WARNs 56–62% on ch6/ch8) and the ch12 chapter-map typo
(`আন্তঃকর্মসংস্থানমূলক` → scan reads `আত্মকর্মসংস্থানমূলক`) is unconfirmed —
Accounting still owes a proper body reconciliation, not a clean bill. The
2026-08-30 heading-gate (see [[pipeline-architecture-2026-08]]) FAILs
`--stage topicmap` for Accounting now until Step 4b `headings/chNN.json` is
built for every chapter.
