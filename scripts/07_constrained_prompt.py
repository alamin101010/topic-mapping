"""Step 7b: Generate constrained topic_map prompt using extracted headings.

Reads the extracted headings from headings/chNN.json and generates a constrained
prompt that forces the Step 7 agent to only use verified section headings.

Usage:
    python 07_constrained_prompt.py <book_name> <chapter_no>

Output:
    prompts/constrained_chNN.txt — ready-to-use prompt for Step 7 agent
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
OCR_DIR = os.path.join(ROOT_DIR, "ocr")
PROMPTS_DIR = os.path.join(ROOT_DIR, "prompts")

# Read the base prompt
BASE_PROMPT_PATH = os.path.join(PROMPTS_DIR, "topic_map_prompt.md")


def load_headings(book_name, chapter_no):
    """Load extracted headings for a chapter."""
    headings_file = os.path.join(
        OCR_DIR, book_name, "headings", f"ch{chapter_no:02d}.json"
    )
    if not os.path.exists(headings_file):
        print(f"Headings file not found: {headings_file}")
        print("Run heading extraction first.")
        sys.exit(1)
    
    with open(headings_file, encoding="utf-8") as f:
        return json.load(f)


def generate_constrained_prompt(headings_data, subject_profile=""):
    """Generate a constrained prompt with heading checklist."""
    
    # Build the heading checklist
    headings = headings_data["headings"]
    chapter_title = headings_data["chapter_title"]
    chapter_no = headings_data["chapter"]
    
    # Deduplicate headings (some may appear on multiple pages)
    unique_headings = []
    seen = set()
    for h in headings:
        heading_text = h["heading"].strip()
        if heading_text not in seen:
            seen.add(heading_text)
            unique_headings.append(heading_text)
    
    # Build the checklist string
    checklist_items = "\n".join(
        f"  {i+1}. {h}" for i, h in enumerate(unique_headings)
    )
    
    constrained_prompt = f"""# Topic-map extraction prompt (CONSTRAINED — Step 7)

You are mapping the syllabus of chapter {chapter_no} ("{chapter_title}") of a Bangladeshi NCTB
school textbook, from scanned page images (Bengali, some English). OCR-style errors
are expected — infer through minor garbling, never invent content.

{subject_profile}

---

## CRITICAL CONSTRAINT: HEADING CHECKLIST

The following section headings have been EXTRACTED FROM THE SCANNED PAGES using
OCR verification. These are the ONLY valid section headings in this chapter.

**YOU MUST ONLY USE TOPICS FROM THIS CHECKLIST. DO NOT INVENT NEW TOPICS.**

### Verified Section Headings:
{checklist_items}

### Rules:
1. **Every topic in your output MUST be derived from one of the headings above**
2. **DO NOT create topics from learning outcomes (শিখনফল)**
3. **DO NOT create topics from your general knowledge**
4. **DO NOT combine multiple headings into one topic unless they are compound headings**
5. **If a heading is a bare attribute (e.g., "নীতিমালা", "সমস্যা"), prefix it with
   the parent concept from the enclosing section**
6. **You may shorten headings by dropping filler words (বিভিন্ন, উল্লেখযোগ্য) but
   MUST keep the core concept**
7. **You may merge natural pairs (ধারণা + প্রকারভেদ) but MUST keep distinct concepts separate**

---

## What a "topic" is

A topic is a **self-contained concept name that still makes sense on its own**, with
the chapter name and subject hidden. It is a Bengali noun phrase that names *what is
taught*, carrying the concept it is about.

- GOOD: `সমবায় সমিতির নীতিমালা`, `অংশীদারি ব্যবসায়ের চুক্তিপত্র`
- BAD (bare attribute): `নীতিমালা`, `চুক্তিপত্র`, `সমস্যা`
- BAD (meaning-changing qualifier dropped): dropping qualifiers that change meaning

**Keep it short — ≤ 5 words is the goal** (3–8 acceptable, no minimum).

---

## Procedure

### 1. Read the body, not just the box
Use the শিখনফল box only to (a) confirm you missed nothing and (b) correct garbled
spending. Topics come from the **verified headings list above**.

### 2. Match headings to body content
For each verified heading, find where it appears in the chapter body images and
understand what concepts it covers.

### 3. Attach the head noun
For each heading/concept, write the topic so it carries its parent concept. If a
heading is a bare attribute, prefix the concept from the enclosing section.

### 4. Split compounds without orphaning
Split on standalone `এবং`, space-surrounded ` ও `, or commas between parallel
noun phrases — **only if each part keeps its own head noun after the split**.

### 5. Granularity — one row = one 15–30 min study/quiz topic
Do **not** emit `X-এর ধারণা`, `X-এর বৈশিষ্ট্য`, `X-এর গুরুত্ব` as separate rows for
the same X. Merge into `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব`.

### 6. Filter
Drop experimental/lab/verification items.

### 7. Cross-check against the checklist
Every topic MUST correspond to a heading in the verified checklist above. If a
topic doesn't match any heading, REMOVE it — it is hallucinated.

---

## Output

Return ONLY this JSON object (no commentary, no code fences):

```json
{{
  "class": "9-10",
  "subject": "bgs",
  "chapter_no": {chapter_no},
  "chapter_title": "{chapter_title}",
  "learning_outcomes": ["<box bullet verbatim, verbs KEPT>", "..."],
  "topics": ["<self-contained topic derived from verified headings>", "..."],
  "keywords": ["<5–15 revision terms>"],
  "one_line_summary": "<one Bengali sentence>",
  "source_pages": "<pdf start-end>"
}}
```

**VALIDATION**: Before outputting, verify EVERY topic in your list matches a
heading in the checklist above. Remove any that don't match.

IMAGES: the chapter's pages follow, in order.
"""
    
    return constrained_prompt


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate constrained Step 7 prompt")
    parser.add_argument("book_name", help="Book directory name under ocr/")
    parser.add_argument("chapter_no", type=int, help="Chapter number")
    args = parser.parse_args()
    
    headings_data = load_headings(args.book_name, args.chapter_no)
    
    # Try to load subject profile
    subject = "bgs"
    subject_file = os.path.join(ROOT_DIR, "subjects", f"{subject}.md")
    subject_profile = ""
    if os.path.exists(subject_file):
        with open(subject_file, encoding="utf-8") as f:
            subject_profile = f.read()
    
    prompt = generate_constrained_prompt(headings_data, subject_profile)
    
    # Save the constrained prompt
    output_path = os.path.join(
        PROMPTS_DIR, f"constrained_ch{args.chapter_no:02d}.txt"
    )
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print(f"Generated constrained prompt: {output_path}")
    print(f"Chapter: {args.chapter_no} - {headings_data['chapter_title']}")
    print(f"Verified headings: {len(headings_data['headings'])}")
    print(f"\nNext: Use this prompt with the Step 7 agent to generate topic_map.json")


if __name__ == "__main__":
    main()
