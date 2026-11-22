import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.shopsense.engine.intent import (
    IntentExtractor,
    _phrase_matches,
    _extract_size,
)

extractor = IntentExtractor()

tests = [
    "I need Urbanyx black pair of jeans size 32, below 2000",
    "casual sneakers size 9, by Kudova",
    "UK 10",
    "show me Strydo blue runners UK 8, less than 5500",
    "size eight actually six",
    "UK 7 no no, UK 6",
    "das number",
    "mere liye blue jogging shoes budget Rs. 4000, das number milega?",
]

print("AVAILABLE SIZE PHRASES:")
for key in ["6", "7", "8", "9", "10", "11", "28", "30", "32", "34", "36"]:
    print(f"{key}: {extractor.size_phrases.get(key)}")

print("\nDIRECT EXTRACTION:")
for text in tests:
    result = extractor.extract(text)
    print(f"\nInput: {text}")
    print(f"Extracted size: {result.get('size')}")

    for key in ["6", "7", "8", "9", "10", "32"]:
        matches = _phrase_matches(text.lower(), key)
        if matches:
            print(f"  Match {key}: {[m.group() for m in matches]}")

    print(f"  Final internal size result: {_extract_size(text.lower(), extractor.size_phrases)}")
