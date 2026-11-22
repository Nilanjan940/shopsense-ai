import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "competition"

CATALOGUE = DATA_DIR / "catalogue.csv"
DEV_DATA = DATA_DIR / "dev.jsonl"


def load_catalogue():
    with CATALOGUE.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_dev_data():
    with DEV_DATA.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def show_counter(title, values):
    print(f"\n{title} ({len(values)} unique values)")
    print("-" * 55)
    for value, count in sorted(values.items()):
        print(f"{str(value):25} {count:>6}")


def main():
    products = load_catalogue()
    requests = load_dev_data()

    print("=" * 65)
    print("             SHOPSENSE AI - DATASET ANALYSIS")
    print("=" * 65)

    print("\nDATASET SUMMARY")
    print("-" * 55)
    print("Catalogue rows:", len(products))
    print("Development requests:", len(requests))
    print("Catalogue columns:", list(products[0].keys()))

    product_ids = {p["product_id"] for p in products}
    styles = {
        (
            p["title"], p["brand"], p["category"],
            p["colour"], p["price"]
        )
        for p in products
    }

    print("Unique product IDs:", len(product_ids))
    print("Distinct product styles (excluding size):", len(styles))

    # Catalogue vocabulary
    for field in ("category", "brand", "colour", "size"):
        counts = Counter(p[field].strip() for p in products)
        show_counter(f"CATALOGUE: {field.upper()}", counts)

    prices = [int(p["price"]) for p in products]

    print("\nPRICE STATISTICS")
    print("-" * 55)
    print("Minimum:", min(prices))
    print("Maximum:", max(prices))
    print("Average:", round(sum(prices) / len(prices), 2))

    # Development data
    print("\nDEVELOPMENT DATASET")
    print("-" * 55)

    tag_counts = Counter(
        tag for request in requests
        for tag in request.get("tags", [])
    )
    show_counter("REQUEST TAGS", tag_counts)

    print("\nFILTER FREQUENCY")
    print("-" * 55)

    filter_counts = Counter()
    null_counts = Counter()

    for request in requests:
        for key, value in request.get("filters", {}).items():
            if value is None:
                null_counts[key] += 1
            else:
                filter_counts[key] += 1

    show_counter("NON-NULL FILTERS", filter_counts)
    show_counter("NULL FILTERS", null_counts)

    # Edge cases
    print("\nCORRECTION EXAMPLES")
    print("-" * 55)

    corrections = [
        r for r in requests if "correction" in r.get("tags", [])
    ]

    for request in corrections[:10]:
        print(f"{request['id']}: {request['text']}")

    print("\nLATE-CONSTRAINT EXAMPLES")
    print("-" * 55)

    late = [
        r for r in requests if "late_constraint" in r.get("tags", [])
    ]

    for request in late[:10]:
        print(f"{request['id']}: {request['text']}")

    print("\nSAMPLE PRODUCTS")
    print("-" * 55)

    for product in products[:5]:
        print(
            product["product_id"],
            "|", product["title"],
            "|", product["brand"],
            "|", product["category"],
            "|", product["colour"],
            "| Size:", product["size"],
            "| Price:", product["price"]
        )

    print("\nANALYSIS COMPLETE")


if __name__ == "__main__":
    main()
