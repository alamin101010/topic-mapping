"""Full comparison of human fixes vs automated merge."""
import csv
import io

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
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","উদ্যোগের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","ব্যবসায় উদ্যোগের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","উদ্যোগ ও ব্যবসায় উদ্যোগের পার্থক্য","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","ব্যবসায় উদ্যোগের বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","ব্যবসায় উদ্যোগের কার্যাবলি","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","সফল উদ্যোক্তার গুণাবলি","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","ব্যবসায় উদ্যোগের গুরুত্ব","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","ব্যবসায় উদ্যোগ ও ঝুঁকির সম্পর্ক","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","অনুকূল পরিবেশ","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","উন্নয়নে বাধাসমূহ","",""
"9-10","business entrepreneurship","অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা","বাধা দূরীকরণের করণীয়","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","আত্মকর্মসংস্থানের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","আত্মকর্মসংস্থান ও উদ্যোগের সম্পর্ক","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","প্রশিক্ষণের প্রয়োজনীয়তা","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","উপযুক্ত ক্ষেত্র","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","লাভজনক ক্ষেত্র","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","সহায়তাকারী প্রতিষ্ঠান","",""
"9-10","business entrepreneurship","অধ্যায় ৩: আত্মকর্মসংস্থান","উত্সাহকরণের উপায়","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","ব্যবসায়ের প্রকারভেদ","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","আইনগত বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","একমালিকানা ব্যবসায়ের সংজ্ঞা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","একমালিকানা ব্যবসায়ের বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","একমালিকানা ব্যবসায়ের সুবিধা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","একমালিকানা ব্যবসায়ের অসুবিধা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","একমালিকানা ব্যবসায়ের উপযুক্ত ক্ষেত্র","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","জনপ্রিয়তার কারণ","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","অংশীদারি ব্যবসায়ের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","অংশীদারি ব্যবসায়ের বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","অংশীদারি ব্যবসায়ের সুবিধা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","অংশীদারি ব্যবসায়ের অসুবিধা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","গঠনপ্রণালি","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","চুক্তিপত্র","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","নিবন্ধন","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","অংশীদারদের প্রকারভেদ","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","ভেঙে যাওয়ার কারণ","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","সীমিতমূলধনী ব্যবসায়ের সংজ্ঞা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","সীমিতমূলধনী ব্যবসায়ের বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","পাবলিক কোম্পানি","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","প্রাইভেট কোম্পানি","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","সমবায় সমিতির ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","সমবায় সমিতির বৈশিষ্ট্য","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","সমবায় সমিতির গঠন","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","নীতিমালা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","রাষ্ট্রীয় ব্যবসায়ের ধারণা","",""
"9-10","business entrepreneurship","অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়","রাষ্ট্রীয় ব্যবসায়ের বৈশিষ্ট্য","",""
"""

reader = csv.reader(io.StringIO(human_fix_csv))
header = next(reader)
rows = list(reader)

# Group by chapter
chapters = {}
for row in rows:
    ch = row[2]
    topic = row[3]
    human_topic = row[5] if len(row) > 5 else ""
    if ch not in chapters:
        chapters[ch] = {"topics": [], "merges": []}
    chapters[ch]["topics"].append(topic)
    if human_topic:
        chapters[ch]["merges"].append(human_topic)

print("=" * 70)
print("FULL HUMAN FIX ANALYSIS")
print("=" * 70)

for ch, data in chapters.items():
    topics = data["topics"]
    merges = data["merges"]
    
    print(f"\n{'='*70}")
    print(f"Chapter: {ch}")
    print(f"{'='*70}")
    print(f"  Original topics ({len(topics)}):")
    for i, t in enumerate(topics, 1):
        print(f"    {i}. {t}")
    
    if merges:
        print(f"\n  Human merged topics ({len(merges)}):")
        for i, t in enumerate(merges, 1):
            print(f"    {i}. {t}")
        
        # Calculate reduction
        reduction = len(topics) - len(merges)
        pct = (reduction / len(topics)) * 100
        print(f"\n  Reduction: {len(topics)} → {len(merges)} ({pct:.0f}% reduction)")
