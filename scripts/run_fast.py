"""Fast orchestrator — runs the full pipeline with optimized scripts.

Usage:
    python scripts/run_fast.py "<book folder under ocr/>" <grade> <subject> [--map <csv> --step N --workers 8]

    --step N     run only this step (1-5), then stop
    --workers N  parallel workers for image extraction (default: 8)

Steps:
  1. Validate setup
  2. Extract images (parallel via fast_extract.py)
  3. Check headings (Step 4b — manual agent step)
  4. Check topic_map.json (Step 7 — manual agent step)
  5. Assemble -> merge -> scope_split -> final validate
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OCR_DIR = os.path.join(ROOT, "ocr")
sys.path.insert(0, SCRIPT_DIR)
import _config  # noqa: E402

PY = sys.executable


def sh(*args) -> int:
    return subprocess.call([PY, *args] if args[0].endswith(".py") else list(args),
                           cwd=ROOT)


def die(msg, code=1):
    print("\n" + "=" * 70 + f"\nSTOP: {msg}\n" + "=" * 70)
    sys.exit(code)


def main():
    args = sys.argv[1:]
    cmap = None
    step_only = 0
    workers = 8

    if "--map" in args:
        i = args.index("--map")
        cmap = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--step" in args:
        i = args.index("--step")
        step_only = int(args[i + 1])
        del args[i:i + 2]
    if "--workers" in args:
        i = args.index("--workers")
        workers = int(args[i + 1])
        del args[i:i + 2]

    if len(args) != 3:
        print(__doc__)
        sys.exit(2)
    book, grade, subject = args
    subject = _config.slugify(subject)
    book_dir = os.path.join(OCR_DIR, book)
    mapflag = ["--map", cmap] if cmap else []

    t_total = time.time()

    def validate(stage):
        extra = ["--subject", subject] if stage == "setup" else []
        rc = sh(os.path.join("scripts", "05_validate.py"), "--stage", stage,
                book, *mapflag, *extra)
        if rc:
            die(f"--stage {stage} FAILed. Fix the FAILs above and re-run.")

    # 1 -------------------------------------------------------------- setup ---
    if step_only in (0, 1):
        t = time.time()
        print(f"\n{'='*60}\n  STEP 1: Setup validation\n{'='*60}")
        validate("setup")
        print(f"  [{time.time()-t:.1f}s] Setup OK")

    # 2 ------------------------------------------------------------ extract ---
    if step_only in (0, 2):
        t = time.time()
        print(f"\n{'='*60}\n  STEP 2: Image extraction ({workers} workers)\n{'='*60}")
        chdir = os.path.join(book_dir, "chapters")
        has_images = glob.glob(os.path.join(chdir, "ch*", "*.png"))
        if not has_images:
            # Use fast_extract.py
            import csv as csv_mod
            cmap_path = None
            if cmap:
                cmap_path = cmap if os.path.isabs(cmap) else os.path.join(ROOT, "chapter-maps", cmap)
            else:
                # Auto-detect chapter map
                slug = book.lower().replace(" ", "-").replace("_", "-")
                for f in os.listdir(os.path.join(ROOT, "chapter-maps")):
                    if f.endswith(".csv") and slug[:20] in f.lower():
                        cmap_path = os.path.join(ROOT, "chapter-maps", f)
                        break

            if cmap_path and os.path.exists(cmap_path):
                rc = sh(os.path.join("scripts", "fast_extract.py"),
                        os.path.basename(cmap_path).replace(".csv", ".pdf") if False else book,
                        cmap_path, "--workers", str(workers))
            else:
                die(f"No extracted pages and no chapter map found. Run:\n"
                    f"  python scripts/fast_extract.py <pdf> <chapter_map> --workers {workers}")
        else:
            print(f"  Images already exist ({len(has_images)} files). Use --force to re-extract.")
        validate("extract")
        print(f"  [{time.time()-t:.1f}s] Extraction OK")

    if step_only == 2:
        print(f"\nTotal: {time.time()-t_total:.1f}s")
        return

    # 3 --------------------------------------------------- headings (4b) ----
    if step_only in (0, 3):
        t = time.time()
        print(f"\n{'='*60}\n  STEP 3: Heading check (Step 4b)\n{'='*60}")
        chdir = os.path.join(book_dir, "chapters")
        chapters = sorted({int(re.search(r"ch0*(\d+)", os.path.basename(d)).group(1))
                           for d in glob.glob(os.path.join(chdir, "ch*"))
                           if re.search(r"ch0*\d+$", os.path.basename(d))})
        hdir = os.path.join(book_dir, "headings")
        missing = []
        filled = []
        for n in chapters:
            p = os.path.join(hdir, f"ch{n:02d}.json")
            if not os.path.exists(p):
                missing.append(n); continue
            try:
                d = json.load(open(p, encoding="utf-8"))
            except json.JSONDecodeError:
                missing.append(n); continue
            if d.get("pending") or not d.get("headings"):
                missing.append(n)
            else:
                filled.append(n)

        if missing and os.environ.get("NCTB_SKIP_HEADING_GATE"):
            print(f"  WARNING: {len(missing)} chapters missing headings — "
                  f"continuing (NCTB_SKIP_HEADING_GATE set)")
        elif missing:
            print(f"  {len(filled)}/{len(chapters)} chapters have headings filled")
            sh(os.path.join("scripts", "04_extract_headings.py"), book, *mapflag)
            die(f"Step 4b not done for chapter(s) {', '.join(map(str, missing))}. "
                f"Fill each chNN.json, then re-run.")
        else:
            print(f"  All {len(chapters)} chapters have headings filled")
        print(f"  [{time.time()-t:.1f}s] Headings OK")

    if step_only == 3:
        print(f"\nTotal: {time.time()-t_total:.1f}s")
        return

    # 4 ------------------------------------------------- topic_map (Step 7) --
    if step_only in (0, 4):
        t = time.time()
        print(f"\n{'='*60}\n  STEP 4: Topic map check (Step 7)\n{'='*60}")
        tm = os.path.join(book_dir, "topic_map.json")
        if not os.path.exists(tm):
            die(f"{os.path.relpath(tm, ROOT)} does not exist — do Step 7 "
                f"(prompts/topic_map_prompt.md), then re-run.")
        validate("topicmap")
        print(f"  [{time.time()-t:.1f}s] Topic map OK")

    if step_only == 4:
        print(f"\nTotal: {time.time()-t_total:.1f}s")
        return

    # 5 ------------------------------------ assemble -> merge -> split -> final
    if step_only in (0, 5):
        t = time.time()
        print(f"\n{'='*60}\n  STEP 5: Assemble -> Merge -> Split -> Final\n{'='*60}")
        csv_path = os.path.join("output", f"{book}.csv")
        if sh(os.path.join("scripts", "06_assemble.py"), book, grade, subject):
            die("06_assemble.py failed.")
        if sh(os.path.join("scripts", "08_merge.py"), csv_path):
            die("08_merge.py failed.")
        if _config.load(subject).get("scope_split", {}).get("enabled"):
            if sh(os.path.join("scripts", "12_scope_split.py"), csv_path):
                die("12_scope_split.py failed.")
        else:
            print(f"  (scope_split disabled — CSV stays 4-column)")
        validate("final")
        print(f"  [{time.time()-t:.1f}s] Post-processing OK")

    elapsed = time.time() - t_total
    print(f"\n{'='*70}")
    print(f"  DONE — {book}.csv — {elapsed:.1f}s total")
    print(f"  Next: Step 6 eyeball (every topic vs its page)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
