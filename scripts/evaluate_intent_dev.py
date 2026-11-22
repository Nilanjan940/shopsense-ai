import json
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from shopsense.engine.intent import IntentExtractor

DEV_PATH = PROJECT_ROOT / "competition" / "dev.jsonl"
FIELDS = ("brand", "category", "colour", "size", "max_price")


def load_requests():
    if not DEV_PATH.exists():
        raise FileNotFoundError(f"Development data not found: {DEV_PATH}")

    records = []

    with DEV_PATH.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                )

    return records


def normalise_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().lower()

    return value


def main():
    extractor = IntentExtractor()
    records = load_requests()

    field_stats = {
        field: {"correct": 0, "total": 0, "false_positive": 0}
        for field in FIELDS
    }

    exact_matches = 0
    mismatches = []

    for record in records:
        request = record.get("text", "")
        expected = record.get("filters") or {}
        predicted = extractor.extract(request)

        request_correct = True

        for field in FIELDS:
            expected_value = expected.get(field)
            predicted_value = predicted.get(field)

            expected_norm = normalise_value(expected_value)
            predicted_norm = normalise_value(predicted_value)

            if expected_norm is not None:
                field_stats[field]["total"] += 1

                if expected_norm == predicted_norm:
                    field_stats[field]["correct"] += 1
                else:
                    request_correct = False

            elif predicted_norm is not None:
                field_stats[field]["false_positive"] += 1
                request_correct = False

        if request_correct:
            exact_matches += 1
        else:
            mismatches.append({
                "id": record.get("id"),
                "text": request,
                "expected": expected,
                "predicted": predicted,
            })

    print("=" * 72)
    print("SHOPSENSE AI - FULL DEVELOPMENT INTENT EVALUATION")
    print("=" * 72)

    print(f"\nTotal requests: {len(records)}")
    print("\nFIELD-LEVEL ACCURACY")

    for field in FIELDS:
        stats = field_stats[field]
        total = stats["total"]
        correct = stats["correct"]
        false_positive = stats["false_positive"]

        accuracy = (correct / total * 100) if total else 0

        print(
            f"{field:12} "
            f"correct={correct:3}/{total:<3} "
            f"accuracy={accuracy:6.2f}% "
            f"false_positives={false_positive}"
        )

    exact_accuracy = (
        exact_matches / len(records) * 100
        if records else 0
    )

    print("\nCOMPLETE FILTER MATCH")
    print(f"Exact matches: {exact_matches}/{len(records)}")
    print(f"Exact-match accuracy: {exact_accuracy:.2f}%")
    print(f"Requests with mismatches: {len(mismatches)}")

    print("\nFIRST 20 MISMATCHES")

    for item in mismatches[:20]:
        print("\n" + "-" * 72)
        print(f"ID: {item['id']}")
        print(f"Text: {item['text']}")
        print(f"Expected: {item['expected']}")
        print(f"Predicted: {item['predicted']}")

    print("\n" + "=" * 72)
    print("DEVELOPMENT EVALUATION COMPLETED")
    print("=" * 72)


if __name__ == "__main__":
    main()
