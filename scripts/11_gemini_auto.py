"""Gemini web automation using existing Chrome browser.

Usage:
    python 11_gemini_auto.py <book_folder> <grade> <subject>

Example:
    python 11_gemini_auto.py "Secondary (BV)-2026_Class 9-10_Business Entrepreneurship_compressed" "9-10" "business entrepreneurship"

Requires:
    playwright (pip install playwright)
    Chrome browser installed
"""
import csv
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")
PROMPT_FILE = os.path.join(SCRIPT_DIR, "..", "prompts", "chapter_extract_merge.md")


def load_prompt():
    with open(PROMPT_FILE, encoding="utf-8") as f:
        return f.read()


def main():
    if len(sys.argv) < 4:
        print("Usage: python 11_gemini_auto.py <book_folder> <grade> <subject>")
        sys.exit(1)

    book_folder, grade, subject = sys.argv[1], sys.argv[2], sys.argv[3]

    # Load topic_map.json
    topic_map_path = os.path.join("ocr", book_folder, "topic_map.json")
    if not os.path.exists(topic_map_path):
        print(f"topic_map.json not found: {topic_map_path}", file=sys.stderr)
        sys.exit(1)

    with open(topic_map_path, encoding="utf-8") as f:
        chapters = json.load(f)

    # Build input text for all chapters
    input_text = ""
    for chapter in chapters:
        ch_title = f"অধ্যায় {chapter['chapter_no']}: {chapter['chapter_title']}"
        topics = chapter.get("topics", [])
        topic_list = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
        input_text += f"\n{ch_title}:\n{topic_list}\n"

    # Create the full prompt - MERGE RULES FOR BUSINESS ENTREPRENEURSHIP
    prompt = f"""You are an NCTB Business Entrepreneurship curriculum expert. Merge redundant topics.

## MUST MERGE (these are redundant):
1. "ব্যবসায়ের ধারণা" + "ব্যবসায়ের উৎপত্তি" + "ব্যবসায়ের ক্রমবিকাশ" → "ব্যবসায়ের ধারণা, উৎপত্তি ও ক্রমবিকাশ"
2. "ব্যবসায়ের পরিধি" + "ব্যবসায়ের বৈশিষ্ট্য" → "ব্যবসায়ের পরিধি ও বৈশিষ্ট্য"
3. "ব্যবসায়ের প্রকারভেদ" + "ব্যবসায়ের গুরুত্ব" → "ব্যবসায়ের প্রকারভেদ ও গুরুত্ব"
4. "শিল্পের ধারণা" + "শিল্পের প্রকারভেদ" → "শিল্পের ধারণা ও প্রকারভেদ"
5. "বাণিজ্যের ধারণা" + "বাণিজ্যের প্রকারভেদ" → "বাণিজ্যের ধারণা ও প্রকারভেদ"
6. "সেবার ধারণা" + "সেবার প্রকারভেদ" → "সেবার ধারণা ও প্রকারভেদ"
7. "লাইসেন্সের ধারণা" + "লাইসেন্স পাওয়ার উপায়" → "লাইসেন্সের ধারণা ও পাওয়ার উপায়"
8. "ফ্র্যাঞ্চাইজের ধারণা" + "ফ্র্যাঞ্চাইজ পাওয়ার উপায়" → "ফ্র্যাঞ্চাইজের ধারণা ও পাওয়ার উপায়"
9. "ট্রেডমার্কের ধারণা" + "ট্রেডমার্কের ধরন" + "ট্রেডমার্ক নিবন্ধন পদ্ধতি" → "ট্রেডমার্কের ধারণা, ধরন ও নিবন্ধন পদ্ধতি"
10. "বৃহৎ শিল্পের ধারণা" + "বৃহৎ শিল্পের বৈশিষ্ট্য" + "বৃহৎ শিল্পের গুরুত্ব" → "বৃহৎ শিল্পের ধারণা, বৈশিষ্ট্য ও গুরুত্ব"
11. "সীমিতমূলধনী ব্যবসায়ের সংজ্ঞা" + "সীমিতমূলধনী ব্যবসায়ের বৈশিষ্ট্য" → "সীমিতমূলধনী ব্যবসায়ের সংজ্ঞা ও বৈশিষ্ট্য"

## DO NOT MERGE (keep separate):
1. "সুবিধা" + "অসুবিধা"
2. "একমালিকানা" ≠ "অংশীদারি" ≠ "সীমিতমূলধনী"
3. "রাষ্ট্রের প্রতি" ≠ "সমাজের প্রতি" ≠ "ক্রেতার প্রতি"
4. "পেটেন্ট" ≠ "ট্রেডমার্ক" ≠ "কপিরাইট"

## INPUT:
{input_text}

## OUTPUT: JSON object only. Chapter names as keys, merged topic arrays as values.

Example:
{{
  "অধ্যায় ১: ব্যবসায় পরিচিতি": ["ব্যবসায়ের ধারণা, উৎপত্তি ও ক্রমবিকাশ", "ব্যবসায়ের পরিধি ও বৈশিষ্ট্য", "ব্যবসায়ের প্রকারভেদ ও গুরুত্ব", "শিল্পের ধারণা ও প্রকারভেদ"]
}}"""

    print("=" * 60, file=sys.stderr)
    print("GEMINI WEB AUTOMATION", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Book: {book_folder}", file=sys.stderr)
    print(f"Chapters: {len(chapters)}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Save prompt for reference
    prompt_file = os.path.join(OUTPUT_DIR, "gemini_prompt.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"Prompt saved to: {prompt_file}", file=sys.stderr)

    try:
        from playwright.sync_api import sync_playwright

        print("\nConnecting to Chrome...", file=sys.stderr)
        print("NOTE: Chrome must be running with --remote-debugging-port=9222", file=sys.stderr)
        print("If not, close Chrome and run:", file=sys.stderr)
        print('  chrome.exe --remote-debugging-port=9222', file=sys.stderr)

        with sync_playwright() as p:
            # Connect to existing Chrome instance
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                print("Connected to existing Chrome!", file=sys.stderr)
            except Exception as e:
                print(f"Could not connect: {e}", file=sys.stderr)
                print("Launching new Chrome with debugging port...", file=sys.stderr)
                browser = p.chromium.launch(
                    executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    headless=False,
                    args=["--start-maximized", "--remote-debugging-port=9222"]
                )

            # Use existing context or create new one
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                print(f"Using existing context with {len(context.pages)} tabs", file=sys.stderr)
            else:
                context = browser.new_context(viewport={"width": 1920, "height": 1080})

            # Find or create Gemini tab
            page = None
            for p_tab in context.pages:
                if "gemini" in p_tab.url.lower():
                    page = p_tab
                    print(f"Found existing Gemini tab: {p_tab.url}", file=sys.stderr)
                    break

            if not page:
                page = context.new_page()

            print("Opening Gemini...", file=sys.stderr)
            page.goto("https://gemini.google.com")
            page.wait_for_load_state("networkidle")

            print("Waiting 5s for page to load...", file=sys.stderr)
            time.sleep(5)

            # Find the input area and paste prompt
            print("Pasting prompt...", file=sys.stderr)

            # Try different selectors for the input area
            input_selectors = [
                'div[contenteditable="true"]',
                'textarea',
                '.ql-editor',
                '[data-placeholder]',
                'div[role="textbox"]'
            ]

            input_element = None
            for selector in input_selectors:
                try:
                    input_element = page.wait_for_selector(selector, timeout=5000)
                    if input_element:
                        print(f"  Found input with selector: {selector}", file=sys.stderr)
                        break
                except:
                    continue

            if not input_element:
                print("  Could not find input area. Please paste manually.", file=sys.stderr)
                print(f"\n  Prompt saved to: {prompt_file}", file=sys.stderr)
                input("  Press Enter after pasting and getting response...")
            else:
                # Click and type
                input_element.click()
                time.sleep(0.5)

                # Use clipboard to paste
                page.evaluate(f"navigator.clipboard.writeText(`{prompt}`)")
                page.keyboard.press("Control+V")
                time.sleep(0.5)

                # Press Enter to submit
                page.keyboard.press("Enter")

                print("Waiting for response (up to 90s)...", file=sys.stderr)

                # Wait for response to complete - look for the stop/regenerate button
                for i in range(90):
                    time.sleep(1)
                    # Check if response is still generating
                    try:
                        stop_btn = page.query_selector('button[aria-label="Stop response"]')
                        if not stop_btn:
                            # Response might be done, wait a bit more
                            time.sleep(2)
                            break
                    except:
                        pass

                print("  Extracting response...", file=sys.stderr)

                # Try to find the response - look for code blocks or markdown content
                response_text = ""

                # Method 1: Look for code blocks (JSON is usually in code block)
                try:
                    code_blocks = page.query_selector_all('code')
                    for block in code_blocks:
                        text = block.inner_text()
                        if '{' in text and '}' in text:
                            response_text = text
                            print("  Found JSON in code block", file=sys.stderr)
                            break
                except:
                    pass

                # Method 2: Look for pre blocks
                if not response_text:
                    try:
                        pre_blocks = page.query_selector_all('pre')
                        for block in pre_blocks:
                            text = block.inner_text()
                            if '{' in text and '}' in text:
                                response_text = text
                                print("  Found JSON in pre block", file=sys.stderr)
                                break
                    except:
                        pass

                # Method 3: Get all markdown content
                if not response_text:
                    try:
                        markdown_elements = page.query_selector_all('.markdown, .response-content, message-content')
                        for elem in markdown_elements:
                            text = elem.inner_text()
                            if '{' in text and '}' in text:
                                # Extract JSON from text
                                start = text.find('{')
                                end = text.rfind('}') + 1
                                if start >= 0 and end > start:
                                    response_text = text[start:end]
                                    print("  Found JSON in markdown", file=sys.stderr)
                                    break
                    except:
                        pass

                if not response_text:
                    print("\n  Could not auto-extract response.", file=sys.stderr)
                    print("  Please copy the response manually.", file=sys.stderr)
                    input("  Press Enter after copying response...")

                    # Try to get from clipboard
                    try:
                        response_text = page.evaluate("navigator.clipboard.readText()")
                    except:
                        response_text = ""

            # Save response
            if response_text:
                response_file = os.path.join(OUTPUT_DIR, "gemini_response.json")

                # Clean up response
                clean = response_text.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[1]
                if clean.endswith("```"):
                    clean = clean.rsplit("```", 1)[0]

                with open(response_file, "w", encoding="utf-8") as f:
                    f.write(clean)

                print(f"\nResponse saved to: {response_file}", file=sys.stderr)

                # Parse and apply merge
                try:
                    data = json.loads(clean)
                    apply_merge(data, chapters, book_folder, grade, subject)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}", file=sys.stderr)
                    print("Please fix the JSON file and run import manually.", file=sys.stderr)
            else:
                print("\nNo response captured.", file=sys.stderr)
                print("Please save the response manually and run:", file=sys.stderr)
                print(f"  python 10_extract_merge.py output/{book_folder}.csv --import output/gemini_response.json", file=sys.stderr)

            browser.close()

    except ImportError:
        print("Error: playwright not installed", file=sys.stderr)
        print("Run: pip install playwright", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def apply_merge(data, chapters, book_folder, grade, subject):
    """Apply merge data to create CSV."""
    all_topics = []

    for chapter in chapters:
        ch_title = f"অধ্যায় {chapter['chapter_no']}: {chapter['chapter_title']}"
        merged_topics = data.get(ch_title, chapter.get("topics", []))

        if not isinstance(merged_topics, list):
            merged_topics = chapter.get("topics", [])

        for topic in merged_topics:
            all_topics.append({
                "grade": grade,
                "subject": subject,
                "chapter": ch_title,
                "topic": topic
            })

    # Write CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{book_folder}.csv")

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["grade", "subject", "chapter", "topic"],
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(all_topics)

    print(f"\nCSV written: {output_path} ({len(all_topics)} topics)", file=sys.stderr)


if __name__ == "__main__":
    main()
