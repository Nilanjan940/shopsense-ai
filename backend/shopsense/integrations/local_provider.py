import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND.parent
COMPETITION_DIR = PROJECT_ROOT / "competition"

if str(COMPETITION_DIR) not in sys.path:
    sys.path.insert(0, str(COMPETITION_DIR))

from search import search as catalogue_search

from shopsense.integrations.product_provider import (
    ProductProvider,
    ProductResult,
)


class LocalProductProvider(ProductProvider):
    """Product discovery using ShopSenseAI's local catalogue."""

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[ProductResult]:

        if limit < 1:
            raise ValueError("limit must be at least 1")

        results = catalogue_search(
            query=query,
            filters=filters or {},
            k=limit,
        )

        return [
            ProductResult(
                product_id=item["product_id"],
                title=item["title"],
                brand=item.get("brand"),
                category=item.get("category"),
                colour=item.get("colour"),
                size=item.get("size"),
                price=float(item["price"]),
                description=item.get("description"),
                source="local_catalogue",
                relevance_score=float(item.get("score", 0)),
            )
            for item in results
        ]
