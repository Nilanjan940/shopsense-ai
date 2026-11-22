import os

from shopsense.integrations.local_provider import LocalProductProvider
from shopsense.integrations.product_provider import ProductProvider


def get_product_provider(
    provider_name=None,
) -> ProductProvider:
    """Return the configured product provider."""

    name = (
        provider_name
        or os.getenv("SHOPSENSE_PRODUCT_PROVIDER")
        or "local"
    ).strip().lower()

    if name == "local":
        return LocalProductProvider()

    if name == "rezolve":
        raise RuntimeError(
            "Rezolve provider is not configured. "
            "API access and the official integration contract are required."
        )

    raise ValueError(
        "Unsupported product provider: {}".format(name)
    )
