"""Step 2 (FAST): Extract chapter page images from a scanned PDF — PARALLEL.

Same as 01_extract_images.py but uses multiprocessing to render pages in parallel.
Typical speedup: 4-8x on multi-core machines.

Usage:
    python fast_extract.py <pdf_name> <chapter_map_csv> [--workers N --force]

    --workers N   number of parallel workers (default: min(8, cpu_count))
    --force       overwrite existing images

After extraction it verifies every chapter got its whole range.
"""
import csv
import os
import sys
import time
from multiprocessing import Pool, cpu_count

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


def _render_page(args):
    """Render a single page to PNG. Runs in a worker process."""
    pdf_path, page_num, output_path, dpi = args
    doc = pymupdf.open(pdf_path)
    pix = doc[page_num].get_pixmap(dpi=dpi)
    pix.save(output_path)
    doc.close()
    return output_path


def extract_chapter_images(pdf_name, chapter_map_csv, max_pages=0, force=False,
                           workers=0):
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

    if not workers:
        workers = min(8, cpu_count())

    doc = pymupdf.open(pdf_path)
    total_pages = doc.page_count
    doc.close()

    print(f"PDF: {pdf_name} ({total_pages} pages)")
    print(f"Workers: {workers}")
    print(f"Extracting {'first %d pages/chapter (FORCED)' % max_pages if max_pages else 'the FULL page range'} "
          f"for {len(chapters)} chapters...")

    t0 = time.time()

    # Build work items for all pages
    work_items = []
    chapter_info = {}  # ch_no -> (want, ch_dir, start_idx, last_idx)

    for ch in chapters:
        ch_dir = os.path.join(chapters_dir, f"ch{ch['chapter_no']:02d}")
        os.makedirs(ch_dir, exist_ok=True)

        start_idx = ch["start_page"] - 1
        last_idx = ch["end_page"]
        if max_pages:
            last_idx = min(last_idx, start_idx + max_pages)
        last_idx = min(last_idx, total_pages)

        want = ch["end_page"] - ch["start_page"] + 1
        chapter_info[ch["chapter_no"]] = (want, ch_dir, start_idx, last_idx)

        for page_num in range(start_idx, last_idx):
            out_path = os.path.join(ch_dir, f"page_{page_num + 1:03d}.png")
            if force or not os.path.exists(out_path):
                work_items.append((pdf_path, page_num, out_path, DPI))

    if work_items:
        print(f"  Rendering {len(work_items)} pages...")
        with Pool(workers) as pool:
            results = pool.map(_render_page, work_items)
        print(f"  Done: {len(results)} pages rendered in {time.time() - t0:.1f}s")
    else:
        print(f"  All pages already extracted. Use --force to re-render.")

    # Verify chapter completeness
    short = []
    for ch in chapters:
        ch_no = ch["chapter_no"]
        want, ch_dir, start_idx, last_idx = chapter_info[ch_no]
        got = len([f for f in os.listdir(ch_dir) if f.startswith("page_")])
        flag = "" if got >= want else f"  <-- SHORT ({got}/{want})"
        print(f"  Chapter {ch_no:>2}: PDF pages {start_idx + 1}-{last_idx}  ({got} pages){flag}")
        if got < want:
            short.append(ch_no)

    total = sum(
        len([f for f in os.listdir(os.path.join(chapters_dir, f"ch{ch['chapter_no']:02d}"))
             if f.startswith("page_")])
        for ch in chapters
    )
    elapsed = time.time() - t0
    print(f"\nDone: {total} images under {os.path.relpath(chapters_dir, SCRIPT_DIR)} "
          f"({elapsed:.1f}s, {workers} workers)")

    if short and not (max_pages and force):
        print(f"\nERROR: chapters {short} did not get their full page range. "
              f"Check start_page/end_page in the chapter map against the PDF.")
        sys.exit(1)
    print("Next: python 05_validate.py --stage extract \"%s\"" % book_name)


if __name__ == "__main__":
    args = list(sys.argv[1:])
    force = False
    workers = 0
    max_pages = 0

    if "--force" in args:
        force = True
        args.remove("--force")

    if "--workers" in args:
        i = args.index("--workers")
        workers = int(args[i + 1])
        del args[i:i + 2]

    for flag in ("--max-pages", "--first-only"):
        if flag in args:
            i = args.index(flag)
            max_pages = int(args[i + 1])
            del args[i:i + 2]

    if len(args) < 2:
        print("Usage: python fast_extract.py <pdf_name> <chapter_map_csv> "
              "[--workers N --force]")
        sys.exit(1)

    extract_chapter_images(args[0], args[1], max_pages, force, workers)
