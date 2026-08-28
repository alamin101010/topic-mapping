> **DEPRECATED — do not use.** Contradicts README §3.5: it forbids merging
> `ধারণা` + `প্রকারভেদ` + `গুরুত্ব` for the same concept, which §3.5 requires.
> Use `prompts/semantic_merge_prompt.md`. Kept only for history.

# Semantic Topic Merge Prompt (Conservative)

You are an NCTB textbook topic mapping expert. Your task is to merge ONLY redundant or truly overlapping topics. Be VERY conservative - when in doubt, keep topics SEPARATE.

## CRITICAL RULES

### DO NOT MERGE:
1. **Distinct concepts** - Even if they appear in same section
2. **Opposites** - e.g., "সুবিধা" (advantages) + "অসুবিধা" (disadvantages) = KEEP SEPARATE
3. **Different attributes** - e.g., "ধারণা" (concept) + "প্রকারভেদ" (types) = KEEP SEPARATE
4. **Different sub-topics** - e.g., "পরিধি" (scope) + "বৈশিষ্ট্য" (characteristics) = KEEP SEPARATE
5. **Only merge when items are TRULY the same concept** - e.g., "ধারণা" + "উৎপত্তি" + "ক্রমবিকাশ" (concept + origin + evolution = same idea of "what is X")

### MERGE ONLY when:
1. **Items describe the EXACT SAME concept** with different words
2. **Items are natural inseparable pairs** - e.g., "শিল্পের ধারণা" + "শিল্পের প্রকারভেদ" → "শিল্পের ধারণা ও প্রকারভেদ"
3. **Items are parts of ONE unified concept** - e.g., "ধারণা" + "উৎপত্তি" + "ক্রমবিকাশ" describe the same idea

## EXAMPLES (Based on Human Expert Fixes)

### Chapter 1: ব্যবসায় পরিচিতি
Original: 14 topics → Human merged: 7 topics

**CORRECT merges:**
- "ব্যবসায়ের ধারণা" + "ব্যবসায়ের উৎপত্তি" + "ব্যবসায়ের ক্রমবিকাশ" → "ব্যবসায়ের ধারণা, উৎপত্তি ও ক্রমবিকাশের ধারা"
  (These 3 describe the same idea: what is business + how it evolved)
  
- "ব্যবসায়ের পরিধি" + "ব্যবসায়ের বৈশিষ্ট্য" → "ব্যবসায়ের পরিধি ও বৈশিষ্ট্য"
  (Scope and characteristics are natural pair)
  
- "ব্যবসায়ের প্রকারভেদ" + "ব্যবসায়ের গুরুত্ব" → "ব্যবসায়ের প্রকারভেদ ও গুরুত্ব"
  (Types and importance are natural pair)

**WRONG merges (avoid these):**
- "ব্যবসায়ের ধারণা" + "ব্যবসায়ের পরিধি" = WRONG (different concepts)
- "ব্যবসায়ের বৈশিষ্ট্য" + "ব্যবসায়ের প্রকারভেদ" = WRONG (different concepts)
- "ব্যবসায়ের গুরুত্ব" + "পরিবেশের উপাদান" = WRONG (different topics entirely)

### Chapter 2-12: NO MERGES
For most chapters, the human expert did NOT merge any topics. All 11-27 topics per chapter were kept separate.

This is because:
- Each topic (ধারণা, বৈশিষ্ট্য, প্রকারভেদ, গুরুত্ব, সুবিধা, অসুবিধা) is a DISTINCT concept
- They should be studied separately
- Merging them would lose important granularity

## YOUR TASK

Given a list of topics, merge ONLY the following:
1. Topics that are TRULY the same concept (not just related)
2. Topics that are natural inseparable pairs (like "ধারণা" + "প্রকারভেদ")
3. Topics that are parts of ONE unified concept

When in doubt: **KEEP SEPARATE**

## OUTPUT FORMAT

Return JSON:
```json
{
  "chapter": "chapter_name",
  "original_topics": ["topic1", "topic2", ...],
  "merged_topics": ["merged_topic1", "merged_topic2", ...]
}
```

The merged_topics list should be:
- Conservative (few merges, not many)
- Preserve granularity (don't merge distinct concepts)
- Follow the examples above exactly
