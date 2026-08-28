# Bengali dictionary for the lexical check

`05_validate.py --stage topicmap` spell-checks every topic word and WARNs on
anything a Bengali dictionary does not know (catches OCR reading errors like
`পাকশল্লি` for `পাকস্থলী`). It looks here first.

## Enable it

Drop a hunspell Bengali dictionary pair into this folder:

```
scripts/dict/bn_BD.dic
scripts/dict/bn_BD.aff
```

Sources (pick one, MPL/LGPL/GPL — fine to vendor):

- LibreOffice: https://github.com/LibreOffice/dictionaries/tree/master/bn_BD
- Firefox add-on "Bengali (Bangladesh) Spell Checker" — unzip the `.xpi`,
  take `dictionaries/bn-BD.dic` + `.aff`, rename to `bn_BD.*`

Then either have the `hunspell` CLI on PATH, **or** `pip install pyenchant`
(the script also accepts a system-installed `bn_BD`/`bn_IN`/`bn` dict via
pyenchant, in which case this folder is not needed).

## Reduce false positives

A general dictionary will not know valid subject terms (`কোলেস্টেরল`,
`পাকস্থলী`, transliterations). Add those — **after checking the spelling against
the page image** — to `config/<subject>.json` → `lexicon_extra.words`, not here.

## Turn it off

`NCTB_NO_SPELLCHECK=1` skips the check and the "no dictionary" WARN.
