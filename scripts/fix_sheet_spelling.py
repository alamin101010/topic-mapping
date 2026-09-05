"""Apply the spelling/typo corrections from docs/sheet-tab-qa-findings.md
directly to the master Google Sheet.

Scope: spelling errors and orthography only. Does NOT touch the
misclassification / contamination / structural issues (Ch2 of SSC Science &
BGS, HSC paper-collision, Economics row duplication, HSC Accounting meta-rows,
wrong chapter title `আর্থিক সংস্থান`, wrong terms like `স্থিতিস্থাপক জড়তা`,
`রক্তনীতি`, `সামুদ্রিক প্রবাল`, `একক সুদ`, BMR expansion, `খরমশ্রীর নীতি`) —
those need a rebuild or a human call.

Usage:
    python scripts/fix_sheet_spelling.py                 # dry run: print every change, write no cells
    python scripts/fix_sheet_spelling.py --apply         # write the changes

Requires:
    - a populated service-account key (see CREDS_PATH / $GSHEET_CREDS) whose
      client_email has Editor access to the sheet
    - pip install gspread google-auth
"""
from __future__ import annotations
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
CREDS_PATH = os.environ.get(
    "GSHEET_CREDS", os.path.join(ROOT, "bright-fastness-397410-e569326fd692.json")
)
SHEET_KEY = "11I4QaFd1GZSaFWFCQ9I7UuBBAUpfxZ-jN1y9TZGkmV0"
DIFF_OUT = os.path.join(ROOT, "output", "sheet-spelling-fixes-diff.txt")

# Only rewrite cells in these logical columns (never grade / subject).
EDITABLE_COLS = {"chapter", "topic", "scope_note", "topic_raw"}

# mode:
#   "sub"  - replace the substring wherever it appears in an editable cell of this tab
#   "cell" - only when the trimmed cell value equals `find` exactly
CORRECTIONS = [
    ("2025083455", "Class 6 Math", [
        ("বিশদৃশ", "অসদৃশ", "sub", "non-word -> 'unlike terms'"),
    ]),
    ("369857847", "Class 6 Science", [
        ("শ্রেণীকরণ", "শ্রেণিকরণ", "sub", "old orthography"),
    ]),
    ("1721681542", "Class 7 Science", [
        ("নিম্নশ্রেণীর", "নিম্নশ্রেণির", "sub", "old orthography"),
        ("শ্রেণীবিন্যাস", "শ্রেণিবিন্যাস", "sub", "old orthography"),
    ]),
    ("795753235", "Class 8 Math", [
        ("নিশ্চেদ", "নিশ্ছেদ", "sub", "disjoint sets - wrong conjunct"),
    ]),
    ("654729889", "Class 8 BGS", [
        ("প্রত্নত্ন", "প্রত্নতত্ত্ব", "sub", "garbled 'archaeology'"),
    ]),
    ("1227006678", "SSC | Business Entrepreneurship", [
        ("শিক্ষাদীয়", "শিক্ষণীয়", "sub", "non-word -> 'lessons to learn'"),
        ("বর্তনপ্রণালি", "বণ্টনপ্রণালি", "sub", "distribution channel"),
        ("আর্থায়ন", "অর্থায়ন", "sub", "non-standard -> financing"),
        ("উৎপাদনমূলী", "উৎপাদনমূলক", "sub", "typo"),
        ("আত্তীয়-স্বজন", "আত্মীয়-স্বজন", "sub", "typo in scope note"),
    ]),
    ("1184647150", "SSC | Finance and Banking", [
        ("আদর্শ বিচ্ছিন্নতা", "আদর্শ বিচ্যুতি", "sub", "standard deviation"),
        ("পরিবারিক অর্থায়ন", "পারিবারিক অর্থায়ন", "sub", "typo"),
        ("উপযুক্তার নীতি", "উপযুক্ততার নীতি", "sub", "typo"),
        ("মূদ্রাস্ফীতি", "মুদ্রাস্ফীতি", "sub", "typo"),
    ]),
    ("1291785113", "SSC | Accounting", [
        ("হিসাবের চক", "হিসাবের ছক", "sub", "চ/ছ typo -> 'format'"),
        ("খাতিয়ানাভূতকরণ", "খতিয়ানভুক্তকরণ", "sub", "garbled 'posting to ledger'"),
    ]),
    ("864277108", "SSC | Geography", [
        ("সিন্ডার কোণ", "সিন্ডার কোন", "sub", "cinder CONE not angle"),
    ]),
    ("1906998603", "SSC | BGS", [
        ("অপ্রাচ্যতা", "অপ্রাচুর্যতা", "sub", "corruption of 'scarcity'"),
        ("নারী প্রতি বৈষম্য", "নারীর প্রতি বৈষম্য", "sub", "missing র"),
    ]),
    ("833821380", "SSC | Science", [
        ("অগুচ্চিকা", "অণুচক্রিকা", "sub", "platelets"),
        ("কাপাস", "কার্পাস", "sub", "cotton"),
        ("পলিস্টার", "পলিয়েস্টার", "sub", "polyester"),
        ("জীবঅভিব্ভের সপক্ষে প্রমাণ", "জীবের অভিব্যক্তির সপক্ষে প্রমাণ", "cell",
         "garbled 'evidence for evolution'"),
    ]),
    ("438824984", "SSC | Higher Math", [
        ("অবয়", "অন্বয়", "cell", "the term for a mathematical Relation"),
        ("বর্তনবিধি", "বণ্টনবিধি", "sub", "distributive law"),
        ("শিরংকোণ", "শীর্ষকোণ", "sub", "vertex angle"),
        ("ভূমিসংলগ্ন কোন ও উচ্চতা", "ভূমিসংলগ্ন কোণ ও উচ্চতা", "sub", "কোন->কোণ"),
        ("দুটি কোনের মান", "দুটি কোণের মান", "sub", "কোন->কোণ"),
    ]),
    ("1125492063", "SSC | General Math", [
        ("সমান্তরালিক", "সামান্তরিক", "sub", "parallelogram misspelling"),
        ("সমান্তরিক অঙ্কন", "সামান্তরিক অঙ্কন", "sub", "parallelogram misspelling"),
    ]),
    ("1920808558", "SSC | History", [
        ("বিশ্বসভ্যাতার", "বিশ্বসভ্যতার", "sub", "extra আ"),
        ("গ্রীক ও রোমান", "গ্রিক ও রোমান", "sub", "old orthography"),
    ]),
    ("1965713046", "HSC Higher Math", [
        ("Argond's Diagram", "Argand's Diagram", "sub", "Argand misspelled"),
        ("জ্যামিতিক প্রতিরুপ", "জ্যামিতিক প্রতিরূপ", "sub", "ু/ূ"),
        ("পোলার রুপ", "পোলার রূপ", "sub", "ু/ূ"),
        ("মুলগুলো সমান্তর ও গুনোত্তর ক্রমান্বয়ে",
         "মূলগুলো সমান্তর ও গুণোত্তর ক্রমান্বয়ে", "sub", "মুল->মূল, গুন->গুণ"),
        ("তথ্য্যের", "তথ্যের", "sub", "typo"),
        ("সম্ভাবতার পরিমাপ", "সম্ভাব্যতার পরিমাপ", "sub", "typo"),
        ("ঘড়ির কাটা সম্পর্কিত সমস্যা", "ঘড়ির কাঁটা সম্পর্কিত সমস্যা", "sub", "কাটা->কাঁটা"),
    ]),
    ("1202622939", "HSC Chemistry", [
        ("রঞ্জিন উপাদান", "রঞ্জক উপাদান", "sub", "pigment"),
        ("ফাজান এর নীতি", "ফাযান-এর নীতি", "sub", "Fajans' rules"),
    ]),
    ("2103007751", "HSC Physics", [
        ("ত্রিমাত্রিক স্থানাংক", "ত্রিমাত্রিক স্থানাঙ্ক", "sub", "স্থানাঙ্ক"),
    ]),
    ("1449066933", "HSC Biology", [
        ("মায়োসিস ও এর ধাপ", "মিয়োসিস ও এর ধাপ", "sub", "spelling consistency"),
        ("গলজি বডি", "গলগি বডি", "sub", "Golgi"),
    ]),
    ("1005883629", "HSC_Accounting 1st Paper", [
        ("কন্ট্রিা বা বিপরীত দাখিলা", "কন্ট্রা বা বিপরীত দাখিলা", "sub", "contra"),
    ]),
]


def col_letter(idx0: int) -> str:
    n, s = idx0 + 1, ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: pip install gspread google-auth")
        return 1

    if not os.path.exists(CREDS_PATH) or os.path.getsize(CREDS_PATH) == 0:
        print(f"ERROR: service-account key missing or empty: {CREDS_PATH}")
        print("Put the JSON key there (or set $GSHEET_CREDS) and grant its")
        print("client_email Editor access to the sheet, then re-run.")
        return 1

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_KEY)

    lines: list[str] = []
    total = 0
    for gid, tab, rules in CORRECTIONS:
        try:
            ws = sh.get_worksheet_by_id(int(gid))
        except Exception as e:  # noqa: BLE001
            lines.append(f"!! {tab} (gid {gid}): cannot open worksheet: {e}")
            continue
        values = ws.get_all_values()
        if not values:
            continue
        header = [h.strip().lower() for h in values[0]]
        editable_idx = {i for i, h in enumerate(header) if h in EDITABLE_COLS}
        updates = []
        for r, row in enumerate(values[1:], start=2):
            for c, cell in enumerate(row):
                if c not in editable_idx:
                    continue
                new = cell
                hit = None
                for find, repl, mode, note in rules:
                    if mode == "cell":
                        if new.strip() == find:
                            new, hit = repl, note
                    else:
                        if find in new:
                            new, hit = new.replace(find, repl), note
                if hit is not None and new != cell:
                    a1 = f"{col_letter(c)}{r}"
                    updates.append({"range": a1, "values": [[new]]})
                    lines.append(f"  {tab}  {a1}  [{hit}]")
                    lines.append(f"      - {cell}")
                    lines.append(f"      + {new}")
        total += len(updates)
        if updates:
            lines.append(f"== {tab}: {len(updates)} cell(s)")
            if args.apply:
                ws.batch_update(updates, value_input_option="RAW")
        else:
            lines.append(f"== {tab}: nothing to change (already clean?)")

    report = "\n".join(lines)
    print(report)
    os.makedirs(os.path.dirname(DIFF_OUT), exist_ok=True)
    with open(DIFF_OUT, "w", encoding="utf-8") as f:
        f.write(report + f"\n\nTOTAL cells: {total}\napplied: {args.apply}\n")
    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'} — {total} cells. Diff -> {DIFF_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
