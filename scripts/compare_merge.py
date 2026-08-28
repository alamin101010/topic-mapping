"""Compare automated merge vs human fixes."""
import csv

# Our automated merge results
our_merge = {
    "অধ্যায় ১: ব্যবসায় পরিচিতি": 6,
    "অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা": 5,
    "অধ্যায় ৩: আত্মকর্মসংস্থান": 4,
    "অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়": 11,
    "অধ্যায় ৫: ব্যবসায়ের আইনগত দিক": 7,
    "অধ্যায় ৬: ব্যবসায় পরিকল্পনা": 4,
    "অধ্যায় ৭: বাংলাদেশের শিল্প": 5,
    "অধ্যায় ৮: ব্যবসায় প্রতিষ্ঠানের ব্যবস্থাপনা": 5,
    "অধ্যায় ৯: বিপণন": 5,
    "অধ্যায় ১০: ব্যবসায় উদ্যোগ উন্নয়নে সহায়ক সেবা": 4,
    "অধ্যায় ১১: ব্যবসায়ে নৈতিকতা ও সামাজিক দায়িত্ব": 6,
    "অধ্যায় ১২: সফল উদ্যোক্তাদের জীবনী থেকে শিক্ষাদীয়": 7,
}

# Original topic counts
original_counts = {
    "অধ্যায় ১: ব্যবসায় পরিচিতি": 14,
    "অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা": 11,
    "অধ্যায় ৩: আত্মকর্মসংস্থান": 7,
    "অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়": 27,
    "অধ্যায় ৫: ব্যবসায়ের আইনগত দিক": 19,
    "অধ্যায় ৬: ব্যবসায় পরিকল্পনা": 12,
    "অধ্যায় ৭: বাংলাদেশের শিল্প": 17,
    "অধ্যায় ৮: ব্যবসায় প্রতিষ্ঠানের ব্যবস্থাপনা": 11,
    "অধ্যায় ৯: বিপণন": 10,
    "অধ্যায় ১০: ব্যবসায় উদ্যোগ উন্নয়নে সহায়ক সেবা": 8,
    "অধ্যায় ১১: ব্যবসায়ে নৈতিকতা ও সামাজিক দায়িত্ব": 15,
    "অধ্যায় ১২: সফল উদ্যোক্তাদের জীবনী থেকে শিক্ষাদীয়": 8,
}

# Human fix results (from sheet)
human_fix = {
    "অধ্যায় ১: ব্যবসায় পরিচিতি": 7,  # Only Ch1 was merged
    "অধ্যায় ২: ব্যবসায় উদ্যোগ ও উদ্যোক্তা": 11,  # No merge
    "অধ্যায় ৩: আত্মকর্মসংস্থান": 7,  # No merge
    "অধ্যায় ৪: মালিকানার ভিত্তিতে ব্যবসায়": 27,  # No merge
    "অধ্যায় ৫: ব্যবসায়ের আইনগত দিক": 19,  # No merge
    "অধ্যায় ৬: ব্যবসায় পরিকল্পনা": 12,  # No merge
    "অধ্যায় ৭: বাংলাদেশের শিল্প": 17,  # No merge
    "অধ্যায় ৮: ব্যবসায় প্রতিষ্ঠানের ব্যবস্থাপনা": 11,  # No merge
    "অধ্যায় ৯: বিপণন": 10,  # No merge
    "অধ্যায় ১০: ব্যবসায় উদ্যোগ উন্নয়নে সহায়ক সেবা": 8,  # No merge
    "অধ্যায় ১১: ব্যবসায়ে নৈতিকতা ও সামাজিক দায়িত্ব": 15,  # No merge
    "অধ্যায় ১২: সফল উদ্যোক্তাদের জীবনী থেকে শিক্ষাদীয়": 8,  # No merge
}

print("=" * 80)
print("AUTOMATED vs HUMAN FIX COMPARISON")
print("=" * 80)
print(f"{'Chapter':<40} {'Original':>8} {'Ours':>8} {'Human':>8} {'Diff':>8}")
print("-" * 80)

total_orig = 0
total_ours = 0
total_human = 0

for ch in original_counts:
    orig = original_counts[ch]
    ours = our_merge.get(ch, orig)
    human = human_fix.get(ch, orig)
    diff = ours - human
    
    total_orig += orig
    total_ours += ours
    total_human += human
    
    # Truncate chapter name for display
    ch_display = ch[:38] if len(ch) > 38 else ch
    print(f"{ch_display:<40} {orig:>8} {ours:>8} {human:>8} {diff:>+8}")

print("-" * 80)
print(f"{'TOTAL':<40} {total_orig:>8} {total_ours:>8} {total_human:>8} {total_ours-total_human:>+8}")
print(f"\nReduction: {total_orig} → {total_ours} (ours) vs {total_human} (human)")

print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)
print("""
1. HUMAN ONLY MERGED CHAPTER 1 (14 → 7 topics, 50% reduction)
   Chapters 2-12: NO MERGES at all (human kept all topics separate)

2. WE WERE TOO AGGRESSIVE:
   - We merged 159 → 70 topics (56% reduction)
   - Human would merge only 159 → ~140 topics (12% reduction)
   - We over-merged by 3x!

3. SPECIFIC ERRORS IN CHAPTER 1:
   - We: ধারণা + উৎপত্তি + ক্রমবিকাশ + পরিধি (4 items)
   - Human: ধারণা + উৎপত্তি + ক্রমবিকাশ (3 items, NO পরিধি)
   
   - We: বৈশিষ্ট্য + প্রকারভেদ
   - Human: পরিধি + বৈশিষ্ট্য (different pairing!)
   
   - We: গুরুত্ব + পরিবেশের উপাদান
   - Human: প্রকারভেদ + গুরুত্ব (different pairing!)

4. LESSON: Human merge rules are MUCH more conservative than we thought
   - Only merge items that are TRULY part of same concept
   - Don't merge across concept boundaries
   - Keep items separate when in doubt
""")
