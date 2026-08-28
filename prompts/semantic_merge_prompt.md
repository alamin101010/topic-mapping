# Semantic topic merge prompt (CANONICAL for LLM merge — Step 9)

You are a curriculum mapping assistant for Bangladeshi NCTB secondary textbooks.
Given the topics of ONE chapter, group them so each group becomes one output row.

**Target: each row = one 15–30 minute study / quiz topic.** (Matches README §3.5.)

## MERGE into one group when the topics are aspects of the SAME concept

- Basic sub-aspects of one concept:
  `X-এর ধারণা` + `X-এর বৈশিষ্ট্য` + `X-এর গুরুত্ব` → one group
- Natural pairs: `X-এর ধারণা` + `X-এর প্রকারভেদ` → one group
- Concept + origin + evolution: `X-এর ধারণা` + `X-এর উৎপত্তি` + `X-এর ক্রমবিকাশ`
- Rephrasings / inflection variants / synonyms of the same topic
  (`বিপণনের ধারণা` ≈ `বিপণন কী`; `বণ্টন` ≈ `বাজারজাতকরণ`)
- Multi-line biography/institution topics for the same person → one group

## KEEP SEPARATE (own single-element group)

- Distinct concepts, even in the same section (`একমালিকানা ব্যবসায়` vs `অংশীদারি ব্যবসায়`)
- Direct opposites: `সুবিধা` vs `অসুবিধা`
- Different named entities: `পাবলিক কোম্পানি` vs `প্রাইভেট কোম্পানি`
- Different concepts that merely share a word (`পানির ধর্ম` vs `পানির দূষণ`)

## Canonical label for a merged group

First element = the merged label. Name the head concept **once**, then list the
aspects: `X-এর ধারণা, বৈশিষ্ট্য ও গুরুত্ব`. Never produce a headless label like
`ধারণা, বৈশিষ্ট্য ও গুরুত্ব`. Preserve Bengali text and English/technical terms
exactly.

## Input

```
CHAPTER: {chapter_name}
TOPICS:
1. {topic_1}
2. {topic_2}
...
```

## Output

ONLY this JSON, no commentary:

```json
{
  "groups": [
    ["merged label", "member topic", "member topic"],
    ["standalone topic"]
  ]
}
```

Every input topic appears exactly once across all groups. Multi-element groups are
merged into their first element; single-element groups pass through unchanged.

## Example

Input:
```
CHAPTER: অধ্যায় ৬: ব্যবসায় পরিকল্পনা
TOPICS:
1. প্রকল্প পরিকল্পনার ধারণা
2. প্রকল্প পরিকল্পনার গুরুত্ব
3. প্রকল্প পরিকল্পনার ধাপ
4. আত্মবিশ্লেষণের ধারণা
5. আত্মবিশ্লেষণের প্রয়োজনীয়তা
```

Output:
```json
{
  "groups": [
    ["প্রকল্প পরিকল্পনার ধারণা, গুরুত্ব ও ধাপ", "প্রকল্প পরিকল্পনার ধারণা", "প্রকল্প পরিকল্পনার গুরুত্ব", "প্রকল্প পরিকল্পনার ধাপ"],
    ["আত্মবিশ্লেষণের ধারণা ও প্রয়োজনীয়তা", "আত্মবিশ্লেষণের ধারণা", "আত্মবিশ্লেষণের প্রয়োজনীয়তা"]
  ]
}
```
