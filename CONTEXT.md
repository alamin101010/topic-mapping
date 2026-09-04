# NCTB Topic Mapping — Full Pipeline Context

## Project Overview
Extract section headings and map topics from scanned NCTB (National Curriculum and Textbook Board) Bengali textbooks into structured CSV output.

## Completed Pipelines

### 1. General Math (9-10) — COMPLETED
- **PDF**: `Secondary (BV)-2026_Class 9-10_Math_compressed.pdf` (362 pages)
- **Subject slug**: `math`
- **Grade**: `9-10`
- **Chapters**: 17, 344 extracted pages
- **Config**: `config/math.json`
- **Subject profile**: `subjects/math.md`
- **Chapter map**: `chapter-maps/class9-10-math.csv`
- **Output**: `output/Secondary (BV)-2026_Class 9-10_Math_compressed.csv` (164 topics, 0 FAIL, 18 WARN)

### 2. Class 6 Science — COMPLETED
- **PDF**: `books/Class_6_Science_compressed.pdf`
- **Subject slug**: `science6`
- **Grade**: `6`
- **Chapters**: 14, 133 extracted pages
- **Offset k = 5**: PDF page 6 = printed page 1
- **Config**: `config/science6.json`
- **Subject profile**: `subjects/science6.md`
- **Chapter map**: `chapter-maps/class6-science.csv`
- **Output**: `output/Class_6_Science_compressed.csv` (151 topics, 0 FAIL, 4 WARN)

### 3. Class 6 BGS — COMPLETED
- **PDF**: `books/Class_6_BGS_compressed.pdf` (70 pages)
- **Subject slug**: `bgs6`
- **Grade**: `6`
- **Chapters**: 8, 64 extracted pages
- **Offset k = 5**: PDF page 6 = printed page 1
- **Config**: `config/bgs6.json`
- **Subject profile**: `subjects/bgs6.md`
- **Chapter map**: `chapter-maps/class6-bgs.csv`
- **Output**: `output/Class_6_BGS_compressed.csv` (91 topics, 0 FAIL, 0 WARN)

### 4. Class 6 Math — COMPLETED
- **PDF**: `books/Class_6_Math_compressed.pdf` (161 pages)
- **Subject slug**: `math6`
- **Grade**: `6`
- **Chapters**: 8, 153 extracted pages
- **Offset k = 5**: PDF page 6 = printed page 1
- **Config**: `config/math6.json`
- **Subject profile**: `subjects/math6.md`
- **Chapter map**: `chapter-maps/class6-math.csv`
- **Output**: `output/Class_6_Math_compressed.csv` (85 topics, 0 FAIL, 0 WARN)

## Summary Table
| Book | Grade | Subjects | Total Topics | FAIL | WARN |
|------|-------|----------|-------------|------|------|
| General Math | 9-10 | math | 164 | 0 | 18 |
| Class 6 Science | 6 | science6 | 151 | 0 | 4 |
| Class 6 BGS | 6 | bgs6 | 91 | 0 | 0 |
| Class 6 Math | 6 | math6 | 85 | 0 | 0 |
| **Total** | | | **491** | **0** | **22** |

## Chapter Maps

### Class 6 BGS (class6-bgs.csv)
| Ch | Title | Start | End | Pages |
|----|-------|-------|-----|-------|
| 1 | সমাজ বিবর্তনের ইতিহাস | 6 | 14 | 9 |
| 2 | বাংলাদেশের ইতিহাস | 15 | 23 | 9 |
| 3 | বাংলাদেশের সংস্কৃতি ও সমাজ | 24 | 28 | 5 |
| 4 | বাংলাদেশের অর্থনীতি | 29 | 38 | 10 |
| 5 | বাংলাদেশ ও বাংলাদেশের নাগরিক | 39 | 47 | 9 |
| 6 | বাংলাদেশের পরিবেশ | 48 | 53 | 6 |
| 7 | শিল্পের বেড়ে ওঠা ও প্রতিবন্ধকতা: সামাজিকীকরণ | 54 | 60 | 7 |
| 8 | বাংলাদেশ ও আঞ্চলিক সহযোগিতা | 61 | 69 | 9 |

### Class 6 Math (class6-math.csv)
| Ch | Title | Start | End | Pages |
|----|-------|-------|-----|-------|
| 1 | স্বাভাবিক সংখ্যা ও ভগ্নাংশ | 6 | 42 | 37 |
| 2 | অনুপাত ও শতকরা | 43 | 64 | 22 |
| 3 | পূর্ণসংখ্যা | 65 | 81 | 17 |
| 4 | বীজগণিতীয় রাশি | 82 | 100 | 19 |
| 5 | সরল সমীকরণ | 101 | 111 | 11 |
| 6 | জ্যামিতির মৌলিক ধারণা | 112 | 131 | 20 |
| 7 | ব্যবহারিক জ্যামিতি | 132 | 141 | 10 |
| 8 | তথ্য ও উপাত্ত | 142 | 158 | 17 |

## Pipeline Steps (per book)
1. **Extract images**: `python scripts/fast_extract.py "<pdf_name>.csv" "<chapter_map>.csv" --force`
2. **Create headings**: Write `headings/chNN.json` files with `chapter_title`, `heading`, `page` format
3. **Create info files**: Write `headings/chNN_info.json` with chapter metadata
4. **Generate constrained prompts**: `python scripts/07_constrained_prompt.py --subject <slug> "<book_name>" <ch_no>` (per chapter)
5. **Create topic_map.json**: Read page images, generate topics (via vision agent)
6. **Validate topic map**: `python scripts/05_validate.py --stage topicmap "<book_name>"`
7. **Fix FAILs**: One-word topics need head concepts attached
8. **Assemble CSV**: `python scripts/06_assemble.py "<book_name>" <grade> <subject>`
9. **Merge**: `python scripts/08_merge.py "<output_csv>"`
10. **Scope split**: `python scripts/12_scope_split.py "<output_csv>" <subject>`
11. **Final validation**: `python scripts/05_validate.py --stage final "<book_name>"`

## Key Files
- **Configs**: `config/<subject>.json`
- **Subject profiles**: `subjects/<subject>.md`
- **Chapter maps**: `chapter-maps/<book>.csv`
- **Images**: `ocr/<book>/chapters/chNN/page_NNN.png`
- **Headings**: `ocr/<book>/headings/chNN.json`
- **Topic maps**: `ocr/<book>/topic_map.json`
- **Constrained prompts**: `prompts/constrained_chNN.txt`
- **Output CSVs**: `output/<book>.csv`
- **Validation logs**: `output/validation-log.txt`

## Technical Notes
- **Offset k = 5**: All books have 5 front matter pages (cover, preface, TOC). PDF page 6 = printed page 1.
- **PowerShell**: Use `$env:PYTHONIOENCODING='utf-8';` prefix. Use `;` not `&&`.
- **Heading JSON format**: Must use `chapter_title` (not `title`) and `heading` (not `text`), with `page` as string like `"page_007"`.
- **One-word topics FAIL**: Always attach head concept (e.g. `সমাজ` → `সমাজের ধারণা`).
- **Parallel vision tasks**: `task()` calls get cancelled — process chapter-by-chapter directly.
- **fast_extract.py**: Needs `.pdf` extension in the pdf_name argument.

## Do-Not-Auto-Run List
- Higher Math (9-10)
- BGS (9-10) — existing `bgs.json` config is for grade 9-10
- Any book not listed above

## Tools & Scripts
| Script | Purpose |
|--------|---------|
| `fast_extract.py` | Parallel image extraction (multiprocessing) |
| `04_extract_headings.py` | Extract headings from images |
| `07_constrained_prompt.py` | Generate constrained prompts |
| `05_validate.py` | Validate at various stages |
| `06_assemble.py` | Assemble topic_map.json into CSV |
| `08_merge.py` | Merge similar topics |
| `12_scope_split.py` | Split long topics into scope notes |
