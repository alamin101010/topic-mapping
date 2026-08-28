"""Step 10: Split a trailing "(a, b, c ...)" enumeration out of the topic label
into its own scope_note column — NON-DESTRUCTIVE.

Usage:
    python 12_scope_split.py <csv_path>

Reads output/<book>.csv (the Step 9 / 08_merge.py output: 4 columns
grade,subject,chapter,topic) and rewrites it with 6 columns:

    grade,subject,chapter,topic,scope_note,topic_raw

- topic_raw  : the original topic string, verbatim — always kept.
- topic      : the core label = topic_raw with a *trailing* "(...)" removed.
- scope_note : the text that was inside that trailing "(...)", else "".

Only a parenthetical that CLOSES the string is moved. An inline gloss the
sentence runs past — "FCR (খাদ্য রূপান্তর হার) ও মাছের সম্পূরক খাদ্য তৈরি" — is
left untouched. Nothing is merged, dropped or reworded; every original string
survives in topic_raw, which is what `05_validate.py --stage final` checks
against for silent drops.

Idempotent: if the CSV already has a topic_raw column the split is re-derived
from topic_raw, so re-running after a fresh Step 8/9 is safe. Rows with no
trailing (...) get an empty scope_note and topic_raw == topic, so the 6-column
schema is uniform across every book.

STANDARD STEP — run it for every book (config/_TEMPLATE.json ships
scope_split.enabled = true). Config: config/<subject>.json -> scope_split
    { "enabled": true, "max_core_words": 12 }
Only a subject explicitly set "enabled": false (or with no config file at all)
is left at 4 columns.

README: §3.6 (label length + scope notes), §4 Step 10.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config  # noqa: E402

BASE_COLS = ["grade", "subject", "chapter", "topic"]
FULL_COLS = BASE_COLS + ["scope_note", "topic_raw"]

# Aspect words that cannot stand alone as a topic: a core label that is ONLY
# these (or a single word) lost its head concept while being shortened (§3.6).
# Advisory print only — the authoritative WARN is 05_validate.py --stage final,
# which uses the full ATTRIBUTE_NOUNS set + a chapter-title comparison. Keep this
# subset roughly in sync with that list.
ASPECT_ONLY = {
    "ধারণা", "বৈশিষ্ট্য", "গুরুত্ব", "প্রকারভেদ", "প্রকার", "সুবিধা", "অসুবিধা",
    "প্রয়োজনীয়তা", "পার্থক্য", "প্রভাব", "নীতিমালা", "সমস্যা", "উপায়", "কারণ",
    "ধাপ", "গঠন", "কাজ", "ভূমিকা", "উদ্দেশ্য", "ব্যবহার", "শ্রেণিবিভাগ",
    "শ্রেণীবিভাগ", "বিভাগ", "তাৎপর্য", "উদাহরণ", "পদ্ধতি", "প্রক্রিয়া", "বিষয়",
}

# "<core> (<inside>)" where the ')' closes the whole string (no nesting, no tail).
TRAILING_PAREN = re.compile(r"^(.+?)\s*[（(]\s*([^（()）]+?)\s*[）)]\s*$")


def split_topic(raw):
    """(core_label, scope_note). scope_note == '' when there is no trailing (...)."""
    raw = raw.strip()
    m = TRAILING_PAREN.match(raw)
    if not m:
        return raw, ""
    return m.group(1).strip(" ।,;"), m.group(2).strip()


def word_count(s):
    return len([t for t in re.split(r"\s+", s.strip()) if t])


def process(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if any(c.strip() for c in r)]

    subject = rows[0][1] if rows else ""
    cfg = _config.load(subject).get("scope_split", {})
    if not cfg.get("enabled"):
        print(f"scope_split not enabled for '{subject}' — CSV left unchanged.")
        return csv_path
    max_core = int(cfg.get("max_core_words", 12))

    raw_idx = header.index("topic_raw") if "topic_raw" in header else None
    t_idx = header.index("topic") if "topic" in header else 3

    out, n_split, long_after, thin_after = [], 0, [], []
    for r in rows:
        if raw_idx is not None and len(r) > raw_idx and r[raw_idx].strip():
            raw = r[raw_idx]
        else:
            raw = r[t_idx]
        core, scope = split_topic(raw)
        if scope:
            n_split += 1
        if word_count(core) > max_core:
            long_after.append((r[2], core))
        cw = [t.strip(" ।,;:()[]'\"-") for t in re.split(r"\s+", core.strip()) if t]
        if cw and all(w in ASPECT_ONLY or w in ("ও", "এবং", "এর") for w in cw):
            thin_after.append((r[2], core))
        out.append([r[0], r[1], r[2], core, scope, raw.strip()])

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(FULL_COLS)
        w.writerows(out)

    print(f"config: scope_split enabled  max_core_words={max_core}")
    print(f"scope_split: {len(out)} rows, {n_split} moved a trailing (...) into scope_note")
    if long_after:
        print(f"  {len(long_after)} core label(s) still > {max_core} words — review:")
        for ch, t in long_after:
            print(f"    [{ch}] {t}")
    if thin_after:
        print(f"  {len(thin_after)} core label(s) are aspect-words only — head "
              f"concept lost in shortening, restore it (README §3.6):")
        for ch, t in thin_after:
            print(f"    [{ch}] {t}")
    print('Next: python 05_validate.py --stage final "<book-name>"')
    return csv_path


if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("Usage: python 12_scope_split.py <csv_path>")
        sys.exit(1)
    process(sys.argv[1])
