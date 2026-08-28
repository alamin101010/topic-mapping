import json, sys
path = sys.argv[1]
d = json.load(open(path, 'r', encoding='utf-8'))
if isinstance(d, list):
    print(f"Top-level: list ({len(d)} chapters)")
    for c in d:
        ch = c.get('chapter_no', '?')
        topics = c.get('topics', [])
        kw = c.get('keywords', [])
        print(f"  ch{ch}: {len(topics)} topics, {len(kw)} keywords")
elif isinstance(d, dict):
    print(f"Top-level: dict, keys={list(d.keys())}")
    chapters = d.get('chapters', [])
    print(f"Chapters: {len(chapters)}")
    for c in chapters:
        ch = c.get('chapter_no', '?')
        topics = c.get('topics', [])
        kw = c.get('keywords', [])
        print(f"  ch{ch}: {len(topics)} topics, {len(kw)} keywords")
