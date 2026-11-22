import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from shopsense.integrations.local_provider import LocalProductProvider
from shopsense.integrations.product_provider import ProductResult


def main():
    provider = LocalProductProvider()

    results = provider.search(
        "black running shoes",
        {"colour": "black", "size": "9"},
        10,
    )
    assert results, "Expected matching products"
    assert all(isinstance(item, ProductResult) for item in results)
    assert all(item.source == "local_catalogue" for item in results)
    assert all(item.colour.lower() == "black" for item in results)
    assert all(item.size == "9" for item in results)
    print("PASS: result structure and strict filters")

    limited = provider.search("shoes", limit=3)
    assert len(limited) <= 3
    print("PASS: result limit")

    empty = provider.search(
        "running shoes",
        {"colour": "black", "size": "INVALID_SIZE"},
        10,
    )
    assert empty == []
    print("PASS: empty-result handling")

    try:
        provider.search("shoes", limit=0)
    except ValueError:
        print("PASS: invalid limit rejection")
    else:
        raise AssertionError("Expected ValueError for limit=0")

    print("\nALL PROVIDER TESTS PASSED")


if __name__ == "__main__":
    main()
