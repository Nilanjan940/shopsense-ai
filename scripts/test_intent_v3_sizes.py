import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.intent_v3 import IntentExtractor

extractor = IntentExtractor()

tests = [
    # Existing V2 regression tests
    ("size M", "Show me size M", "M"),
    ("medium size", "I want medium size t-shirts", "M"),
    ("size L", "Find size L shirts", "L"),
    ("large size", "I need large size jackets", "L"),
    ("size S", "Show me size S", "S"),
    ("small size", "I need small size dresses", "S"),
    ("XL", "Show me XL hoodies", "XL"),
    ("XXL", "I want XXL jackets", "XXL"),
    ("medium price", "Show me medium-priced watches", None),
    ("large collection", "Show me a large collection of shirts", None),
    ("small budget", "I have a small budget for sneakers", None),
    ("medium fit", "I prefer medium fit", None),
    ("size correction", "Size 8, actually 7", "7"),
    ("letter correction", "Size L, no, make it M", "M"),
    ("contextual correction", "I need size M, make it L instead", "L"),
    ("implicit correction", "Make it M instead", "M"),

    # All 23 previously failed benchmark requests
    ("dev-0007", "Urbanyx olive green hooded sweatshirt small below one thousand five hundred", "S"),
    ("dev-0019", "I'm looking for grey tee from Pacevo, large", "L"),
    ("dev-0021", "can you find me navy trackpants within 2k, Zentrail brand, one more thing, large for office", "L"),
    ("dev-0040", "I need Pacevo navy tshirt medium, below eight hundred. no, change that to large", "L"),
    ("dev-0045", "hey, do you have any Urbanyx jacket small, in black, oh, and less than 4k", "S"),
    ("dev-0054", "hey, do you have any Zentrail black jacket within 3.7k large for office", "L"),
    ("dev-0070", "hi, I want Loomsy dress for under 2500 large, and in maroon for office", "L"),
    ("dev-0088", "looking for yellow Tanaro dress large", "L"),
    ("dev-0090", "looking for floaters size nine, in grey, no no, in black under eight hundred, by Kudova", "9"),
    ("dev-0127", "mujhe laal t shirt large aur haan, Loomsy ka dikhao na", "L"),
    ("dev-0143", "kya aapke paas black trackpants Zentrail ka M size nahi, small, 1700 se kam hai kya?", "S"),
    ("dev-0147", "do you have Northweft shirt large, up to eleven hundred in black", "L"),
    ("dev-0166", "I'm looking for Tanaro red dress small", "S"),
    ("dev-0167", "do you have white dress Mehrin brand, oh, and large for my dad", "L"),
    ("dev-0168", "show me Pacevo grey joggers medium, for under rs 2000", "M"),
    ("dev-0176", "I'd like hoodie only Pacevo, less than fifteen hundred, small in maroon", "S"),
    ("dev-0184", "hi, I want black jacket only Zentrail medium budget thirty seven hundred nothing too flashy", "M"),
    ("dev-0213", "Kesar Loom kurta under 2,600, in maroon, small thanks", "S"),
    ("dev-0225", "do you have blue kurta medium under 900 thank you", "M"),
    ("dev-0240", "can you find me navy blue medium Northweft casual shirt max 1,500 as a gift", "M"),
    ("dev-0267", "Pacevo grey t shirt medium for a wedding", "M"),
    ("dev-0278", "mere liye dress small, Mehrin wala, ek aur baat, in navy blue chahiye please", "S"),
    ("dev-0295", "I need grey Strydo trackpants medium within eleven hundred for the gym", "M"),

    # Additional false-positive safeguards
    ("large budget", "I have a large budget for watches", None),
    ("small collection", "Show me a small collection of jackets", None),
    ("medium-priced", "Find medium-priced headphones", None),
    ("small number", "Show me a small number of backpacks", None),
]

passed = 0
failed = []

print("=" * 110)
print("SHOPSENSE AI - V3 SIZE REGRESSION")
print("=" * 110)

for name, query, expected in tests:
    actual = extractor.extract(query).get("size")
    ok = actual == expected

    passed += int(ok)

    if not ok:
        failed.append((name, query, expected, actual))

    print(
        f"{'PASS' if ok else 'FAIL':<5} | "
        f"{name:<20} | "
        f"expected={str(expected):<5} "
        f"actual={str(actual):<5} | {query}"
    )

print("-" * 110)
print(f"RESULT: {passed}/{len(tests)} passed")

if failed:
    print("\nFAILURES:")
    for name, query, expected, actual in failed:
        print(f"{name}: expected={expected}, actual={actual}")
