"""Step 8: Assemble topic maps into CSV output.

Usage:
    python 06_assemble.py <book_name> <grade> <subject>

Example:
    python 06_assemble.py "Secondary (BV)-2026_Class 9-10_Science_compressed" "9-10" "science"

Reads ocr/<book_name>/topic_map.json, applies spelling corrections from
config/<subject>.json (falls back to scripts/spelling_corrections.json), converts
chapter numbers to Bengali numerals, and writes output/<book_name>.csv with
csv.QUOTE_ALL.

This step does NOT fix bad topics. Its atomizer only strips a trailing pedagogy
verb and splits on standalone এবং; it never splits on ও and never emits a
fragment shorter than 2 tokens. Topics must already be correct per README
§3.2 / §3.5 in topic_map.json. Run `05_validate.py --stage topicmap` first.
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _config  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")
OCR_DIR = os.path.join(SCRIPT_DIR, "..", "ocr")

BENGALI_DIGITS = "০১২৩৪৫৬৭৮৯"

# NOTE: experimental/lab filtering (পরীক্ষণ, স্লাইড, প্রস্থচ্ছেদ ...) is done in
# Step 7 by the LLM, which has the chapter context to tell a lab drill from a
# real concept. This mechanical step must NOT blanket-drop on keywords —
# doing so deleted real topics like "ডেবিট ও ক্রেডিট পক্ষ শনাক্তকরণ" and
# "...লেনদেন পার্থক্যের প্রয়োগ".

VERB_ENDINGS = [
    "তালিকা তৈরি করে বর্ণনা করতে পারব", "ব্যাখ্যা করতে পারব", "বর্ণনা করতে পারব",
    "বিশ্লেষণ করতে পারব", "নির্ণয় করতে পারব", "নির্ধারণ করতে পারব",
    "শনাক্ত করতে পারব", "চিহ্নিত করতে পারব", "তৈরি করতে পারব",
    "প্রস্তুত করতে পারব", "লিপিবদ্ধ করতে পারব", "সংরক্ষণ করতে পারব",
    "প্রণয়ন করতে পারব", "প্রয়োগ করতে পারব", "উপলব্ধি করতে পারব",
    "অনুধাবন করতে পারব", "মূল্যায়ন করতে পারব", "বলতে পারব", "রাখতে পারব",
    "দেখাতে পারব", "বুঝতে পারব", "মেলাতে পারব", "করতে পারব",
    "পারব", "করব", "বলব", "আগ্রহী হব", "সচেতন হব",
]

# A trailing token that is meaningless as a standalone topic.
BARE_TAIL = {"ধারণা", "বৈশিষ্ট্য", "গুরুত্ব", "প্রকারভেদ", "প্রকার", "সুবিধা",
             "অসুবিধা", "প্রয়োজনীয়তা", "পার্থক্য", "প্রভাব", "নীতিমালা",
             "সমস্যা", "উপায়", "কারণ", "ধাপ", "গঠন", "ভূমিকা", "উদ্দেশ্য",
             "ব্যবহার", "শ্রেণিবিভাগ", "তাৎপর্য"}


def to_bengali_numeral(n):
    return "".join(BENGALI_DIGITS[int(d)] for d in str(n))


def apply_spelling(text, corrections):
    # token-boundary-aware (see _config.apply_corrections) so a fix cannot
    # rewrite the middle of an unrelated word.
    return _config.apply_corrections(text, corrections)


def atomize_topics(chapter, corrections, bare_extra, allowed_single_words=None):
    if allowed_single_words is None:
        allowed_single_words = set()
    raw = chapter.get("topics") or chapter.get("learning_outcomes", [])
    out = []
    for item in raw:
        item = apply_spelling(item.strip(), corrections)
        if not item:
            continue
        for verb in VERB_ENDINGS:
            if item.endswith(" " + verb) or item == verb:
                item = item[: len(item) - len(verb)].strip(" ।,;")
                break
        if not item:
            continue
        parts = [p.strip() for p in item.split("এবং")] if "এবং" in item else [item]
        for part in parts:
            toks = [t for t in re.split(r"\s+", part) if t]
            if len(toks) < 2:
                # Allow single-word topics that are in the allowed list
                if part in allowed_single_words:
                    if part not in out:
                        out.append(part)
                    continue
                # would be a bare fragment; keep the whole pre-split item instead
                part = item
                toks = [t for t in re.split(r"\s+", item) if t]
            if len(toks) < 2:
                # Check allowed list again after reassignment
                if part in allowed_single_words:
                    if part not in out:
                        out.append(part)
                continue
            if toks[-1] in (BARE_TAIL | bare_extra) and len(toks) < 2:
                continue
            if part not in out:
                out.append(part)
    return out


def assemble_book(topic_map_path, book_name, grade, subject):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # One canonical slug for the CSV subject column, every subject, every run:
    # lowercase a-z0-9 words joined by single hyphens. This MUST equal the
    # config/<subject>.json filename stem (05_validate.py --stage final FAILs if
    # they differ). Trusting the raw arg is how the CSV got 'finance_and_banking'
    # while the config was 'finance-and-banking'.
    subject = _config.slugify(subject)
    grade = grade.strip()
    if not re.match(r"^[0-9]+(-[0-9]+)?$", grade):
        print(f"WARNING: grade '{grade}' is not like '9-10'")
    cfg_path = os.path.join(SCRIPT_DIR, "..", "config", f"{subject}.json")
    prof_path = os.path.join(SCRIPT_DIR, "..", "subjects", f"{subject}.md")
    if not os.path.exists(cfg_path):
        print(f"REFUSED: config/{subject}.json does not exist. Copy "
              f"config/_TEMPLATE.json and fill it, then re-run. "
              f"(run `05_validate.py --stage setup` first)")
        sys.exit(2)
    if not os.path.exists(prof_path):
        print(f"REFUSED: subjects/{subject}.md does not exist. Copy "
              f"subjects/_TEMPLATE.md and fill it, then re-run.")
        sys.exit(2)

    cfg = _config.load(subject)
    corrections = cfg["spelling_corrections"]
    bare_extra = cfg["attribute_nouns_extra"]
    allowed_single_words = cfg.get("allowed_single_words", set())
    print(f"subject slug: {subject}   config: {cfg['source']}  "
          f"({len(corrections)} spelling fixes, {len(allowed_single_words)} allowed single words)")

    with open(topic_map_path, encoding="utf-8") as f:
        topic_map = json.load(f)

    rows = []
    for chapter in topic_map:
        chapter["chapter_title"] = apply_spelling(chapter["chapter_title"], corrections)
        ch_label = f"অধ্যায় {to_bengali_numeral(chapter['chapter_no'])}: {chapter['chapter_title']}"
        for topic in atomize_topics(chapter, corrections, bare_extra, allowed_single_words):
            rows.append([grade, subject, ch_label, topic])

    csv_path = os.path.join(OUTPUT_DIR, f"{book_name}.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["grade", "subject", "chapter", "topic"])
        writer.writerows(rows)

    print(f"CSV written: {csv_path} ({len(rows)} topics)")
    print(f"Next: python 08_merge.py \"{csv_path}\"")
    return csv_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python 06_assemble.py <book_name> <grade> <subject>")
        sys.exit(1)

    book_name, grade, subject = sys.argv[1], sys.argv[2], sys.argv[3]
    topic_map_path = os.path.join(OCR_DIR, book_name, "topic_map.json")
    if not os.path.exists(topic_map_path):
        print(f"Topic map not found: {topic_map_path}")
        sys.exit(1)

    assemble_book(topic_map_path, book_name, grade, subject)
