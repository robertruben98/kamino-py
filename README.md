# kamino-py

[![CI](https://github.com/robertruben98/kamino-py/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/kamino-py/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/kamino-py.svg)](https://pypi.org/project/kamino-py/)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://robertruben98.github.io/kamino-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/kamino-py.svg)](https://pypi.org/project/kamino-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Types: py.typed](https://img.shields.io/badge/types-py.typed-blue.svg)](https://peps.python.org/pep-0561/)

A small, typed Python client for the [Kamino Finance](https://kamino.finance) public API — read-only
access to Solana DeFi data: lending markets, reserves, liquidity vaults (KVaults), oracle prices,
and staking yields.

- Synchronous (`KaminoClient`) and asynchronous (`AsyncKaminoClient`) clients, built on `httpx`.
- Typed [pydantic v2](https://docs.pydantic.dev/) models with `extra="allow"`, so new API fields
  never break your code.
- High-precision numeric values are preserved as exact strings (no float rounding).
- Ships with `py.typed`; works on Python 3.9–3.13.
- No API key required for the endpoints covered here.

> **Scope:** This is a v1 **read-only data layer**. It does not build or sign transactions.

## Installation

```bash
pip install kamino-py
```

The import name is `kamino`:

```python
from kamino import KaminoClient
```

## Quickstart

```python
from kamino import KaminoClient

with KaminoClient() as client:
    # All Kamino lending markets
    markets = client.get_markets()
    primary = next(m for m in markets if m.is_primary)
    print(primary.name, primary.lending_market)

    # Reserve metrics (APYs, supply/borrow) for the primary market
    for reserve in client.get_reserve_metrics(primary.lending_market):
        print(f"{reserve.liquidity_token}: supply {reserve.supply_apy}  borrow {reserve.borrow_apy}")

    # Oracle prices
    for price in client.get_oracle_prices()[:5]:
        print(price.name, price.price)
```

### Async

```python
import asyncio
from kamino import AsyncKaminoClient


async def main():
    async with AsyncKaminoClient() as client:
        vaults = await client.get_vaults()
        print(f"{len(vaults)} vaults")
        if vaults:
            metrics = await client.get_vault_metrics(vaults[0].address)
            print("APY (30d):", metrics.apy_30d)


asyncio.run(main())
```

## Covered endpoints

All endpoints were **discovered from the live Kamino API** (the OpenAPI spec at
`https://api.kamino.finance/openapi/json`) and validated against live responses. The base URL is
`https://api.kamino.finance` (configurable via `KaminoClient(base_url=...)`).

| Client method | HTTP endpoint | Returns |
|---|---|---|
| `get_markets(program_id=None)` | `GET /v2/kamino-market` | `list[MarketConfig]` |
| `get_market(pubkey, program_id=None)` | `GET /v2/kamino-market/{pubkey}` | `MarketConfig` |
| `get_reserve_metrics(market_pubkey)` | `GET /kamino-market/{pubkey}/reserves/metrics` | `list[ReserveMetrics]` |
| `get_vaults()` | `GET /kvaults/vaults` | `list[Vault]` |
| `get_vault(pubkey)` | `GET /kvaults/vaults/{pubkey}` | `Vault` |
| `get_vault_metrics(pubkey)` | `GET /kvaults/vaults/{pubkey}/metrics` | `KvaultMetrics` |
| `get_oracle_prices(markets="main")` | `GET /oracles/prices` | `list[OraclePrice]` |
| `get_staking_yields()` | `GET /v2/staking-yields` | `list[StakingYield]` |

`get_oracle_prices` accepts a `markets` argument that the API defines as an enum: `"main"` (the
default — assets in the main market) or `"all"` (assets across every public KLend market). Other
values are rejected by the API with HTTP 400.

The full public API exposes many more endpoints (user positions, rewards, historical metrics,
transaction building, etc.); see the [official API reference](https://docs.kamino.finance).
This v1 client deliberately covers the core read-only data surface.

## Numeric values

The Kamino API returns monetary and rate values as JSON **strings** to preserve arbitrary
precision (e.g. `"331207.0453075084101040319913000775642331"`). This client keeps them as `str`
to avoid float rounding. Convert when you need arithmetic:

```python
from decimal import Decimal

reserve = client.get_reserve_metrics(primary.lending_market)[0]
borrow_apy = Decimal(reserve.borrow_apy)
```

## Error handling

Non-success HTTP responses raise `KaminoAPIError` with `.status_code` and `.response_text`:

```python
from kamino import KaminoClient, KaminoAPIError

try:
    with KaminoClient() as client:
        client.get_market("not-a-real-pubkey")
except KaminoAPIError as e:
    print(e.status_code, e)
```

## Configuration

```python
KaminoClient(
    base_url="https://api.kamino.finance",  # override for a proxy/staging host
    timeout=30.0,                            # request timeout in seconds
    http_client=my_httpx_client,             # bring your own httpx.Client
)
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
mypy
pytest                 # unit tests (live integration tests deselected)
pytest -m integration  # run the live integration test against the real API
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
