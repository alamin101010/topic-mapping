"""Assemble atomized topics into Markdown table format."""
import csv
import json
import os
import sys

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def create_atomized_table(topic_map_path: str, output_md: str):
    """Convert topic map JSON to atomized Markdown table."""
    with open(topic_map_path, encoding="utf-8") as f:
        topic_map = json.load(f)

    rows = []
    for chapter in topic_map:
        chapter_label = f"{chapter['chapter_no']}: {chapter['chapter_title']}"
        for topic in chapter.get("topics", []):
            rows.append((chapter_label, topic))

    # Write Markdown table
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_md)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("| Chapter | Topic |\n")
        f.write("|---------|-------|\n")
        for chapter_label, topic in rows:
            f.write(f"| {chapter_label} | {topic} |\n")

    print(f"Atomized table written to {output_path}")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python 07_atomize.py <topic_map.json> <output.md>")
        sys.exit(1)

    create_atomized_table(sys.argv[1], sys.argv[2])
