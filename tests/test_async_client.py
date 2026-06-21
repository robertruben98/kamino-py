"""Unit tests for the asynchronous AsyncKaminoClient, using respx to mock HTTP."""

import httpx
import pytest
import respx

from kamino import AsyncKaminoClient
from kamino.exceptions import KaminoAPIError
from kamino.models import MarketConfig, OraclePrice

BASE = "https://api.kamino.finance"


@respx.mock
async def test_async_get_markets() -> None:
    respx.get(f"{BASE}/v2/kamino-market").mock(
        return_value=httpx.Response(200, json=[{"name": "Main Market", "lendingMarket": "abc"}])
    )
    async with AsyncKaminoClient() as client:
        markets = await client.get_markets()
    assert isinstance(markets[0], MarketConfig)
    assert markets[0].name == "Main Market"


@respx.mock
async def test_async_get_oracle_prices() -> None:
    respx.get(f"{BASE}/oracles/prices").mock(
        return_value=httpx.Response(200, json=[{"mint": "m", "name": "SOL", "price": "150.5"}])
    )
    async with AsyncKaminoClient() as client:
        prices = await client.get_oracle_prices()
    assert isinstance(prices[0], OraclePrice)
    assert prices[0].price == "150.5"


@respx.mock
async def test_async_http_error_raises() -> None:
    respx.get(f"{BASE}/v2/kamino-market").mock(return_value=httpx.Response(404, text="nope"))
    async with AsyncKaminoClient() as client:
        with pytest.raises(KaminoAPIError) as exc_info:
            await client.get_markets()
    assert exc_info.value.status_code == 404
