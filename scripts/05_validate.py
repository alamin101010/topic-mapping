"""Step 3b / 7b / 9b: staged validation gate for the topic-mapping pipeline.

Runs one of three stages and exits nonzero on any FAIL so a batch run halts on
the first bad book instead of emitting broken CSVs.

    python 05_validate.py --stage extract  "<book-name>"
    python 05_validate.py --stage topicmap "<book-name>"
    python 05_validate.py --stage final    "<book-name>"

<book-name> is the folder name under ocr/ and the stem of output/<book-name>.csv.
The chapter map is chapter-maps/<slug>.csv, resolved by --map or auto-guessed.

Backward compatible: `python 05_validate.py <topic_map.json> <chapter_map.csv>`
still runs the topicmap-stage checks on those two paths.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER_MAPS_DIR = os.path.join(ROOT, "chapter-maps")
OCR_DIR = os.path.join(ROOT, "ocr")
OUTPUT_DIR = os.path.join(ROOT, "output")
CONFIG_DIR = os.path.join(ROOT, "config")

BENGALI_DIGITS = "০১২৩৪৫৬৭৮৯"
ASCII_TO_BN = {str(i): BENGALI_DIGITS[i] for i in range(10)}

# Bare attribute nouns: valid only WITH a head concept in front of them.
ATTRIBUTE_NOUNS = {
    "ধারণা", "বৈশিষ্ট্য", "গুরুত্ব", "প্রকারভেদ", "প্রকার", "সুবিধা", "অসুবিধা",
    "প্রয়োজনীয়তা", "পার্থক্য", "প্রভাব", "নীতিমালা", "সমস্যা", "উপায়", "কারণ",
    "ধাপ", "গঠন", "কাজ", "ভূমিকা", "উদ্দেশ্য", "ব্যবহার", "উৎপত্তি", "ক্রমবিকাশ",
    "শ্রেণিবিভাগ", "শ্রেণীবিভাগ", "বিভাগ", "তাৎপর্য", "লক্ষণ", "প্রতিকার",
    "প্রতিরোধ", "উপকারিতা", "অপকারিতা", "ফলাফল", "বিবরণ", "পদ্ধতি", "চুক্তিপত্র",
    "প্রক্রিয়া", "কৌশল", "সম্পর্ক", "রকমভেদ", "উপাদান", "দিক", "ক্ষেত্র",
}

# Trailing pedagogy verb phrases stripped when testing "is this topic just a
# verb-stripped learning outcome?".  Longest first.
PEDAGOGY_TAILS = [
    "তালিকা তৈরি করে বর্ণনা করতে পারব", "উপলব্ধি করে হিসাবভুক্ত করতে পারব",
    "নির্ণয় ও বিশ্লেষণ করতে পারব", "প্রস্তুত করতে পারব", "বর্ণনা করতে পারব",
    "ব্যাখ্যা করতে পারব", "বিশ্লেষণ করতে পারব", "নির্ণয় করতে পারব",
    "নির্ধারণ করতে পারব", "শনাক্ত করতে পারব", "চিহ্নিত করতে পারব",
    "তৈরি করতে পারব", "লিপিবদ্ধ করতে পারব", "সংরক্ষণ করতে পারব",
    "প্রণয়ন করতে পারব", "প্রয়োগ করতে পারব", "উপলব্ধি করতে পারব",
    "অনুধাবন করতে পারব", "মূল্যায়ন করতে পারব", "রাখতে পারব", "দেখাতে পারব",
    "বুঝতে পারব", "মেলাতে পারব", "টানতে পারব", "করতে পারব", "করতে পারবে",
    "পারব", "পারবে", "করব", "বলব", "আগ্রহী হব", "সচেতন হব", "অভ্যস্ত হব",
    "বর্ণনা", "ব্যাখ্যা", "বিশ্লেষণ", "প্রস্তুতকরণ", "নির্ধারণ", "নির্ণয়",
    "শনাক্তকরণ", "চিহ্নিতকরণ", "লিপিবদ্ধকরণ",
]

STOPWORDS = {
    "ও", "এবং", "এর", "এ", "একটি", "যে", "তা", "থেকে", "জন্য", "মধ্যে", "সাথে",
    "করে", "কীভাবে", "কত", "কোন", "কোনো", "বিভিন্ন", "নিয়ে", "উপর", "অর্থাৎ",
    "বা", "এই", "যা", "হয়", "করা", "নিরূপণ", "প্রভৃতি", "সমূহ", "সমুহ",
}

# Distinct-concept markers: two topics that share almost all their text but
# differ on one of these are OPPOSITES, not near-duplicates. Never treat one as
# "present" because the other is, and never auto-merge them.
DISTINCT_MARKERS = [
    ("ক্রয়", "বিক্রয়"), ("প্রাপ্তি", "প্রদান"), ("সুবিধা", "অসুবিধা"),
    ("আয়", "ব্যয়"), ("স্থায়ী", "চলতি"), ("ডেবিট", "ক্রেডিট"),
    ("দীর্ঘমেয়াদি", "স্বল্পমেয়াদি"), ("দীর্ঘমেয়াদী", "চলতি"),
    ("আমদানি", "রপ্তানি"), ("মূলধন", "মুনাফা"), ("একতরফা", "দুতরফা"),
    ("উত্তল", "অবতল"), ("অম্ল", "ক্ষার"), ("ধাতু", "অধাতু"),
    ("লাভ", "ক্ষতি"), ("প্রয়োগ", "পার্থক্য"), ("নগদ", "ধারে"),
    ("সম্পদ", "দায়"), ("জমা", "উত্তোলন"),
]


def opposites(a: str, b: str) -> bool:
    """True if a and b are near-identical strings that flip on a paired marker
    (ক্রয়/বিক্রয়, প্রাপ্তি/প্রদান, ...) — i.e. distinct concepts, not dupes."""
    a, b = nfc(a), nfc(b)
    if fuzzy(a, b) >= 0.985:
        return False
    for x, y in DISTINCT_MARKERS:
        if (y in a) == (y in b) and (x in a) == (x in b):
            continue
        na, nb = a.replace(y, x), b.replace(y, x)
        if fuzzy(na, nb) >= 0.95:
            return True
    return False


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").strip())


def tokens(s: str):
    return [t for t in re.split(r"\s+", nfc(s)) if t]


def content_tokens(s: str):
    return {t.strip("।,;:()[]'\"-") for t in tokens(s)} - STOPWORDS


def fuzzy(a: str, b: str) -> float:
    return SequenceMatcher(None, nfc(a), nfc(b)).ratio()


def strip_pedagogy(s: str) -> str:
    s = nfc(s).rstrip(" ।;,")
    changed = True
    while changed:
        changed = False
        for tail in PEDAGOGY_TAILS:
            if s.endswith(" " + tail) or s == tail:
                s = s[: len(s) - len(tail)].rstrip(" ।;,")
                changed = True
                break
    return s


def slugify_book(book: str) -> str:
    m = re.search(r"Class\s*([0-9\-]+)_([A-Za-z &]+)", book)
    if m:
        grade = m.group(1).strip()
        subj = m.group(2).strip().lower().replace(" ", "-").replace("&", "and")
        return f"class{grade}-{subj}"
    return book.lower().replace(" ", "-")


def find_chapter_map(book: str, explicit: str | None) -> str:
    if explicit:
        p = explicit if os.path.isabs(explicit) else os.path.join(CHAPTER_MAPS_DIR, explicit)
        if os.path.exists(p):
            return p
    guess = os.path.join(CHAPTER_MAPS_DIR, slugify_book(book) + ".csv")
    if os.path.exists(guess):
        return guess
    # last resort: single fuzzy hit
    cands = glob.glob(os.path.join(CHAPTER_MAPS_DIR, "*.csv"))
    key = slugify_book(book)
    cands.sort(key=lambda c: fuzzy(os.path.basename(c), key), reverse=True)
    return cands[0] if cands else guess


def load_chapters(chapter_map_path: str):
    with open(chapter_map_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_topic_map(book_or_path: str):
    if book_or_path.endswith(".json"):
        path = book_or_path
    else:
        path = os.path.join(OCR_DIR, book_or_path, "topic_map.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f), path


def load_config(subject: str) -> dict:
    """Per-subject config via the shared loader (handles _comment keys and the
    legacy global-file fallback)."""
    import _config
    return _config.load(subject)


# --------------------------------------------------------------------------- #
# Lexical check — catch OCR reading errors (পাকশল্লি, সংগ্রহলন, কোলেষ্টেরল …)  #
# that structure checks can't see. Best-effort: needs hunspell + a Bengali    #
# dictionary; degrades to a single WARN when unavailable.                     #
# --------------------------------------------------------------------------- #
BENGALI_WORD_RE = re.compile(r"[ঀ-৿]{2,}")


def bengali_words(s: str):
    return {w for w in BENGALI_WORD_RE.findall(nfc(s)) if w not in STOPWORDS}


DICT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dict")


def spellcheck_bengali(words):
    """Return the subset of `words` a Bengali dictionary flags as unknown, or
    None if no checker is available.

    Dictionary sources, in order:
      1. a system dict via pyenchant (`bn_BD` / `bn_IN` / `bn`).
      2. scripts/dict/bn_BD.{dic,aff} via the hunspell CLI — commit these to make
         the check work everywhere with no system install (LibreOffice / Firefox
         bn_BD hunspell dict). See scripts/dict/README.md.
      3. a system hunspell dict via the hunspell CLI.
    Set NCTB_NO_SPELLCHECK=1 to force-skip.
    """
    if os.environ.get("NCTB_NO_SPELLCHECK"):
        return set()
    if not words:
        return set()
    tags = ("bn_BD", "bn_IN", "bn")
    local = os.path.join(DICT_DIR, "bn_BD")
    have_local = os.path.exists(local + ".dic") and os.path.exists(local + ".aff")

    # -- pyenchant (system dicts) --------------------------------------------- #
    try:
        import enchant  # type: ignore
        for tag in tags:
            if enchant.dict_exists(tag):
                d = enchant.Dict(tag)
                return {w for w in words if not d.check(w)}
    except Exception:
        pass

    # -- hunspell CLI ---------------------------------------------------------- #
    import shutil
    import subprocess
    if not shutil.which("hunspell"):
        return None
    payload = "\n".join(sorted(words)) + "\n"
    for tag in ([local] if have_local else []) + list(tags):
        try:
            r = subprocess.run(["hunspell", "-d", tag, "-l"], input=payload,
                               capture_output=True, text=True, timeout=60)
        except Exception:
            return None
        err = (r.stderr or "").lower()
        if "can't open" in err or "cannot open" in err or "no such" in err:
            continue
        return {w for w in r.stdout.splitlines() if w.strip()}
    return None


# --------------------------------------------------------------------------- #
# Stage: extract  — did we actually get the whole chapter, not just the box?  #
# --------------------------------------------------------------------------- #
def stage_extract(book: str, chapter_map_path: str):
    fails, warns = [], []
    chapters = load_chapters(chapter_map_path)
    base = os.path.join(OCR_DIR, book, "chapters")
    if not os.path.isdir(base):
        return [f"no extracted pages: {base} missing"], []
    for ch in chapters:
        no = int(ch["chapter_no"])
        rng = int(ch["end_page"]) - int(ch["start_page"]) + 1
        got = 0
        for pat in (f"ch{no:02d}", f"ch{no}", f"chap{no:02d}", f"chapter{no:02d}"):
            d = os.path.join(base, pat)
            if os.path.isdir(d):
                got = len(glob.glob(os.path.join(d, "*.png")) +
                          glob.glob(os.path.join(d, "*.jpg")))
                break
        else:
            fails.append(f"ch{no}: no page folder under {base}")
            continue
        if rng >= 5 and got <= 3:
            fails.append(
                f"ch{no}: BOX-ONLY — {got} pages extracted of a {rng}-page chapter "
                f"({ch['start_page']}-{ch['end_page']}). Re-run 01_extract_images.py "
                f"without --max-pages.")
        elif got < rng * 0.8:
            warns.append(f"ch{no}: only {got}/{rng} pages extracted")
    return fails, warns


# --------------------------------------------------------------------------- #
# Stage: topicmap — is topic_map.json a real body map or a box paraphrase?    #
# --------------------------------------------------------------------------- #
def stage_topicmap(book_or_path: str, chapter_map_path: str):
    fails, warns = [], []
    topic_map, tm_path = load_topic_map(book_or_path)
    chapters = load_chapters(chapter_map_path)

    map_nos = {int(c["chapter_no"]) for c in chapters}
    tm_nos = {int(c.get("chapter_no", i + 1)) for i, c in enumerate(topic_map)}
    for missing in sorted(map_nos - tm_nos):
        fails.append(f"chapter {missing} present in chapter-map, absent from topic_map.json")

    titles_by_no = {int(c["chapter_no"]): nfc(c["chapter_title"]) for c in chapters}
    ranges_by_no = {}
    for c in chapters:
        try:
            ranges_by_no[int(c["chapter_no"])] = (
                int(c["start_page"]), int(c["end_page"]))
        except (KeyError, ValueError, TypeError):
            pass

    subject = (topic_map[0].get("subject") if topic_map else "") or slugify_book(
        os.path.basename(book_or_path))
    cfg = load_config(subject)
    bare = ATTRIBUTE_NOUNS | set(cfg.get("attribute_nouns_extra", set()))

    for i, ch in enumerate(topic_map):
        no = int(ch.get("chapter_no", i + 1))
        P = f"ch{no}"
        topics = [nfc(t) for t in ch.get("topics", [])]
        los = [nfc(x) for x in ch.get("learning_outcomes", [])]
        kw = ch.get("keywords", [])

        if not topics:
            fails.append(f"{P}: empty topics")
        if not los:
            warns.append(f"{P}: empty learning_outcomes (cross-check impossible)")
        if not (5 <= len(kw) <= 15):
            warns.append(f"{P}: {len(kw)} keywords (want 5-15)")
        if ch.get("needs_review"):
            fails.append(f"{P}: needs_review=true — provisional/box-only, redo Step 7")

        exp = titles_by_no.get(no, "")
        if exp and fuzzy(exp, ch.get("chapter_title", "")) < 0.6:
            warns.append(f"{P}: title '{ch.get('chapter_title')}' != map '{exp}'")

        # -- box-only tell: source_pages far narrower than the chapter ------ #
        sp = str(ch.get("source_pages", "")).strip()
        m = re.match(r"\s*(\d+)\s*[-–—]\s*(\d+)\s*$", sp)
        if m and no in ranges_by_no:
            got = int(m.group(2)) - int(m.group(1)) + 1
            want = ranges_by_no[no][1] - ranges_by_no[no][0] + 1
            if want >= 5 and got <= 3:
                fails.append(
                    f"{P}: source_pages '{sp}' = {got} pages of a {want}-page "
                    f"chapter — topic_map.json was built from the শিখনফল box, "
                    f"not the body. Delete it and redo Step 7 from the pages.")

        # -- bare / one-word / orphan topics -------------------------------- #
        for t in topics:
            tk = tokens(t)
            if len(tk) == 1:
                fails.append(f"{P}: one-word topic '{t}' — attach its head concept")
            elif tk and tk[0] in ("ও", "এবং") or t.startswith(("ও ", "এবং ", ",", "，")):
                fails.append(f"{P}: orphaned fragment '{t}' — head noun lost in a split")
            elif len(tk) <= 2 and tk[-1] in bare and (
                    len(tk) == 1 or tk[0] in STOPWORDS or tk[0] in bare):
                fails.append(f"{P}: bare attribute topic '{t}' — no head concept")
            elif tk[-1] in bare and len(tk) <= 2:
                warns.append(f"{P}: thin topic '{t}' — confirm it carries a head concept")

        # -- topics == verb-stripped learning outcomes? ------------------- #
        if los and topics:
            lo_norm = [strip_pedagogy(x) for x in los]
            hits = 0
            for t in topics:
                if any(fuzzy(t, ln) >= 0.85 or t in ln or ln in t
                       for ln in lo_norm if ln):
                    hits += 1
            ratio = hits / len(topics)
            if ratio >= 0.75:
                fails.append(
                    f"{P}: {hits}/{len(topics)} topics are verb-stripped copies of "
                    f"learning_outcomes ({ratio:.0%}) — this is a box paraphrase, "
                    f"not a body map. Read the chapter pages.")
            elif ratio >= 0.55:
                warns.append(f"{P}: {ratio:.0%} of topics track the outcome box closely")

        # -- every outcome covered by some topic -------------------------- #
        for lo in los:
            need = content_tokens(strip_pedagogy(lo))
            if not need:
                continue
            if not any(content_tokens(t) & need for t in topics):
                warns.append(f"{P}: outcome not covered by any topic — '{lo[:60]}...'")

        # -- topics is not a verb-stripped copy, structurally ------------- #
        if los and topics == [strip_pedagogy(x) for x in los]:
            fails.append(f"{P}: topics is a 1:1 verb-stripped copy of learning_outcomes")

    # -- lexical check: OCR reading errors in the shipped topic labels --- #
    # Structure checks pass a garble like 'পাকশল্লি' straight through; a
    # dictionary is the only thing that catches it. WARN, not FAIL: Bengali
    # dictionaries miss many valid technical terms, so a human must confirm
    # each hit against the page image (Step 7.2). Grow the false-positive
    # list via config/<subject>.json -> lexicon_extra.words.
    allow = set(cfg.get("lexicon_extra", set()))
    for _w, _c in cfg.get("spelling_corrections", {}).items():
        allow |= bengali_words(_c)
    locs = {}
    for i, ch in enumerate(topic_map):
        no = int(ch.get("chapter_no", i + 1))
        for t in ch.get("topics", []):
            for w in bengali_words(t):
                locs.setdefault(w, []).append((no, nfc(t)))
        for w in bengali_words(ch.get("chapter_title", "")):
            locs.setdefault(w, []).append((no, "chapter title"))
    flagged = spellcheck_bengali(set(locs) - allow)
    if flagged is None:
        warns.append("lexical check SKIPPED — no Bengali dictionary found. "
                     "Add scripts/dict/bn_BD.{dic,aff}, or `pip install "
                     "pyenchant` with a system bn_BD dict, or set "
                     "NCTB_NO_SPELLCHECK=1 to silence. Until then OCR reading "
                     "errors are NOT caught — eyeball every topic vs the page.")
    else:
        for w in sorted(flagged):
            no, where = locs[w][0]
            more = f" (+{len(locs[w]) - 1} more)" if len(locs[w]) > 1 else ""
            warns.append(f"ch{no}: '{w}' ({where}){more} is not in the Bengali "
                         f"dictionary — check the page: OCR misread -> fix "
                         f"topic_map.json; real term -> config lexicon_extra")

    return fails, warns


# --------------------------------------------------------------------------- #
# Stage: final — did assemble/merge silently drop topics? digits Bengali?     #
# --------------------------------------------------------------------------- #
def bn_chapter_label(no: int) -> str:
    return "অধ্যায় " + "".join(ASCII_TO_BN[d] for d in str(no))


def stage_final(book: str, chapter_map_path: str):
    fails, warns = [], []
    topic_map, _ = load_topic_map(book)
    csv_path = os.path.join(OUTPUT_DIR, book + ".csv")
    if not os.path.exists(csv_path):
        return [f"missing {csv_path}"], []

    all_rows = list(csv.reader(open(csv_path, encoding="utf-8-sig")))
    header = all_rows[0] if all_rows else []
    rows = all_rows[1:]
    # Step 10 (12_scope_split.py) may add scope_note + topic_raw. The silent-drop
    # check must run against the pre-split label, so prefer topic_raw when present.
    raw_idx = header.index("topic_raw") if "topic_raw" in header else None
    csv_by_ch = {}
    for r in rows:
        if len(r) < 4:
            fails.append(f"malformed CSV row: {r!r}")
            continue
        if raw_idx is not None and len(r) > raw_idx and r[raw_idx].strip():
            csv_by_ch.setdefault(nfc(r[2]), []).append(nfc(r[raw_idx]))
        else:
            csv_by_ch.setdefault(nfc(r[2]), []).append(nfc(r[3]))

    # subject config (per-subject preferred, legacy global as fallback)
    subject = (topic_map[0].get("subject") if topic_map else "") or slugify_book(book)
    cfg = load_config(subject)
    overrides = cfg.get("merge_overrides", {})
    spelling = cfg.get("spelling_corrections", {})

    import _config
    def corrected(s: str) -> str:
        return nfc(_config.apply_corrections(s, spelling))

    # ASCII digits in chapter label
    for ch_label in csv_by_ch:
        if re.search(r"[0-9]", ch_label):
            fails.append(f"CSV chapter label has ASCII digits: '{ch_label}' "
                         f"— Step 8 Bengali-numeral conversion did not run")

    # duplicate rows within a chapter
    for ch_label, ts in csv_by_ch.items():
        dupes = {t for t in ts if ts.count(t) > 1}
        for d in dupes:
            warns.append(f"'{ch_label}': duplicate topic row '{d}'")

    # scope-note / label-length (§3.6). WARN only — this is a style guard, never
    # a gate. Active only when Step 10 ran (topic_raw present) and the subject
    # opted in via config/<subject>.json -> scope_split.
    ss = cfg.get("scope_split", {})
    if ss.get("enabled") and raw_idx is not None:
        max_core = int(ss.get("max_core_words", 12))
        for r in rows:
            if len(r) <= 4:
                continue
            core = nfc(r[3])
            if re.search(r"[（(][^（()）]*[）)]\s*$", core):
                warns.append(f"'{nfc(r[2])}': topic still ends in a (...) after "
                             f"Step 10 — '{core}'")
            n = len([t for t in re.split(r"\s+", core) if t])
            if n > max_core:
                warns.append(f"'{nfc(r[2])}': topic label is {n} words (> {max_core}) "
                             f"— move detail to scope_note or rephrase — '{core}'")

    # silent-drop check: every topic_map topic must reach the CSV OR be named
    # in an explicit merge_overrides rule for that chapter.
    csv_labels = list(csv_by_ch)
    for i, ch in enumerate(topic_map):
        no = int(ch.get("chapter_no", i + 1))
        label = next((c for c in csv_labels if c.startswith(bn_chapter_label(no) + ":")
                      or c.startswith(bn_chapter_label(no) + " ")), None)
        if label is None:
            fails.append(f"ch{no}: no rows in CSV for '{bn_chapter_label(no)}'")
            continue
        present = csv_by_ch[label]
        ov = overrides.get(label, {})
        named = {corrected(k) for k in ov}
        for t in (corrected(x) for x in ch.get("topics", [])):
            match = [p for p in present
                     if (fuzzy(t, p) >= 0.9 or t in p or p in t
                         or set(tokens(t)) <= set(tokens(p)))
                     and not opposites(t, p)]
            if match:
                continue
            if t in named:
                continue  # deliberately merged/dropped via config
            fails.append(
                f"ch{no}: topic '{t}' from topic_map.json is NOT in the CSV and has "
                f"no merge_overrides rule — silently dropped by 07_atomize/08_merge. "
                f"Add a rule to config/{subject}.json or fix the merge.")
    return fails, warns


# --------------------------------------------------------------------------- #
def report(stage: str, book: str, fails, warns) -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log = os.path.join(OUTPUT_DIR, "validation-log.txt")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"\n=== [{stage}] {book} ===\n")
        for w in warns:
            f.write(f"  WARN  {w}\n")
        for e in fails:
            f.write(f"  FAIL  {e}\n")
    for w in warns:
        print(f"  WARN  {w}")
    for e in fails:
        print(f"  FAIL  {e}")
    print(f"\n[{stage}] {book}: {len(fails)} FAIL, {len(warns)} WARN  "
          f"(log: {os.path.relpath(log, ROOT)})")
    return 1 if fails else 0


def main():
    # legacy 2-positional form
    if len(sys.argv) == 3 and sys.argv[1].endswith(".json"):
        f, w = stage_topicmap(sys.argv[1], sys.argv[2])
        sys.exit(report("topicmap", os.path.basename(sys.argv[1]), f, w))

    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["extract", "topicmap", "final"])
    ap.add_argument("book", help="book folder name under ocr/ (and output/<book>.csv stem)")
    ap.add_argument("--map", help="chapter-map csv (auto-guessed from the book name if omitted)")
    args = ap.parse_args()

    cmap = find_chapter_map(args.book, args.map)
    if not os.path.exists(cmap):
        print(f"chapter map not found for '{args.book}' (tried {cmap})")
        sys.exit(2)
    print(f"chapter map: {os.path.relpath(cmap, ROOT)}")

    fn = {"extract": stage_extract, "topicmap": stage_topicmap, "final": stage_final}[args.stage]
    f, w = fn(args.book, cmap)
    sys.exit(report(args.stage, args.book, f, w))


if __name__ == "__main__":
    main()
