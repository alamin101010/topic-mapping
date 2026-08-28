"""Step 9: Merge similar topics within each chapter — NON-DESTRUCTIVE.

Usage:
    python 08_merge.py <csv_path>

The fuzzy pass here NEVER deletes a topic on its own. It only:
  - applies the explicit per-chapter rules in config/<subject>.json -> merge_overrides
  - deduplicates exact-duplicate rows
  - REPORTS near-duplicate / mergeable groups to <csv>-merge-candidates.txt for
    you to encode as merge_overrides (then re-run)

Opposite concepts (ক্রয়/বিক্রয়, প্রাপ্তি/প্রদান, সুবিধা/অসুবিধা, and any pair in
config/<subject>.json -> distinct_pairs) are never proposed for merging.

Merge target / rules: README §3.5. Run `05_validate.py --stage final "<book>"`
afterwards — it fails if any topic_map.json topic vanished without a rule.
"""
import csv
import os
import re
import sys
from collections import defaultdict, OrderedDict
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config  # noqa: E402

BUILTIN_MARKERS = [
    ("ক্রয়", "বিক্রয়"), ("প্রাপ্তি", "প্রদান"), ("সুবিধা", "অসুবিধা"),
    ("আয়", "ব্যয়"), ("স্থায়ী", "চলতি"), ("ডেবিট", "ক্রেডিট"),
    ("আমদানি", "রপ্তানি"), ("মূলধন", "মুনাফা"), ("উত্তল", "অবতল"),
    ("অম্ল", "ক্ষার"), ("ধাতু", "অধাতু"), ("লাভ", "ক্ষতি"),
    ("সম্পদ", "দায়"), ("জমা", "উত্তোলন"), ("একতরফা", "দুতরফা"),
]


def ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def word_overlap(a, b):
    wa, wb = set(a.split()), set(b.split())
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


def opposites(a, b, extra_pairs):
    if ratio(a, b) >= 0.985:
        return False
    for x, y in list(BUILTIN_MARKERS) + list(extra_pairs):
        if (y in a) == (y in b) and (x in a) == (x in b):
            continue
        if ratio(a.replace(y, x), b.replace(y, x)) >= 0.95:
            return True
    # a distinct_pairs entry can also be two full topic strings
    for x, y in extra_pairs:
        if {a, b} == {x, y}:
            return True
    return False


def apply_overrides(rows, ch_overrides):
    if not ch_overrides:
        return rows, []
    kept, notes = [], []
    rename = {t: r for t, r in ch_overrides.items() if r not in ("_merge_", "_drop_")}
    for row in rows:
        t = row[3]
        if t in ch_overrides and ch_overrides[t] in ("_merge_", "_drop_"):
            notes.append(f"    override {ch_overrides[t]}: {t}")
            continue
        if t in rename:
            row = row[:3] + [rename[t]]
            notes.append(f"    override rename: -> {rename[t]}")
        if row not in kept:
            kept.append(row)
    return kept, notes


def dedupe(rows):
    seen, out = set(), []
    for row in rows:
        key = tuple(row[:4])
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def find_candidates(rows, extra_pairs, threshold=0.6):
    """Group near-duplicate topics WITHOUT merging. Returns list of groups."""
    topics = [r[3] for r in rows]
    used, groups = set(), []
    for i, a in enumerate(topics):
        if i in used:
            continue
        grp = [a]
        used.add(i)
        for j in range(i + 1, len(topics)):
            if j in used:
                continue
            b = topics[j]
            if opposites(a, b, extra_pairs):
                continue
            if word_overlap(a, b) >= threshold or ratio(a, b) >= 0.82:
                grp.append(b)
                used.add(j)
        if len(grp) > 1:
            groups.append(grp)
    return groups


def merge_csv(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        # If Step 10 (12_scope_split.py) already ran, this CSV has 6 columns.
        # Merge always operates on the canonical 4; re-run Step 10 afterwards.
        header = header[:4]
        rows = [r[:4] for r in reader if len(r) >= 4]

    subject = rows[0][1] if rows else ""
    cfg = _config.load(subject)
    overrides = cfg["merge_overrides"]
    extra_pairs = cfg["distinct_pairs"]
    print(f"config: {cfg['source']}  ({len(overrides)} chapters with merge rules)")

    chapters = OrderedDict()
    for row in rows:
        chapters.setdefault(row[2], []).append(row)

    out, candidate_report = [], []
    for ch_label, ch_rows in chapters.items():
        ch_rows, notes = apply_overrides(ch_rows, overrides.get(ch_label, {}))
        ch_rows = dedupe(ch_rows)
        out.extend(ch_rows)

        groups = find_candidates(ch_rows, extra_pairs)
        if groups or notes:
            candidate_report.append(f'  "{ch_label}": {{')
            for n in notes:
                candidate_report.append(n)
            for grp in groups:
                longest = max(grp, key=len)
                candidate_report.append(f"    # consider merging -> {longest!r}")
                for t in grp:
                    tag = "" if t == longest else '  "_merge_"'
                    candidate_report.append(f'      {t!r}:{tag}')
            candidate_report.append("  }")

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(out)

    print(f"Merged CSV written: {csv_path} ({len(rows)} -> {len(out)} topics)")

    rep_path = re.sub(r"\.csv$", "", csv_path) + "-merge-candidates.txt"
    if candidate_report:
        with open(rep_path, "w", encoding="utf-8") as f:
            f.write("# Suggested merges — review, then add the real ones to\n"
                    "# config/<subject>.json -> merge_overrides, and re-run 08_merge.py.\n"
                    "# Nothing here was merged automatically.\n\n")
            f.write("\n".join(candidate_report) + "\n")
        print(f"Merge candidates for review: {rep_path}")
    elif os.path.exists(rep_path):
        os.remove(rep_path)

    print(f"Next: python 05_validate.py --stage final \"<book-name>\"")
    return csv_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 08_merge.py <csv_path>")
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"CSV not found: {sys.argv[1]}")
        sys.exit(1)
    merge_csv(sys.argv[1])
