# Product Discovery Provider Architecture

## Overview

ShopSenseAI uses a provider-based architecture to separate product
discovery from intent extraction and recommendation logic.

## Components

- `product_provider.py`: Defines the normalized ProductResult model,
  ProductProvider interface, and provider availability exception.
- `local_provider.py`: Adapts the existing competition catalogue search
  to the normalized provider interface.
- `provider_factory.py`: Selects a provider using an explicit argument
  or the SHOPSENSE_PRODUCT_PROVIDER environment variable.

## Current provider

The local provider is implemented and tested against the competition
catalogue. It supports the existing categorical and price filters.

## Rezolve Labs integration status

The Rezolve provider is not implemented. API access and the official
integration contract are currently unavailable.

The factory deliberately rejects `rezolve` selection instead of
pretending that a live external connection exists.

## Competition benchmark isolation

The verified competition agent continues to use the evaluator-injected
tools.search() interface directly.

The provider architecture is separate and does not change the verified
competition benchmark path.

## Validation

- Product provider interface import test: passed.
- Local strict-filter test: passed.
- Provider result structure and limit tests: passed.
- Empty-result handling: passed.
- Invalid-limit handling: passed.
- Provider selection and error-handling tests: passed.

## Future work

1. Obtain Rezolve Labs API access.
2. Verify the official authentication and Product Discovery API schemas.
3. Implement a RezolveProductProvider.
4. Normalize external responses into ProductResult.
5. Add timeout, retry, error handling, and local fallback.
6. Test the integration with real API responses.
