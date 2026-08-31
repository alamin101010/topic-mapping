"""Shared per-subject config loader.

One file per subject: config/<subject>.json (see config/_TEMPLATE.json). Holds
spelling_corrections, merge_overrides, distinct_pairs, attribute_nouns_extra.

Falls back to the legacy global files (scripts/spelling_corrections.json,
scripts/merge_overrides.json) so older books keep working until migrated.
"""
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(ROOT, "config")
LEGACY_SPELLING = os.path.join(SCRIPT_DIR, "spelling_corrections.json")
LEGACY_OVERRIDES = os.path.join(SCRIPT_DIR, "merge_overrides.json")


def _read(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _strip_comments(d):
    if isinstance(d, dict):
        return {k: _strip_comments(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, list):
        return [_strip_comments(x) for x in d]
    return d


def slugify(subject: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", subject.strip().lower()).strip("-")


_BN_LETTER = "ঀ-৿"


def apply_corrections(text: str, corrections: dict) -> str:
    """Apply {wrong: right} spelling fixes to `text`.

    Unlike a blind ``str.replace``, each pattern must start on a token boundary
    (not immediately preceded by another Bengali letter) so a fix can never
    rewrite the middle of an unrelated word — e.g. a rule ``তন্ত্র -> তন্তু``
    will not corrupt ``গণতন্ত্রের``. The trailing edge is left free so inflected
    endings (``...ের``, ``...কে``) are still caught.
    """
    for wrong, correct in (corrections or {}).items():
        if not wrong:
            continue
        text = re.sub(r"(?<![" + _BN_LETTER + r"])" + re.escape(wrong), correct, text)
    return text


def load(subject: str) -> dict:
    """Return {spelling_corrections, merge_overrides, distinct_pairs,
    attribute_nouns_extra} for a subject.

    If config/<subject>.json exists it is the SOLE source (no cross-subject
    contamination from the legacy globals). The legacy global files are used only
    when a subject has no config file yet.
    """
    cfg, found = {}, False
    for name in (f"{subject}.json", f"{slugify(subject)}.json"):
        p = os.path.join(CONFIG_DIR, name)
        if os.path.exists(p):
            cfg = _strip_comments(_read(p))
            found = True
            break

    if found:
        spelling = dict(cfg.get("spelling_corrections", {}))
        overrides = dict(cfg.get("merge_overrides", {}))
    else:
        name = "(legacy global files)"
        spelling = dict(_read(LEGACY_SPELLING))
        overrides = dict(_read(LEGACY_OVERRIDES))

    dp = cfg.get("distinct_pairs", {})
    pairs = dp.get("pairs", dp) if isinstance(dp, dict) else dp

    an = cfg.get("attribute_nouns_extra", {})
    words = an.get("words", an) if isinstance(an, dict) else an

    scope_split = cfg.get("scope_split", {})
    if not isinstance(scope_split, dict):
        scope_split = {}

    lex = cfg.get("lexicon_extra", {})
    lex_words = lex.get("words", lex) if isinstance(lex, dict) else lex

    return {
        "source": name,
        "spelling_corrections": spelling,
        "merge_overrides": overrides,
        "distinct_pairs": [tuple(p) for p in pairs],
        "attribute_nouns_extra": set(words),
        "scope_split": scope_split,
        "lexicon_extra": set(lex_words or []),
    }
