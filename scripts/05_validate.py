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
    "উদাহরণ", "বিষয়", "বিষয়াদি",
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
# Heading checklist (Step 4b, scripts/04_extract_headings.py)                 #
# ocr/<book>/headings/chNN.json = the page-anchored ground truth that a Step  #
# 7 map is checked against. Its absence, or a map that only covers its first  #
# pages, is how the "agent mapped পরিচ্ছেদ ৩.১-৩.২ and stopped" bug shipped.   #
# --------------------------------------------------------------------------- #
def load_headings(headings_dir: str, no: int):
    """Return (list[{'page':int,'heading':str}], path, status).
    status: 'ok' | 'missing' | 'stub' | 'bad'."""
    path = os.path.join(headings_dir, f"ch{no:02d}.json")
    if not os.path.exists(path):
        return [], path, "missing"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], path, "bad"
    raw = data.get("headings", data) if isinstance(data, dict) else data
    if isinstance(data, dict) and data.get("pending"):
        return [], path, "stub"
    out = []
    for h in raw or []:
        if isinstance(h, str):
            out.append({"page": 0, "heading": nfc(h)})
        elif isinstance(h, dict) and h.get("heading"):
            pm = re.search(r"(\d+)", str(h.get("page", "")))
            out.append({"page": int(pm.group(1)) if pm else 0,
                        "heading": nfc(h["heading"])})
    if not out:
        return [], path, "stub"
    return out, path, "ok"


def heading_match(topic: str, heading: str) -> bool:
    """Loose: is `topic` derived from `heading`? Tolerates shortening, head-noun
    prefixing, OCR wobble."""
    a, b = nfc(topic), nfc(heading)
    if not a or not b:
        return False
    if fuzzy(a, b) >= 0.72 or a in b or b in a:
        return True
    ta, tb = content_tokens(a), content_tokens(b)
    if not ta or not tb:
        return False
    inter = ta & tb
    return len(inter) >= 2 or (
        len(inter) >= 1 and len(inter) / min(len(ta), len(tb)) >= 0.6)


# --------------------------------------------------------------------------- #
# Canonical output format — one shape for every subject, every run.          #
# --------------------------------------------------------------------------- #
SUBJECT_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GRADE_RE = re.compile(r"^[0-9]+(?:-[0-9]+)?$")
BASE_HEADER = ["grade", "subject", "chapter", "topic"]
FULL_HEADER = BASE_HEADER + ["scope_note", "topic_raw"]
# Distinctive unfilled-template strings. Prose references like `config/<subject>.json`
# are legitimate and must NOT be listed here.
PROFILE_MARKERS = ("# Subject profile — <subject>", "`<e.g. ", "<the section title |",
                   "<subject-specific example, e.g.", "<none | unit")
CONFIG_MARKERS = ("<english lowercase, must equal", "<chapter name>",
                  "<topic to replace>", "<topic to fold in>",
                  "<merged label naming")


def subject_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").strip().lower()).strip("-")


def resolve_subject(book: str, explicit: str | None, topic_map=None) -> str:
    if explicit:
        return subject_slug(explicit)
    if topic_map is None:
        try:
            topic_map, _ = load_topic_map(book)
        except Exception:
            topic_map = []
    if topic_map and topic_map[0].get("subject"):
        return subject_slug(topic_map[0]["subject"])
    # last resort: book name -> subject slug (drop the "class9-10-" prefix that
    # slugify_book adds for chapter-map lookup)
    return re.sub(r"^class[0-9-]+-", "", slugify_book(os.path.basename(book)))


# --------------------------------------------------------------------------- #
# Stage: setup — is this subject ready for a run? (templates filled, slugs OK) #
# --------------------------------------------------------------------------- #
def stage_setup(book: str, chapter_map_path: str, subject: str | None = None):
    fails, warns = [], []
    subj = resolve_subject(book, subject)

    if not SUBJECT_SLUG_RE.match(subj):
        fails.append(f"subject '{subj}' is not a clean slug — use lowercase "
                     f"a-z0-9 words joined by single hyphens (e.g. 'geography', "
                     f"'finance-and-banking'), matching the config filename")

    prof = os.path.join(ROOT, "subjects", f"{subj}.md")
    if not os.path.exists(prof):
        fails.append(f"subjects/{subj}.md missing — copy subjects/_TEMPLATE.md and "
                     f"fill every section from 2-3 real chapters before Step 7")
    else:
        txt = open(prof, encoding="utf-8").read()
        hit = [m for m in PROFILE_MARKERS if m in txt]
        if hit:
            fails.append(f"subjects/{subj}.md still has unfilled template "
                         f"placeholders ({hit[0]!r}…) — fill it from the book")

    cfgp = os.path.join(CONFIG_DIR, f"{subj}.json")
    if not os.path.exists(cfgp):
        fails.append(f"config/{subj}.json missing — copy config/_TEMPLATE.json")
    else:
        cfgtxt = open(cfgp, encoding="utf-8").read()
        chit = [m for m in CONFIG_MARKERS if m in cfgtxt]
        if chit:
            fails.append(f"config/{subj}.json still has template placeholders "
                         f"({chit[0]!r}…) — fill or delete the placeholder entries")
        try:
            raw = json.loads(cfgtxt)
        except json.JSONDecodeError as e:
            return fails + [f"config/{subj}.json is not valid JSON: {e}"], warns
        if subject_slug(raw.get("subject", "")) != subj:
            fails.append(f"config/{subj}.json 'subject' field is "
                         f"'{raw.get('subject')}' — must equal '{subj}' (the "
                         f"filename stem and the CSV subject column)")
        for k in ("spelling_corrections", "merge_overrides", "scope_split",
                  "distinct_pairs", "attribute_nouns_extra", "lexicon_extra"):
            if k not in raw:
                fails.append(f"config/{subj}.json missing key '{k}' (see _TEMPLATE.json)")
        ss = raw.get("scope_split", {})
        if isinstance(ss, dict) and ss.get("enabled") and ss.get("max_core_words", 12) == 12:
            warns.append(f"config/{subj}.json scope_split.max_core_words is still "
                         f"12 (template default) — set it to 5 for the §3.6 goal, "
                         f"or leave 12 if this subject genuinely needs long labels")

    cmap = chapter_map_path
    want_slug = slugify_book(os.path.basename(book)).replace("class", "").lstrip("0123456789-")
    mismatch = cmap and want_slug and want_slug not in os.path.basename(cmap).lower()
    if not cmap or not os.path.exists(cmap) or mismatch:
        fails.append(f"chapter map for this book not found — create "
                     f"chapter-maps/{slugify_book(os.path.basename(book))}.csv "
                     f"(chapter_no,chapter_title,start_page,end_page; PDF page "
                     f"numbers). §Step 1."
                     + (f" (auto-guess picked the unrelated "
                        f"{os.path.basename(cmap)})" if mismatch else ""))
    else:
        try:
            rows = load_chapters(cmap)
            need = {"chapter_no", "chapter_title", "start_page", "end_page"}
            if rows and not need <= set(rows[0]):
                fails.append(f"{os.path.relpath(cmap, ROOT)} header must be "
                             f"exactly chapter_no,chapter_title,start_page,end_page")
        except Exception as e:
            fails.append(f"cannot read {cmap}: {e}")

    return fails, warns


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

    headings_dir = os.path.join(os.path.dirname(tm_path), "headings")
    skip_heading_gate = bool(os.environ.get("NCTB_SKIP_HEADING_GATE"))

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

        # -- learning_outcomes transcribed from the box, not paraphrased -- #
        # A real শিখনফল box uses varied action verbs (ব্যাখ্যা/বিশ্লেষণ/মূল্যায়ন
        # … করতে পারব). A map whose outcomes collapse to "X সম্পর্কে জানব" was
        # written from memory, not read off page 1 — the same failure that ships
        # invented outcomes (BGS ch3: 5/6 "সম্পর্কে জানব", 3 not in the box).
        janob = [x for x in los if re.search(r"জানব(ো)?\s*$", x)]
        if los and len(janob) >= max(3, round(0.5 * len(los))):
            warns.append(f"{P}: {len(janob)}/{len(los)} learning_outcomes end in "
                         f"'জানব' — looks paraphrased; copy the শিখনফল box verbatim "
                         f"(verbs kept) and re-check every topic against the body")

        # -- coverage / truncation vs the Step-4b heading checklist ------- #
        rng = ranges_by_no.get(no)
        span = (rng[1] - rng[0] + 1) if rng else 0
        hlist, hpath, hstatus = load_headings(headings_dir, no)
        hrel = os.path.relpath(hpath, ROOT)
        if hstatus != "ok":
            msg = {
                "missing": f"{P}: heading checklist {hrel} missing — run "
                           f"scripts/04_extract_headings.py (Step 4b) before Step 7; "
                           f"without it a mid-chapter truncation or an invented topic "
                           f"cannot be caught",
                "stub":    f"{P}: heading checklist {hrel} is an unfilled stub — run "
                           f"the Step 4b agent pass to list every page's headings",
                "bad":     f"{P}: heading checklist {hrel} is not valid JSON",
            }[hstatus]
            if skip_heading_gate:
                warns.append(msg + " (NCTB_SKIP_HEADING_GATE set — not enforced)")
            else:
                fails.append(msg + " — or set NCTB_SKIP_HEADING_GATE=1 for a legacy "
                             f"book mid-migration")
        elif topics:
            htexts = [h["heading"] for h in hlist]
            hit_h = [h for h in htexts if any(heading_match(t, h) for t in topics)]
            frac = len(hit_h) / len(htexts)
            # coverage is WARN-only: extracted headings are often more granular
            # than topics (numbered sub-items), so a low ratio is a hint, not proof.
            if frac < 0.6:
                warns.append(f"{P}: only {frac:.0%} of the {len(htexts)} extracted "
                             f"section headings map to a topic — confirm no whole "
                             f"section was skipped")
            # truncation is the FAIL: earlier headings DID map, but the final
            # quarter of the chapter has ≥2 headings and NONE of them mapped —
            # i.e. Step 7 stopped part-way (BGS ch3: mapped ৩.১-৩.২, dropped ৩.৩-৩.৪).
            if rng and span >= 8 and hit_h:
                tail_start = rng[0] + int(span * 0.75)
                tail = [h for h in hlist if h["page"] >= tail_start]
                tail_hit = [h for h in tail
                            if any(heading_match(t, h["heading"]) for t in topics)]
                if len(tail) >= 2 and not tail_hit:
                    covered_pg = [h["page"] for h in hlist if h["page"] and any(
                        heading_match(t, h["heading"]) for t in topics)]
                    stop = max(covered_pg) if covered_pg else rng[0]
                    fails.append(f"{P}: topics stop around page {stop} but the chapter "
                                 f"runs to {rng[1]} and pages {tail_start}-{rng[1]} "
                                 f"carry {len(tail)} unmapped headings — mid-chapter "
                                 f"truncation. Re-map Step 7 from every page.")
            # invented: a topic that matches no heading and no outcome
            for t in topics:
                if any(heading_match(t, h) for h in htexts):
                    continue
                if any(fuzzy(t, strip_pedagogy(x)) >= 0.6 or
                       content_tokens(t) & content_tokens(strip_pedagogy(x))
                       for x in los):
                    continue
                warns.append(f"{P}: topic '{t}' matches no extracted heading and no "
                             f"outcome — verify it is on a page, not invented")
        # density backstop (works even when the heading gate is skipped)
        if span >= 12 and len(topics) < 0.5 * span:
            warns.append(f"{P}: {len(topics)} topics for a {span}-page chapter "
                         f"(< 0.5/page) — likely truncated; check the tail পরিচ্ছেদ")

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

    rawbytes = open(csv_path, "rb").read()
    if not rawbytes.startswith(b"\xef\xbb\xbf"):
        fails.append(f"{book}.csv is not UTF-8 with BOM — 06_assemble.py writes "
                     f"utf-8-sig; something re-saved it")
    all_rows = list(csv.reader(open(csv_path, encoding="utf-8-sig")))
    header = all_rows[0] if all_rows else []
    rows = all_rows[1:]

    # -- canonical shape: same header for every subject, every run ----------- #
    if header not in (BASE_HEADER, FULL_HEADER):
        fails.append(f"CSV header is {header} — must be exactly {BASE_HEADER} "
                     f"(pre-Step-10) or {FULL_HEADER} (after Step 10)")
    # QUOTE_ALL: 06_assemble writes every field quoted
    first_data = next((ln for ln in rawbytes.decode("utf-8-sig").splitlines()[1:]
                       if ln.strip()), "")
    if first_data and not first_data.startswith('"'):
        fails.append(f"CSV is not QUOTE_ALL (row starts {first_data[:20]!r}) — "
                     f"re-run 06_assemble.py")

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
    subject = resolve_subject(book, None, topic_map)
    cfg = load_config(subject)
    overrides = cfg.get("merge_overrides", {})
    spelling = cfg.get("spelling_corrections", {})

    # -- uniform grade / subject columns ------------------------------------- #
    grade_vals = {r[0] for r in rows if len(r) >= 1}
    subj_vals = {r[1] for r in rows if len(r) >= 2}
    for g in grade_vals:
        if not GRADE_RE.match(g):
            fails.append(f"CSV grade column has '{g}' — must be like '9-10'")
    for s in subj_vals:
        if s != subject:
            fails.append(f"CSV subject column has '{s}' — must be '{subject}' on "
                         f"every row (lowercase-hyphen slug == config filename; "
                         f"fix the arg to 06_assemble.py and the topic_map.json "
                         f"'subject' field)")

    # -- Step 10 must have run when the subject opts in --------------------- #
    ss_enabled = bool(cfg.get("scope_split", {}).get("enabled"))
    if ss_enabled and raw_idx is None:
        fails.append(f"CSV has {len(header)} columns but config/{subject}.json "
                     f"scope_split.enabled=true — Step 10 (12_scope_split.py) "
                     f"never ran. Run it, or set scope_split.enabled=false.")
    if not ss_enabled and raw_idx is not None:
        warns.append(f"CSV is 6-column but config/{subject}.json "
                     f"scope_split.enabled is not true — set it true to keep the "
                     f"schema intentional")

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

    # scope-note / label-length + self-identifying check (§3.6). WARN only — a
    # style guard, never a gate. Active only when Step 10 ran (topic_raw present)
    # and the subject opted in via config/<subject>.json -> scope_split.
    ss = cfg.get("scope_split", {})
    if ss.get("enabled") and raw_idx is not None:
        max_core = int(ss.get("max_core_words", 12))
        bare = ATTRIBUTE_NOUNS | set(cfg.get("attribute_nouns_extra", set()))
        for r in rows:
            if len(r) <= 4:
                continue
            core = nfc(r[3])
            raw = nfc(r[raw_idx]) if len(r) > raw_idx else core
            if re.search(r"[（(][^（()）]*[）)]\s*$", core):
                warns.append(f"'{nfc(r[2])}': topic still ends in a (...) after "
                             f"Step 10 — '{core}'")
            core_toks = tokens(core)
            n = len(core_toks)
            if n > max_core:
                warns.append(f"'{nfc(r[2])}': topic label is {n} words (> {max_core}) "
                             f"— move detail to scope_note or rephrase — '{core}'")
            # self-identifying (§3.6): the label must still name the concept with
            # the chapter title AND subject hidden. Flags a label that has
            # collapsed to nothing but aspect nouns plus, at most, one word the
            # chapter title already supplies — i.e. the head concept was cut
            # while shortening. Token match is exact (inflected forms count as
            # their own word), so this under-flags rather than nags.
            ch_concept = content_tokens(
                re.sub(r"^\s*অধ্যায়[^:：]*[:：]?\s*", "", nfc(r[2])))
            non_aspect = content_tokens(core) - bare
            own = non_aspect - ch_concept
            if core_toks and not own and len(non_aspect) <= 1:
                warns.append(
                    f"'{nfc(r[2])}': label '{core}' is not self-identifying — it is "
                    f"aspect words / chapter-title words only; the head concept was "
                    f"lost in shortening (§3.6). raw: '{raw}'")

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
    ap.add_argument("--stage", required=True,
                    choices=["setup", "extract", "topicmap", "final", "all"])
    ap.add_argument("book", help="book folder name under ocr/ (and output/<book>.csv stem)")
    ap.add_argument("--map", help="chapter-map csv (auto-guessed from the book name if omitted)")
    ap.add_argument("--subject", help="subject slug (setup stage; else read from topic_map.json)")
    args = ap.parse_args()

    cmap = find_chapter_map(args.book, args.map)
    if not os.path.exists(cmap) and args.stage not in ("setup", "all"):
        print(f"chapter map not found for '{args.book}' (tried {cmap})")
        sys.exit(2)
    if os.path.exists(cmap):
        print(f"chapter map: {os.path.relpath(cmap, ROOT)}")

    def run(stage):
        if stage == "setup":
            return stage_setup(args.book, cmap, args.subject)
        return {"extract": stage_extract, "topicmap": stage_topicmap,
                "final": stage_final}[stage](args.book, cmap)

    stages = ["setup", "extract", "topicmap", "final"] if args.stage == "all" else [args.stage]
    rc = 0
    for st in stages:
        f, w = run(st)
        rc |= report(st, args.book, f, w)
        if f and args.stage == "all":
            print(f"\n[all] stopped at '{st}' — fix the FAILs above and re-run.")
            break
    sys.exit(rc)


if __name__ == "__main__":
    main()
