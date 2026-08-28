"""Step 10: Semantic merge using LLM or manual Gemini web.

Usage:
    # API mode (requires GEMINI_API_KEY)
    python 09_semantic_merge.py <csv_path>

    # Manual mode
    python 09_semantic_merge.py <csv_path> --export
    python 09_semantic_merge.py <csv_path> --import <response_file>

Example:
    python 09_semantic_merge.py "output/Secondary (BV)-2026_Class 9-10_Business Entrepreneurship_compressed.csv"
"""
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(__file__)
PROMPT_FILE = os.path.join(SCRIPT_DIR, "..", "prompts", "semantic_merge_prompt.md")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def load_prompt():
    """Load the semantic merge prompt template."""
    with open(PROMPT_FILE, encoding="utf-8") as f:
        return f.read()


def call_gemini(prompt, api_key, max_retries=5):
    """Call Gemini API with the given prompt."""
    url = f"{GEMINI_API_URL}?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
        },
    }

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(max_retries):
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
                return text.strip()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            if e.code == 429:  # Rate limit
                wait_time = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            print(f"Gemini API error {e.code}: {error_body}", file=sys.stderr)
            sys.exit(1)

    print("Max retries exceeded", file=sys.stderr)
    sys.exit(1)


def parse_merge_groups(llm_response):
    """Parse LLM JSON response into merge groups."""
    try:
        data = json.loads(llm_response)
        groups = data.get("groups", [])
        return groups
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        print(f"Response was: {llm_response[:500]}", file=sys.stderr)
        return []


def build_merge_map(groups):
    """Build a mapping from each topic to its canonical form."""
    merge_map = {}
    for group in groups:
        if len(group) < 1:
            continue
        canonical = group[0]
        for topic in group:
            merge_map[topic] = canonical
    return merge_map


def merge_chapter_topics(chapter_name, topics, api_key, dry_run=False):
    """Merge similar topics in a chapter using LLM."""
    if len(topics) <= 1:
        return topics, []

    prompt_template = load_prompt()
    topic_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))
    prompt = prompt_template.replace("{chapter_name}", chapter_name).replace(
        "{topic_1}\n2. {topic_2}\n...", topic_list
    )

    if dry_run:
        print(f"\n--- Chapter: {chapter_name} ---")
        print(f"Input topics ({len(topics)}):")
        for t in topics:
            print(f"  - {t}")

    response = call_gemini(prompt, api_key)
    groups = parse_merge_groups(response)
    merge_map = build_merge_map(groups)

    if dry_run:
        print(f"LLM merge groups:")
        for group in groups:
            if len(group) > 1:
                print(f"  MERGE: {group}")
            else:
                print(f"  KEEP:  {group[0]}")

    merged_topics = []
    seen_canonical = set()
    for topic in topics:
        canonical = merge_map.get(topic, topic)
        if canonical not in seen_canonical:
            merged_topics.append(canonical)
            seen_canonical.add(canonical)

    removed = [t for t in topics if t not in merged_topics]

    return merged_topics, removed


def merge_csv_api(csv_path, dry_run=False):
    """Merge similar topics using Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    chapters = defaultdict(list)
    for row in rows:
        if len(row) >= 4:
            chapters[row[2]].append(row)

    merged_all = []
    total_removed = 0

    for i, (ch_label, ch_rows) in enumerate(chapters.items()):
        if i > 0:
            time.sleep(30)  # Wait 30s between chapters for free tier

        topics = [row[3] for row in ch_rows]
        print(f"Processing chapter {i+1}/{len(chapters)}: {ch_label}...", file=sys.stderr)

        merged_topics, removed = merge_chapter_topics(ch_label, topics, api_key, dry_run)
        total_removed += len(removed)

        for topic in merged_topics:
            for row in ch_rows:
                if row[3] == topic:
                    merged_all.append(row)
                    break
            else:
                if ch_rows:
                    new_row = list(ch_rows[0])
                    new_row[3] = topic
                    merged_all.append(new_row)

    if dry_run:
        print(f"\n=== Summary ===")
        print(f"Original: {len(rows)} topics")
        print(f"After merge: {len(merged_all)} topics")
        print(f"Removed: {total_removed} topics")
        return csv_path

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(merged_all)

    print(f"Merged CSV written: {csv_path} ({len(rows)} -> {len(merged_all)} topics)")
    return csv_path


def export_for_gemini(csv_path):
    """Export chapter topics for manual Gemini processing."""
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    chapters = defaultdict(list)
    for row in rows:
        if len(row) >= 4:
            chapters[row[2]].append(row[3])

    prompt_template = load_prompt()
    full_prompt = prompt_template.replace(
        "{chapter_name}\nTOPICS:\n1. {topic_1}\n2. {topic_2}\n...", ""
    ).strip()

    full_prompt += "\n\n## Chapters to process:\n\n"
    for ch_name, topics in chapters.items():
        topic_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))
        full_prompt += f"### CHAPTER: {ch_name}\nTOPICS:\n{topic_list}\n\n"

    prompt_file = os.path.join(os.path.dirname(csv_path), "gemini_prompt.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(full_prompt)

    print(f"Prompt saved to: {prompt_file}")
    print("Copy the prompt into Gemini, then save the response to a .json file")
    print(f"Then run: python 09_semantic_merge.py {csv_path} --import <response_file>")
    return full_prompt


def import_and_merge(csv_path, response_file):
    """Import Gemini response and apply merge to CSV."""
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    with open(response_file, encoding="utf-8") as f:
        content = f.read().strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {response_file}: {e}", file=sys.stderr)
        sys.exit(1)

    chapters_data = data.get("chapters", data)
    if isinstance(chapters_data, dict):
        chapter_groups = {ch["chapter"]: ch["groups"] for ch in chapters_data.get("chapters", [])}
    else:
        chapter_groups = chapters_data

    chapters = defaultdict(list)
    for row in rows:
        if len(row) >= 4:
            chapters[row[2]].append(row)

    merged_all = []
    total_removed = 0

    for ch_label, ch_rows in chapters.items():
        topics = [row[3] for row in ch_rows]
        groups = chapter_groups.get(ch_label, [])
        if not groups:
            merged_all.extend(ch_rows)
            continue

        merge_map = {}
        for group in groups:
            if len(group) > 0:
                canonical = group[0]
                for topic in group:
                    merge_map[topic] = canonical

        seen_canonical = set()
        merged_topics = []
        for topic in topics:
            canonical = merge_map.get(topic, topic)
            if canonical not in seen_canonical:
                merged_topics.append(canonical)
                seen_canonical.add(canonical)

        removed = len(topics) - len(merged_topics)
        total_removed += removed

        for topic in merged_topics:
            for row in ch_rows:
                if row[3] == topic:
                    merged_all.append(row)
                    break
            else:
                if ch_rows:
                    new_row = list(ch_rows[0])
                    new_row[3] = topic
                    merged_all.append(new_row)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(merged_all)

    print(f"Merged CSV written: {csv_path} ({len(rows)} -> {len(merged_all)} topics)")
    print(f"Removed {total_removed} duplicate/similar topics")
    return csv_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  API mode:    python 09_semantic_merge.py <csv_path>")
        print("  Export:      python 09_semantic_merge.py <csv_path> --export")
        print("  Import:      python 09_semantic_merge.py <csv_path> --import <response_file>")
        sys.exit(1)

    csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    if "--export" in sys.argv:
        export_for_gemini(csv_path)
    elif "--import" in sys.argv:
        idx = sys.argv.index("--import")
        if idx + 1 >= len(sys.argv):
            print("Error: --import requires a response file path")
            sys.exit(1)
        response_file = sys.argv[idx + 1]
        if not os.path.exists(response_file):
            print(f"Response file not found: {response_file}")
            sys.exit(1)
        import_and_merge(csv_path, response_file)
    else:
        merge_csv_api(csv_path, "--dry-run" in sys.argv)
