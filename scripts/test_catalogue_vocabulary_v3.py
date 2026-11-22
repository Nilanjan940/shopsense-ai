import sys
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.intent_v3 import IntentExtractor

CATALOGUE = ROOT / "competition" / "catalogue.csv"
extractor = IntentExtractor()

with CATALOGUE.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

fields = {
    "category": "category",
    "brand": "brand",
    "colour": "colour",
    "size": "size",
}

failures = []
total = 0
passed = 0

print("=" * 72)
print("SHOPSENSE AI - EXHAUSTIVE CATALOGUE VOCABULARY TEST")
print("=" * 72)

for field, output_field in fields.items():
    values = sorted({
        row[field].strip()
        for row in rows
        if row.get(field, "").strip()
    })

    print(f"\n--- {field.upper()} ({len(values)} values) ---")

    for value in values:
        if field == "size":
            if value in {"S", "M", "L"}:
                query = f"show me size {value}"
            elif value.isdigit():
                query = f"show me size {value}"
            else:
                query = f"show me size {value}"
        else:
            query = f"show me {value}"

        actual = extractor.extract(query)
        total += 1

        if actual.get(output_field) == value:
            passed += 1
            print(f"[PASS] {value}")
        else:
            failures.append((field, value, query, actual))
            print(f"[FAIL] {value} -> {actual}")

print("\n" + "=" * 72)
print(f"RESULT: {passed}/{total} passed")
print(f"FAILURES: {len(failures)}")

if failures:
    print("\nFAILURE DETAILS:")
    for item in failures:
        print(item)

print("=" * 72)

sys.exit(1 if failures else 0)
