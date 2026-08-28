"""Step 10: Semantic merge - Manual workflow (no API required).

Usage:
    # Export topics to paste into Gemini/ChatGPT
    python 10_extract_merge.py <csv_path> --export

    # Import AI response and apply merge
    python 10_extract_merge.py <csv_path> --import <response_file>

Example:
    python 10_extract_merge.py "output/...csv" --export
    python 10_extract_merge.py "output/...csv" --import gemini_response.json
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")

EXPORT_PROMPT = """You are an expert Educational Curriculum Specialist for Bangladeshi NCTB textbooks.

Given the chapter topics below, merge them into optimal granularity following these rules:

1. MERGE basic sub-aspects: "X-এর ধারণা" + "X-এর বৈশিষ্ট্য" + "X-এর গুরুত্ব" → "X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব"
2. MERGE functional pairs: "বাণিজ্যের ধারণা" + "বাণিজ্যের প্রকারভেদ" → "বাণিজ্যের ধারণা ও প্রকারভেদ"
3. KEEP distinct concepts: "একমালিকানা ব্যবসায়" ≠ "অংশীদারি ব্যবসায়"
4. KEEP opposites: "সুবিধা" ≠ "অসুবিধা"
5. Target: 15-30 min study topics per row

INPUT:
{input_text}

OUTPUT: Return ONLY a JSON object with chapter names as keys and merged topic arrays as values.
Example:
{{
  "অধ্যায় ১: ব্যবসায় পরিচিতি": ["Merged Topic 1", "Merged Topic 2"],
  "অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা": ["Topic A", "Topic B"]
}}"""


def export_for_ai(csv_path):
    """Export chapters for AI processing."""
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    chapters = defaultdict(list)
    for row in rows:
        if len(row) >= 4:
            chapters[row[2]].append(row[3])

    # Build input text
    input_text = ""
    for ch_name, topics in chapters.items():
        topic_list = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
        input_text += f"\n{ch_name}:\n{topic_list}\n"

    prompt = EXPORT_PROMPT.format(input_text=input_text)

    # Save prompt
    prompt_file = os.path.join(os.path.dirname(csv_path), "ai_merge_prompt.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    print("=" * 60, file=sys.stderr)
    print("INSTRUCTIONS:", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"1. Prompt saved to: {prompt_file}", file=sys.stderr)
    print("2. Copy the prompt into ChatGPT/Gemini/Claude", file=sys.stderr)
    print("3. Copy the JSON response", file=sys.stderr)
    print(f"4. Save it to: {os.path.join(os.path.dirname(csv_path), 'ai_response.json')}", file=sys.stderr)
    print(f"5. Run: python 10_extract_merge.py {csv_path} --import ai_response.json", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


def import_and_merge(csv_path, response_file):
    """Import AI response and apply merge."""
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
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Group rows by chapter
    chapters = defaultdict(list)
    for row in rows:
        if len(row) >= 4:
            chapters[row[2]].append(row)

    merged_all = []
    total_original = 0
    total_merged = 0

    for ch_label, ch_rows in chapters.items():
        topics = [row[3] for row in ch_rows]
        total_original += len(topics)

        # Get merged topics from AI response
        merged_topics = data.get(ch_label, topics)
        if not isinstance(merged_topics, list):
            merged_topics = topics

        total_merged += len(merged_topics)

        # Rebuild rows
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

    # Write CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, os.path.basename(csv_path))

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(merged_all)

    print(f"CSV written: {output_path}", file=sys.stderr)
    print(f"Topics: {total_original} → {total_merged} (removed {total_original - total_merged})", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  Export: python 10_extract_merge.py <csv_path> --export", file=sys.stderr)
        print("  Import: python 10_extract_merge.py <csv_path> --import <response_file>", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    if "--export" in sys.argv:
        export_for_ai(csv_path)
    elif "--import" in sys.argv:
        idx = sys.argv.index("--import")
        if idx + 1 >= len(sys.argv):
            print("Error: --import requires a file path", file=sys.stderr)
            sys.exit(1)
        response_file = sys.argv[idx + 1]
        if not os.path.exists(response_file):
            print(f"File not found: {response_file}", file=sys.stderr)
            sys.exit(1)
        import_and_merge(csv_path, response_file)
    else:
        print("Use --export or --import <file>", file=sys.stderr)
