import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.intent import IntentExtractor

records = [
    json.loads(line)
    for line in (ROOT / "competition" / "dev.jsonl").read_text(
        encoding="utf-8-sig"
    ).splitlines()
    if line.strip()
]

extractor = IntentExtractor()

errors = defaultdict(list)
category_pairs = Counter()
size_pairs = Counter()

for record in records:
    expected = record.get("filters") or {}
    predicted = extractor.extract(record.get("text", ""))

    for field in ("category", "colour", "size", "brand", "max_price"):
        exp = expected.get(field)
        got = predicted.get(field)

        exp_norm = str(exp).strip().lower() if exp is not None else None
        got_norm = str(got).strip().lower() if got is not None else None

        if exp_norm != got_norm:
            errors[field].append({
                "id": record.get("id"),
                "text": record.get("text"),
                "expected": exp,
                "predicted": got,
            })

            if field == "category":
                category_pairs[(str(exp), str(got))] += 1

            if field == "size":
                size_pairs[(str(exp), str(got))] += 1


print("=" * 72)
print("SHOPSENSE AI - ERROR PATTERN DIAGNOSTICS")
print("=" * 72)

print("\nCATEGORY ERROR SUMMARY")
for (expected, predicted), count in category_pairs.most_common():
    print(f"{expected:20} -> {predicted:20} : {count}")

print("\nCATEGORY ERROR EXAMPLES")
for item in errors["category"]:
    print(f"\n[{item['id']}] {item['text']}")
    print(f"Expected: {item['expected']} | Predicted: {item['predicted']}")

print("\nSIZE ERROR SUMMARY")
for (expected, predicted), count in size_pairs.most_common():
    print(f"{expected:12} -> {predicted:12} : {count}")

print("\nSIZE ERROR EXAMPLES")
for item in errors["size"]:
    print(f"\n[{item['id']}] {item['text']}")
    print(f"Expected: {item['expected']} | Predicted: {item['predicted']}")

print("\nOTHER FIELD ERROR COUNTS")
for field in ("colour", "brand", "max_price"):
    print(f"{field:12}: {len(errors[field])}")

print("\n" + "=" * 72)
print("DIAGNOSTICS COMPLETED")
print("=" * 72)
