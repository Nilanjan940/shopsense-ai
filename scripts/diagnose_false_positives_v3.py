import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.intent_v3 import IntentExtractor

extractor = IntentExtractor()

tests = [
    ("unrelated number", "Show me shoes for 8 people",
     {"category": "sneakers"}),

    ("order number", "My order number is 8, show me shoes",
     {"category": "sneakers"}),

    ("medium price", "Show me medium-priced watches",
     {"category": "watches"}),

    ("large collection", "Show me a large collection of watches",
     {"category": "watches"}),

    ("small budget", "I have a small budget for sneakers",
     {"category": "sneakers"}),

    ("positive colour", "Show me black sneakers",
     {"category": "sneakers", "colour": "black"}),

    ("colour negation", "Don't show me red sneakers",
     {"category": "sneakers"}),

    ("colour exclusion", "Show me sneakers, not black",
     {"category": "sneakers"}),

    ("unrelated measurement", "Show me shoes with an 8-inch heel",
     {"category": "sneakers"}),

    ("positive budget", "Show me watches not more than 2000",
     {"category": "watches", "max_price": 2000}),

    ("explicit size", "Show me watches in size M",
     {"category": "watches", "size": "M"}),

    ("multiple constraints", "Black sneakers size 8 under 2000",
     {"category": "sneakers", "colour": "black",
      "size": "8", "max_price": 2000}),
]

print("=" * 78)
print("SHOPSENSE AI - FALSE POSITIVE AND AMBIGUITY DIAGNOSTICS")
print("=" * 78)

for name, query, expected in tests:
    actual = extractor.extract(query)

    # Exact comparison: unexpected extra filters are also failures.
    passed = actual == expected

    print(f"\n[{'PASS' if passed else 'REVIEW'}] {name}")
    print(f"  Query:    {query}")
    print(f"  Expected: {expected}")
    print(f"  Actual:   {actual}")

print("\n" + "=" * 78)
print("DIAGNOSTIC COMPLETE")
print("REVIEW cases are potential extraction weaknesses, not benchmark failures.")
print("=" * 78)
