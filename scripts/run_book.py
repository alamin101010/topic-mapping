"""One command to run (and gate) a whole book — so every subject goes through
the SAME steps in the SAME order and no gate can be skipped.

    python scripts/run_book.py "<book folder under ocr/>" <grade> <subject> [--map <csv>]

What it does, stopping at the first failure:

  1. 05_validate.py --stage setup     (subjects/<s>.md + config/<s>.json filled,
                                       slug clean, chapter map present)
  2. 01_extract_images.py             (only if ocr/<book>/chapters/ is empty)
     05_validate.py --stage extract
  3. checks ocr/<book>/headings/chNN.json — every chapter filled (Step 4b).
     If any is missing/stub it runs 04_extract_headings.py to create the
     stubs and STOPS: you (or an agent) must fill them, then re-run.
  4. checks ocr/<book>/topic_map.json exists. If not it STOPS: do Step 7
     (see prompts/topic_map_prompt.md), then re-run.
     05_validate.py --stage topicmap
  5. 06_assemble.py  ->  08_merge.py  ->  12_scope_split.py (if scope_split
     enabled in config)  ->  05_validate.py --stage final

The two human/agent steps (fill headings, write topic_map.json) are the only
gaps; everything else runs and is gated automatically. Re-run the command after
each — it is idempotent and resumes.
"""
import glob
import json
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OCR_DIR = os.path.join(ROOT, "ocr")
sys.path.insert(0, SCRIPT_DIR)
import _config  # noqa: E402

PY = sys.executable


def sh(*args) -> int:
    print("\n$ " + " ".join(a if " " not in a else f'"{a}"' for a in args))
    return subprocess.call([PY, *args] if args[0].endswith(".py") else list(args),
                           cwd=ROOT)


def die(msg, code=1):
    print("\n" + "=" * 70 + f"\nSTOP: {msg}\n" + "=" * 70)
    sys.exit(code)


def main():
    args = sys.argv[1:]
    cmap = None
    if "--map" in args:
        i = args.index("--map")
        cmap = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) != 3:
        print(__doc__)
        sys.exit(2)
    book, grade, subject = args
    subject = _config.slugify(subject)
    book_dir = os.path.join(OCR_DIR, book)
    mapflag = ["--map", cmap] if cmap else []

    def validate(stage):
        extra = ["--subject", subject] if stage == "setup" else []
        rc = sh(os.path.join("scripts", "05_validate.py"), "--stage", stage,
                book, *mapflag, *extra)
        if rc:
            die(f"--stage {stage} FAILed. Fix the FAILs above and re-run.")

    # 1 -------------------------------------------------------------- setup ---
    validate("setup")

    # 2 ------------------------------------------------------------ extract ---
    chdir = os.path.join(book_dir, "chapters")
    if not glob.glob(os.path.join(chdir, "ch*", "*.png")):
        die(f"no extracted pages in {os.path.relpath(chdir, ROOT)} — run:\n"
            f'  python scripts/01_extract_images.py "<pdf>.pdf" "<chapter-map>.csv"\n'
            f"then re-run this command.")
    validate("extract")

    # 3 --------------------------------------------------- headings (4b) ----
    chapters = sorted({int(re.search(r"ch0*(\d+)", os.path.basename(d)).group(1))
                       for d in glob.glob(os.path.join(chdir, "ch*"))
                       if re.search(r"ch0*\d+$", os.path.basename(d))})
    hdir = os.path.join(book_dir, "headings")
    missing = []
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
    if missing and os.environ.get("NCTB_SKIP_HEADING_GATE"):
        print(f"\nWARNING: Step 4b heading checklist missing for chapter(s) "
              f"{', '.join(map(str, missing))} — continuing only because "
              f"NCTB_SKIP_HEADING_GATE is set (legacy bridge, not for a done book).")
    elif missing:
        sh(os.path.join("scripts", "04_extract_headings.py"), book, *mapflag)
        die(f"Step 4b heading checklist not done for chapter(s) "
            f"{', '.join(map(str, missing))}. Stubs written under "
            f"{os.path.relpath(hdir, ROOT)}/. Fill each chNN.json from the pages "
            f"(one page at a time), then re-run this command.")

    # 4 ------------------------------------------------- topic_map (Step 7) --
    tm = os.path.join(book_dir, "topic_map.json")
    if not os.path.exists(tm):
        die(f"{os.path.relpath(tm, ROOT)} does not exist — do Step 7 "
            f"(prompts/topic_map_prompt.md: STEP 0 heading inventory, map every "
            f"পরিচ্ছেদ, §8 coverage self-check), then re-run.")
    validate("topicmap")

    # 5 ------------------------------------ assemble -> merge -> split -> final
    csv_path = os.path.join("output", f"{book}.csv")
    if sh(os.path.join("scripts", "06_assemble.py"), book, grade, subject):
        die("06_assemble.py failed.")
    if sh(os.path.join("scripts", "08_merge.py"), csv_path):
        die("08_merge.py failed.")
    if _config.load(subject).get("scope_split", {}).get("enabled"):
        if sh(os.path.join("scripts", "12_scope_split.py"), csv_path):
            die("12_scope_split.py failed.")
    else:
        print(f"\n(scope_split disabled in config/{subject}.json — CSV stays 4-column)")
    validate("final")

    print("\n" + "=" * 70)
    print(f"OK — output/{book}.csv passed setup + extract + topicmap + final.")
    print("Remaining by hand: Step 6 eyeball (every topic vs its page), and "
          "review output/<book>-merge-candidates.txt.")
    print("=" * 70)


if __name__ == "__main__":
    main()
