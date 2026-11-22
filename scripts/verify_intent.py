import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from shopsense.engine.intent import IntentExtractor


extractor = IntentExtractor()

tests = [
    (
        "Loomsy navy blue casual sneakers within forty five hundred, size 7",
        {
            "brand": "Loomsy",
            "colour": "navy",
            "category": "sneakers",
            "size": "7",
            "max_price": 4500,
        },
    ),
    (
        "olive Urbanyx size 6 slides not more than seven hundred",
        {
            "brand": "Urbanyx",
            "colour": "olive",
            "category": "sandals",
            "size": "6",
            "max_price": 700,
        },
    ),
    (
        "maroon size M, oops, XS Tanaro kurta max 1500",
        {
            "colour": "maroon",
            "size": "XS",
            "brand": "Tanaro",
            "category": "kurtas",
            "max_price": 1500,
        },
    ),
    (
        "black size 9 floaters by Strydo less than 0.8k",
        {
            "colour": "black",
            "size": "9",
            "category": "sandals",
            "brand": "Strydo",
            "max_price": 800,
        },
    ),
    (
        "blue shirt Northweft size L",
        {
            "colour": "blue",
            "category": "shirts",
            "brand": "Northweft",
            "size": "L",
        },
    ),
    (
        "Sonquil headphones under 7,500",
        {
            "brand": "Sonquil",
            "category": "headphones",
            "max_price": 7500,
        },
    ),
    (
        "Urbanyx olive green hooded sweatshirt small below 1500",
        {
            "brand": "Urbanyx",
            "colour": "olive",
            "category": "hoodies",
            "size": "S",
            "max_price": 1500,
        },
    ),
    (
        "shirt budget 2,000, extra large, and in blue",
        {
            "category": "shirts",
            "size": "XL",
            "colour": "blue",
            "max_price": 2000,
        },
    ),
]

print("=" * 65)
print("SHOPSENSE AI - INTENT EXTRACTION TESTS")
print("=" * 65)

passed = 0

for index, (request, expected) in enumerate(tests, start=1):
    actual = extractor.extract(request)
    success = actual == expected

    print(f"\nTEST {index}: {'PASS' if success else 'FAIL'}")
    print("Request: ", request)
    print("Expected:", expected)
    print("Actual:  ", actual)

    if success:
        passed += 1

print("\n" + "=" * 65)
print(f"RESULT: {passed}/{len(tests)} tests passed")
print("=" * 65)

if passed != len(tests):
    raise SystemExit(1)
