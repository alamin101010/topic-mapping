"""Step 4b (MANDATORY before Step 7): extract section headings from the pages.

Reads each chapter's page images and, via an LLM vision pass, records the actual
section / sub-section headings printed in the scan. The result —
`ocr/<book>/headings/chNN.json` — is the page-anchored ground truth that
`05_validate.py --stage topicmap` checks the Step-7 map against.

Why it is mandatory: without a per-page heading list there is no way to tell that
a Step-7 map covered only the first few পরিচ্ছেদ and stopped (the BGS ch3 bug:
mapped ৩.১–৩.২, silently dropped ৩.৩–৩.৪), or that a topic was invented rather
than read off a page. `--stage topicmap` now FAILs when `headings/chNN.json` is
missing or is still an unfilled stub (bypass for a legacy book mid-migration:
`NCTB_SKIP_HEADING_GATE=1`).

Usage:
    python 04_extract_headings.py "<book folder under ocr/>" [--chapter N] [--map <csv>]

For every chapter this writes two files under ocr/<book>/headings/:
  * chNN_info.json  — the extraction prompt + the ordered image list (input for
                      the LLM pass)
  * chNN.json       — a STUB {"chapter": N, "chapter_title": "...",
                      "headings": [], "pending": true}. An existing non-stub file
                      is never overwritten.

The LLM pass then REPLACES each chNN.json with the real list, shape:

    {
      "chapter": 3,
      "chapter_title": "সৌরজগৎ ও ভূমণ্ডল",
      "headings": [
        {"page": "page_032", "heading": "পরিচ্ছেদ ৩.১ : সৌরজগৎ"},
        {"page": "page_032", "heading": "সূর্য"},
        ...
      ]
    }

Then: `07_constrained_prompt.py <book> <N>` bakes that list into the Step-7
prompt, run Step 7, then `05_validate.py --stage topicmap`.
"""
import argparse
import csv
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OCR_DIR = os.path.join(ROOT, "ocr")
CHAPTER_MAPS_DIR = os.path.join(ROOT, "chapter-maps")


def get_chapter_dirs(book_dir):
    chapters_dir = os.path.join(book_dir, "chapters")
    if not os.path.isdir(chapters_dir):
        return []
    return [
        os.path.join(chapters_dir, d)
        for d in sorted(os.listdir(chapters_dir))
        if d.startswith("ch") and os.path.isdir(os.path.join(chapters_dir, d))
    ]


def get_page_images(chapter_dir):
    return [
        os.path.join(chapter_dir, f)
        for f in sorted(os.listdir(chapter_dir))
        if f.startswith("page_") and f.endswith((".png", ".jpg"))
    ]


def slugify_book(book: str) -> str:
    import re
    m = re.search(r"Class\s*([0-9\-]+)_([A-Za-z &]+)", book)
    if m:
        return "class{}-{}".format(
            m.group(1).strip(),
            m.group(2).strip().lower().replace(" ", "-").replace("&", "and"),
        )
    return book.lower().replace(" ", "-")


def load_titles(book: str, explicit_map: str | None):
    """Return {chapter_no: (title, start, end)} from the chapter map, or {}."""
    path = explicit_map
    if path and not os.path.isabs(path):
        path = os.path.join(CHAPTER_MAPS_DIR, path)
    if not path or not os.path.exists(path):
        path = os.path.join(CHAPTER_MAPS_DIR, slugify_book(book) + ".csv")
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    out[int(row["chapter_no"])] = (
                        row["chapter_title"].strip(),
                        int(row["start_page"]),
                        int(row["end_page"]),
                    )
                except (KeyError, ValueError, TypeError):
                    pass
    return out


HEADING_PROMPT = """You are extracting SECTION HEADINGS from ONE scanned page of a
Bengali NCTB textbook chapter.

Return a JSON array of the section / sub-section headings printed on THIS page, in
top-to-bottom order. A heading is bold or larger-font text that starts a section
or sub-section — including পরিচ্ছেদ X.Y lines and named sub-sections
(e.g. "সূর্য (Sun)", "আহ্নিক গতি").

EXCLUDE: the chapter title (e.g. "তৃতীয় অধ্যায়"), the শিখনফল / "এ অধ্যায় শেষে
আমরা –" box, figure captions ("চিত্র X.X :"), "কাজ" boxes, table headers, page
numbers, running headers/footers, and the end-of-chapter
"নমুনা প্রশ্ন / বহুনির্বাচনি / সৃজনশীল / সংক্ষিপ্ত-উত্তর" material.

If the page has no heading, return []. Output ONLY the JSON array.
Example: ["পরিচ্ছেদ ৩.৩ : পৃথিবীর গতি", "আহ্নিক গতি"]"""


def main():
    ap = argparse.ArgumentParser(description="Step 4b — extract section headings")
    ap.add_argument("book_name", help="book folder name under ocr/")
    ap.add_argument("--chapter", type=int, help="process only this chapter number")
    ap.add_argument("--map", help="chapter-map csv (auto-guessed if omitted)")
    args = ap.parse_args()

    book_dir = os.path.join(OCR_DIR, args.book_name)
    if not os.path.isdir(book_dir):
        print(f"Book directory not found: {book_dir}")
        sys.exit(1)

    headings_dir = os.path.join(book_dir, "headings")
    os.makedirs(headings_dir, exist_ok=True)
    titles = load_titles(args.book_name, args.map)

    chapter_dirs = get_chapter_dirs(book_dir)
    if not chapter_dirs:
        print(f"No chapter dirs in {book_dir}/chapters/")
        sys.exit(1)

    print(f"Book: {args.book_name}")
    print(f"Output: {os.path.relpath(headings_dir, ROOT)}/\n")
    made, kept = 0, 0

    for ch_dir in chapter_dirs:
        ch_name = os.path.basename(ch_dir)
        ch_no = int("".join(c for c in ch_name if c.isdigit()) or 0)
        if args.chapter and ch_no != args.chapter:
            continue
        images = get_page_images(ch_dir)
        if not images:
            print(f"  {ch_name}: no images, skipped")
            continue
        title = titles.get(ch_no, ("", 0, 0))[0]

        info = {
            "chapter": ch_no,
            "chapter_title": title,
            "chapter_dir": os.path.relpath(ch_dir, ROOT),
            "images": [os.path.relpath(p, ROOT) for p in images],
            "total_pages": len(images),
            "prompt": HEADING_PROMPT,
            "output_schema": {
                "chapter": ch_no,
                "chapter_title": title,
                "headings": [{"page": "page_0NN", "heading": "<verbatim heading>"}],
            },
        }
        with open(os.path.join(headings_dir, f"{ch_name}_info.json"), "w",
                  encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        stub_path = os.path.join(headings_dir, f"{ch_name}.json")
        if os.path.exists(stub_path):
            try:
                with open(stub_path, encoding="utf-8") as f:
                    existing = json.load(f)
                if not existing.get("pending") and existing.get("headings"):
                    kept += 1
                    print(f"  {ch_name}: {len(images)} pages — chNN.json already filled, kept")
                    continue
            except (json.JSONDecodeError, OSError):
                pass
        with open(stub_path, "w", encoding="utf-8") as f:
            json.dump({"chapter": ch_no, "chapter_title": title,
                       "headings": [], "pending": True}, f,
                      ensure_ascii=False, indent=2)
        made += 1
        print(f"  {ch_name}: {len(images)} pages — wrote stub {ch_name}.json")

    print(f"\n{made} stub(s) written, {kept} kept.")
    print("NEXT: run the LLM heading pass — for each chNN_info.json, feed the "
          "prompt + every listed image (one page at a time) and REPLACE "
          "chNN.json with the real headings list (schema in the info file).")
    print("Then: 07_constrained_prompt.py, Step 7, 05_validate.py --stage topicmap.")


if __name__ == "__main__":
    main()
