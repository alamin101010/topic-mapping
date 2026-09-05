import json

# Fix ch11 heading checklist
with open('ocr/Class_8_Math_compressed/headings/ch11.json', 'r', encoding='utf-8') as f:
    ch11 = json.load(f)
ch11['headings'] = ch11['headings'][:17]
with open('ocr/Class_8_Math_compressed/headings/ch11.json', 'w', encoding='utf-8') as f:
    json.dump(ch11, f, indent=2, ensure_ascii=False)
print(f'ch11 headings: {len(ch11["headings"])}')

# Fix ch8 heading checklist - remove standalone 'ট্রাপিজিয়াম' heading
with open('ocr/Class_8_Math_compressed/headings/ch08.json', 'r', encoding='utf-8') as f:
    ch8 = json.load(f)
ch8['headings'] = [h for h in ch8['headings'] if h['heading'] != 'ট্রাপিজিয়াম']
with open('ocr/Class_8_Math_compressed/headings/ch08.json', 'w', encoding='utf-8') as f:
    json.dump(ch8, f, indent=2, ensure_ascii=False)
print(f'ch8 headings: {len(ch8["headings"])}')
print('Done')
