from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProductResult:
    """Normalized product returned by any discovery provider."""

    product_id: Optional[str]
    title: str
    brand: Optional[str] = None
    category: Optional[str] = None
    colour: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    description: Optional[str] = None
    source: str = "unknown"
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProductProvider(ABC):
    """Common contract for local and external product discovery."""

    @abstractmethod
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[ProductResult]:
        """Return normalized product results."""
        raise NotImplementedError


class ProviderUnavailableError(RuntimeError):
    """Raised when a product discovery provider cannot be used."""
