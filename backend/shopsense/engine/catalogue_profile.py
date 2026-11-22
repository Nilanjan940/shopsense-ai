import csv
from pathlib import Path
from typing import Dict, List, Optional, Set


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOGUE_PATH = PROJECT_ROOT / "competition" / "catalogue.csv"

REQUIRED_FIELDS = {
    "product_id", "title", "brand", "category",
    "colour", "size", "price", "description"
}


class CatalogueProfile:

    def __init__(self, catalogue_path: Optional[Path] = None):
        self.catalogue_path = Path(
            catalogue_path or CATALOGUE_PATH
        )
        self.products: List[Dict[str, str]] = []
        self.vocabulary: Dict[str, Set[str]] = {}
        self._load()

    def _load(self) -> None:
        if not self.catalogue_path.exists():
            raise FileNotFoundError(
                "Catalogue not found: {}".format(
                    self.catalogue_path
                )
            )

        with self.catalogue_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            actual_fields = set(reader.fieldnames or [])
            missing_fields = REQUIRED_FIELDS - actual_fields

            if missing_fields:
                raise ValueError(
                    "Missing catalogue columns: {}".format(
                        sorted(missing_fields)
                    )
                )

            for row in reader:
                product = {
                    key: (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }

                try:
                    int(product["price"])
                except (ValueError, KeyError):
                    raise ValueError(
                        "Invalid price for product {}".format(
                            product.get("product_id", "UNKNOWN")
                        )
                    )

                self.products.append(product)

        if not self.products:
            raise ValueError("Catalogue contains no products.")

        for field in ("brand", "category", "colour", "size"):
            self.vocabulary[field] = {
                product[field]
                for product in self.products
                if product[field]
            }

    def get_values(self, field: str) -> List[str]:
        if field not in self.vocabulary:
            raise ValueError(
                "Unsupported vocabulary field: {}".format(field)
            )

        return sorted(
            self.vocabulary[field],
            key=str.casefold
        )

    def is_valid(self, field: str, value: Optional[str]) -> bool:
        if value is None:
            return True

        if field not in self.vocabulary:
            return False

        return value.strip().casefold() in {
            item.casefold()
            for item in self.vocabulary[field]
        }

    def get_statistics(self) -> Dict[str, int]:
        return {
            "total_rows": len(self.products),
            "unique_product_ids": len({
                p["product_id"] for p in self.products
            }),
            "unique_brands": len(self.vocabulary["brand"]),
            "unique_categories": len(self.vocabulary["category"]),
            "unique_colours": len(self.vocabulary["colour"]),
            "unique_sizes": len(self.vocabulary["size"]),
            "products_without_size": sum(
                1 for p in self.products if not p["size"]
            ),
        }

    def validate_filters(
        self,
        filters: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:

        allowed_fields = {
            "brand", "category", "colour", "size"
        }

        unknown = set(filters) - allowed_fields

        if unknown:
            raise ValueError(
                "Unsupported categorical filters: {}".format(
                    sorted(unknown)
                )
            )

        return {
            field: value
            for field, value in filters.items()
            if self.is_valid(field, value)
        }
