"""Step 2: Extract chapter page images from a scanned PDF.

Extracts the FULL page range (start_page..end_page) of every chapter from the
chapter map into ocr/<book>/chapters/chNN/. Topics are read from the chapter
BODY, not just the শিখনফল box on page 1-2 (README Step 2 / Step 7), so a partial
extraction is treated as an error.

Usage:
    python 01_extract_images.py <pdf_name> <chapter_map_csv> [--max-pages N --force]

    (no flags)      extract every page of every chapter  <-- always use this
    --max-pages N   cap each chapter at its first N pages. REQUIRES --force,
                    because it reproduces the box-only bug. Debug use only.

After extraction it verifies every chapter got its whole range and exits
nonzero if not. Run `05_validate.py --stage extract "<book>"` next.
"""
import csv
import os
import sys

import pymupdf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(SCRIPT_DIR, "..", "books")
OCR_DIR = os.path.join(SCRIPT_DIR, "..", "ocr")
CHAPTER_MAPS_DIR = os.path.join(SCRIPT_DIR, "..", "chapter-maps")

DPI = 200


def resolve_map(chapter_map_csv: str) -> str:
    if os.path.isabs(chapter_map_csv) and os.path.exists(chapter_map_csv):
        return chapter_map_csv
    p = os.path.join(CHAPTER_MAPS_DIR, chapter_map_csv)
    return p if os.path.exists(p) else chapter_map_csv


def extract_chapter_images(pdf_name, chapter_map_csv, max_pages=0, force=False):
    pdf_path = os.path.join(BOOKS_DIR, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    if max_pages and not force:
        print(f"REFUSED: --max-pages {max_pages} without --force reproduces the "
              f"box-only extraction bug. Drop --max-pages (recommended) or add "
              f"--force if you really mean it.")
        sys.exit(2)

    csv_path = resolve_map(chapter_map_csv)
    if not os.path.exists(csv_path):
        print(f"Chapter map not found: {csv_path}")
        sys.exit(1)

    chapters = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            chapters.append({
                "chapter_no": int(row["chapter_no"]),
                "chapter_title": row["chapter_title"],
                "start_page": int(row["start_page"]),
                "end_page": int(row["end_page"]),
            })

    book_name = pdf_name[:-4] if pdf_name.lower().endswith(".pdf") else pdf_name
    chapters_dir = os.path.join(OCR_DIR, book_name, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    print(f"PDF: {pdf_name} ({doc.page_count} pages)")
    print(f"Extracting {'first %d pages/chapter (FORCED)' % max_pages if max_pages else 'the FULL page range'} "
          f"for {len(chapters)} chapters...")

    total = 0
    short = []
    for ch in chapters:
        ch_dir = os.path.join(chapters_dir, f"ch{ch['chapter_no']:02d}")
        os.makedirs(ch_dir, exist_ok=True)

        start_idx = ch["start_page"] - 1
        last_idx = ch["end_page"]  # exclusive
        if max_pages:
            last_idx = min(last_idx, start_idx + max_pages)
        last_idx = min(last_idx, doc.page_count)

        want = ch["end_page"] - ch["start_page"] + 1
        got = 0
        for page_num in range(start_idx, last_idx):
            pix = doc[page_num].get_pixmap(dpi=DPI)
            pix.save(os.path.join(ch_dir, f"page_{page_num + 1:03d}.png"))
            got += 1
            total += 1
        flag = "" if got >= want else f"  <-- SHORT ({got}/{want})"
        print(f"  Chapter {ch['chapter_no']:>2}: PDF pages {start_idx + 1}-{last_idx}  ({got} pages){flag}")
        if got < want:
            short.append(ch["chapter_no"])

    doc.close()
    print(f"\nDone: {total} images under {os.path.relpath(chapters_dir, SCRIPT_DIR)}")

    if short and not (max_pages and force):
        print(f"\nERROR: chapters {short} did not get their full page range. "
              f"Check start_page/end_page in the chapter map against the PDF.")
        sys.exit(1)
    print("Next: python 05_validate.py --stage extract \"%s\"" % book_name)


if __name__ == "__main__":
    args = list(sys.argv[1:])
    max_pages, force = 0, False
    if "--force" in args:
        force = True
        args.remove("--force")
    for flag in ("--max-pages", "--first-only"):
        if flag in args:
            i = args.index(flag)
            max_pages = int(args[i + 1])
            del args[i:i + 2]

    if len(args) < 2:
        print("Usage: python 01_extract_images.py <pdf_name> <chapter_map_csv> "
              "[--max-pages N --force]")
        sys.exit(1)

    extract_chapter_images(args[0], args[1], max_pages, force)
