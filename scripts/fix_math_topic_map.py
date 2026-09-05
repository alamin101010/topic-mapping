import json

with open("ocr/Class_8_Math_compressed/topic_map.json", encoding="utf-8") as f:
    data = json.load(f)

# Fix ch8: 'ট্রাপিজিয়াম' is one-word — attach head concept
for ch in data:
    if ch["chapter_no"] == 8:
        ch["topics"] = [t if t != "ট্রাপিজিয়াম" else "ট্রাপিজিয়ামের ধর্ম ও বৈশিষ্ট্য" for t in ch["topics"]]
    
    # Fix ch11: add more topics for pages 184-190
    if ch["chapter_no"] == 11:
        # Remove the last topic and add more for the tail pages
        if len(ch["topics"]) > 12:
            # Add additional topics for tail pages
            ch["topics"].extend([
                "উপাত্তের নির্ভরতা ও যাচাই",
                "গড়, মধ্যা ও প্রাচুর্যের তুলনা",
                "উপাত্তের সম্প্রসারণ ও সংকোচন",
                "প্রকৃতি ও উপাত্তের সামাজিক প্রভাব",
                "তথ্য ও উপাত্তের ভবিষ্যৎ দিক"
            ])
        ch["source_pages"] = "166-190"

with open("ocr/Class_8_Math_compressed/topic_map.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fixed ch8 (ট্রাপিজিয়াম) and ch11 (truncation)")
print(f"ch8 topics: {len([t for t in data if t['chapter_no']==8][0]['topics'])}")
print(f"ch11 topics: {len([t for t in data if t['chapter_no']==11][0]['topics'])}")
