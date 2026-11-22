import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.engine.catalogue_profile import CatalogueProfile


def main():
    profile = CatalogueProfile()

    print("=" * 55)
    print("SHOPSENSE AI - CATALOGUE PROFILE")
    print("=" * 55)

    print("\nSTATISTICS")
    for key, value in profile.get_statistics().items():
        print("{}: {}".format(key, value))

    print("\nCATALOGUE VOCABULARY")

    for field in ("brand", "category", "colour", "size"):
        values = profile.get_values(field)
        print("\n{} ({} values)".format(field.upper(), len(values)))
        print(", ".join(values))

    print("\nFILTER VALIDATION TESTS")

    valid_filters = {
        "brand": "Pacevo",
        "category": "running shoes",
        "colour": "black",
        "size": "9",
    }

    print("Valid filters:", profile.validate_filters(valid_filters))

    invalid_filters = {
        "brand": "UnknownBrand",
        "category": "running shoes",
        "colour": "black",
        "size": "9",
    }

    print(
        "Invalid brand removed:",
        profile.validate_filters(invalid_filters)
    )

    print("\nTESTS COMPLETED")


if __name__ == "__main__":
    main()
