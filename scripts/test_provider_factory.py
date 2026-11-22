import os
import sys

sys.path.insert(0, "backend")

from shopsense.integrations.provider_factory import get_product_provider
from shopsense.integrations.local_provider import LocalProductProvider

os.environ["SHOPSENSE_PRODUCT_PROVIDER"] = "rezolve"

provider = get_product_provider("local")
assert isinstance(provider, LocalProductProvider)
print("PASS: explicit provider overrides environment")

try:
    get_product_provider()
except RuntimeError as exc:
    assert "not configured" in str(exc)
    print("PASS: unavailable Rezolve provider rejected clearly")

try:
    get_product_provider("unknown")
except ValueError as exc:
    assert "Unsupported product provider" in str(exc)
    print("PASS: unknown provider rejected")

print("\nALL FACTORY TESTS PASSED")
