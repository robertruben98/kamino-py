"""Unit tests for the synchronous KaminoClient, using respx to mock HTTP."""

from collections.abc import Iterator

import httpx
import pytest
import respx

from kamino import KaminoClient
from kamino.exceptions import KaminoAPIError
from kamino.models import (
    KvaultMetrics,
    MarketConfig,
    OraclePrice,
    ReserveMetrics,
    StakingYield,
    Vault,
)

BASE = "https://api.kamino.finance"


@pytest.fixture
def client() -> Iterator[KaminoClient]:
    with KaminoClient() as c:
        yield c


@respx.mock
def test_default_base_url() -> None:
    c = KaminoClient()
    assert str(c.base_url) == BASE
    c.close()


@respx.mock
def test_custom_base_url_strips_trailing_slash() -> None:
    c = KaminoClient(base_url="https://example.test/")
    assert str(c.base_url) == "https://example.test"
    c.close()


@respx.mock
def test_get_markets(client: KaminoClient) -> None:
    respx.get(f"{BASE}/v2/kamino-market").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "Main Market",
                    "isPrimary": True,
                    "lendingMarket": "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF",
                    "isCurated": False,
                }
            ],
        )
    )
    markets = client.get_markets()
    assert isinstance(markets, list)
    assert isinstance(markets[0], MarketConfig)
    assert markets[0].name == "Main Market"
    assert markets[0].lending_market == "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF"


@respx.mock
def test_get_market_by_pubkey(client: KaminoClient) -> None:
    pubkey = "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF"
    route = respx.get(f"{BASE}/v2/kamino-market/{pubkey}").mock(
        return_value=httpx.Response(200, json={"name": "Main Market", "lendingMarket": pubkey})
    )
    market = client.get_market(pubkey)
    assert route.called
    assert isinstance(market, MarketConfig)
    assert market.lending_market == pubkey


@respx.mock
def test_get_reserve_metrics(client: KaminoClient) -> None:
    pubkey = "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF"
    respx.get(f"{BASE}/kamino-market/{pubkey}/reserves/metrics").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "reserve": "EGPE45iPkme8G8C1xFDNZoZeHdP3aRYtaAfAQuuwrcGZ",
                    "liquidityToken": "EURC",
                    "borrowApy": "0.040755456277808966",
                    "totalBorrow": "331207.0453075084101040319913000775642331",
                }
            ],
        )
    )
    metrics = client.get_reserve_metrics(pubkey)
    assert isinstance(metrics[0], ReserveMetrics)
    assert metrics[0].liquidity_token == "EURC"
    # Precision preserved exactly.
    assert metrics[0].total_borrow == "331207.0453075084101040319913000775642331"


@respx.mock
def test_get_vaults(client: KaminoClient) -> None:
    respx.get(f"{BASE}/kvaults/vaults").mock(
        return_value=httpx.Response(
            200,
            json=[{"address": "Vault111", "programId": "Prog111", "state": {"tokenMint": "So111"}}],
        )
    )
    vaults = client.get_vaults()
    assert isinstance(vaults[0], Vault)
    assert vaults[0].address == "Vault111"


@respx.mock
def test_get_vault_by_pubkey(client: KaminoClient) -> None:
    respx.get(f"{BASE}/kvaults/vaults/Vault111").mock(
        return_value=httpx.Response(200, json={"address": "Vault111", "state": {}})
    )
    vault = client.get_vault("Vault111")
    assert isinstance(vault, Vault)
    assert vault.address == "Vault111"


@respx.mock
def test_get_vault_metrics(client: KaminoClient) -> None:
    respx.get(f"{BASE}/kvaults/vaults/Vault111/metrics").mock(
        return_value=httpx.Response(
            200, json={"apy": "0.05", "apy24h": "0.04", "numberOfHolders": 7}
        )
    )
    m = client.get_vault_metrics("Vault111")
    assert isinstance(m, KvaultMetrics)
    assert m.apy == "0.05"
    assert m.apy_24h == "0.04"
    assert m.number_of_holders == 7


@respx.mock
def test_get_oracle_prices(client: KaminoClient) -> None:
    respx.get(f"{BASE}/oracles/prices").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"mint": "Mint1", "name": "EURC", "price": "1.14657968", "timestamp": "1782074291"}
            ],
        )
    )
    prices = client.get_oracle_prices()
    assert isinstance(prices[0], OraclePrice)
    assert prices[0].name == "EURC"
    assert prices[0].price == "1.14657968"


@respx.mock
def test_get_staking_yields(client: KaminoClient) -> None:
    respx.get(f"{BASE}/v2/staking-yields").mock(
        return_value=httpx.Response(200, json=[{"apy": "0.061", "tokenMint": "mSoL"}])
    )
    yields = client.get_staking_yields()
    assert isinstance(yields[0], StakingYield)
    assert yields[0].token_mint == "mSoL"


@respx.mock
def test_http_error_raises_kamino_api_error(client: KaminoClient) -> None:
    respx.get(f"{BASE}/v2/kamino-market").mock(return_value=httpx.Response(500, text="boom"))
    with pytest.raises(KaminoAPIError) as exc_info:
        client.get_markets()
    assert exc_info.value.status_code == 500


@respx.mock
def test_get_markets_passes_program_id_query(client: KaminoClient) -> None:
    route = respx.get(f"{BASE}/v2/kamino-market", params={"programId": "Prog9"}).mock(
        return_value=httpx.Response(200, json=[])
    )
    client.get_markets(program_id="Prog9")
    assert route.called
