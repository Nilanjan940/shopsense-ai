import json
import sys
from pathlib import Path

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

for field in ("colour", "max_price"):
    errors = []

    for record in records:
        expected = (record.get("filters") or {}).get(field)
        predicted = extractor.extract(record.get("text", "")).get(field)

        if expected != predicted:
            errors.append((record, expected, predicted))

    print("\n" + "=" * 80)
    print(f"{field.upper()} ERRORS: {len(errors)}")
    print("=" * 80)

    for record, expected, predicted in errors:
        print(f"\n[{record.get('id')}]")
        print(f"Request:   {record.get('text')}")
        print(f"Expected:  {expected}")
        print(f"Predicted: {predicted}")

print("\nINSPECTION COMPLETED")
