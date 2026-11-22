import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.intent_v3 import IntentExtractor

extractor = IntentExtractor()

tests = [
    ("basic category", "I need black sneakers", {"category": "sneakers", "colour": "black"}),
    ("category synonym", "Show me some joggers", {"category": "track pants"}),
    ("category synonym", "I want a backpack", {"category": "backpacks"}),
    ("colour alias", "Find navy blue shoes", {"category": "sneakers", "colour": "navy"}),
    ("colour alias", "I want grey joggers", {"category": "track pants", "colour": "grey"}),
    ("size context", "I need size 8 shoes", {"category": "sneakers", "size": "8"}),
    ("spoken size", "Show me size eight sneakers", {"category": "sneakers", "size": "8"}),
    ("size correction", "I need size 8, actually 7", {"size": "7"}),
    ("colour correction", "Show me black shoes, no, red shoes", {"category": "sneakers", "colour": "red"}),
    ("budget numeric", "Show me shoes under 2000", {"category": "sneakers", "max_price": 2000}),
    ("budget thousand", "Find shoes below 2k", {"category": "sneakers", "max_price": 2000}),
    ("budget words", "I need shoes under two thousand", {"category": "sneakers", "max_price": 2000}),
    ("budget correction", "Under 2000, actually under 1500", {"max_price": 1500}),
    ("hinglish budget", "Shoes 2000 tak", {"category": "sneakers", "max_price": 2000}),
    ("hinglish colour", "Kaala shoes chahiye", {"category": "sneakers", "colour": "black"}),
]

passed = 0
failed = 0

print("=" * 72)
print("SHOPSENSE AI - INTENT ROBUSTNESS TEST")
print("=" * 72)

for name, text, expected in tests:
    actual = extractor.extract(text)
    ok = all(actual.get(k) == v for k, v in expected.items())

    if ok:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"

    print(f"\n[{status}] {name}")
    print(f"  Input:    {text}")
    print(f"  Expected: {expected}")
    print(f"  Actual:   {actual}")

print("\n" + "=" * 72)
print(f"RESULT: {passed}/{len(tests)} passed, {failed} failed")
print("=" * 72)

sys.exit(1 if failed else 0)
