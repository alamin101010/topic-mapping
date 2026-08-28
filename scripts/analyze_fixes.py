"""Analyze human fixes vs automated merge."""
import csv
import io

# Human fix data from Google Sheets
human_fix_csv = """"grade","subject","chapter","topic","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের ধারণা","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","ব্যবসায়ের ধারণা, উৎপত্তি ও ক্রমবিকাশের ধারা"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের উৎপত্তি","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","ব্যবসায়ের পরিধি ও বৈশিষ্ট্য"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের ক্রমবিকাশ","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","ব্যবসায়ের প্রকারভেদ ও গুরুত্ব"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের পরিধি","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","শিল্পের ধারণা ও প্রকারভেদ"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের বৈশিষ্ট্য","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","বাণিজ্যের ধারণা ও প্রকারভেদ"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের প্রকারভেদ","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","সেবার ধারণা ও প্রকারভেদ"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","ব্যবসায়ের গুরুত্ব","প্রথম অধ্যায়: ব্যবসায় পরিচিতি","ব্যবসায়ের উপর প্রভাব বিস্তারকারী পরিবেশের উপাদানসমূহ"
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","শিল্পের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","শিল্পের প্রকারভেদ","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","বাণিজ্যের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","বাণিজ্যের প্রকারভেদ","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","সেবার ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","সেবার প্রকারভেদ","",""
"9-10","business entrepreneurship","অধ্যায় ১: ব্যবসায় পরিচিতি","পরিবেশের উপাদান","",""
"""

# Parse human fix
reader = csv.reader(io.StringIO(human_fix_csv))
header = next(reader)
rows = list(reader)

# Extract human merged topics (from column F, skipping empty)
human_merges = {}
for row in rows:
    ch = row[2]
    topic = row[3]
    human_topic = row[5] if len(row) > 5 else ""
    
    if ch not in human_merges:
        human_merges[ch] = []
    
    if human_topic:
        human_merges[ch].append(human_topic)

print("=" * 70)
print("HUMAN FIX ANALYSIS - Chapter 1")
print("=" * 70)
print("\nHuman merged topics (from column F):")
for i, topic in enumerate(human_merges.get("অধ্যায় ১: ব্যবসায় পরিচিতি", []), 1):
    print(f"  {i}. {topic}")

print("\n" + "=" * 70)
print("COMPARISON WITH OUR AUTOMATED MERGE")
print("=" * 70)

# Our automated merge for Chapter 1
our_merge = [
    "ব্যবসায়ের ধারণা, উৎপত্তি, ক্রমবিকাশ ও পরিধি",
    "ব্যবসায়ের বৈশিষ্ট্য ও প্রকারভেদ",
    "ব্যবসায়ের গুরুত্ব ও পরিবেশের উপাদান",
    "শিল্পের ধারণা ও প্রকারভেদ",
    "বাণিজ্যের ধারণা ও প্রকারভেদ",
    "সেবার ধারণা ও প্রকারভেদ"
]

human_merge = human_merges.get("অধ্যায় ১: ব্যবসায় পরিচিতি", [])

print("\nOur merge (6 topics):")
for i, topic in enumerate(our_merge, 1):
    print(f"  {i}. {topic}")

print("\nHuman merge (7 topics):")
for i, topic in enumerate(human_merge, 1):
    print(f"  {i}. {topic}")

print("\n" + "=" * 70)
print("ERRORS FOUND")
print("=" * 70)

errors = []

# Check for differences
if len(our_merge) != len(human_merge):
    errors.append(f"Topic count mismatch: Ours={len(our_merge)}, Human={len(human_merge)}")

# Check specific differences
print("\n1. MERGE GROUP DIFFERENCES:")
print("   Ours: 'ব্যবসায়ের ধারণা, উৎপত্তি, ক্রমবিকাশ ও পরিধি' (4 items)")
print("   Human: 'ব্যবসায়ের ধারণা, উৎপত্তি ও ক্রমবিকাশের ধারা' (3 items)")
print("   → We included 'পরিধি' incorrectly")

print("\n2. MERGE GROUP DIFFERENCES:")
print("   Ours: 'ব্যবসায়ের বৈশিষ্ট্য ও প্রকারভেদ'")
print("   Human: 'ব্যবসায়ের পরিধি ও বৈশিষ্ট্য'")
print("   → We merged 'প্রকারভেদ' with 'বৈশিষ্ট্য', Human merged 'পরিধি' with 'বৈশিষ্ট্য'")

print("\n3. MERGE GROUP DIFFERENCES:")
print("   Ours: 'ব্যবসায়ের গুরুত্ব ও পরিবেশের উপাদান'")
print("   Human: 'ব্যবসায়ের প্রকারভেদ ও গুরুত্ব'")
print("   → We merged 'গুরুত্ব' with 'পরিবেশ', Human merged 'গুরুত্ব' with 'প্রকারভেদ'")

print("\n4. HUMAN HAS EXTRA TOPIC:")
print("   Human: 'ব্যবসায়ের উপর প্রভাব বিস্তারকারী পরিবেশের উপাদানসমূহ'")
print("   → This is a separate topic that Human kept standalone")
