"""Tests for pydantic models parsing real Kamino API response shapes."""

from kamino.models import (
    KvaultMetrics,
    MarketConfig,
    OraclePrice,
    ReserveMetrics,
    StakingYield,
    Vault,
)


def test_market_config_parses_real_shape() -> None:
    payload = {
        "name": "Main Market",
        "isPrimary": True,
        "description": "Primary market on mainnet",
        "lendingMarket": "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF",
        "lookupTable": "FGMSBiyVE8TvZcdQnZETAAKw28tkQJ2ccZy6pyp95URb",
        "isCurated": False,
    }
    market = MarketConfig.model_validate(payload)
    assert market.name == "Main Market"
    assert market.is_primary is True
    assert market.lending_market == "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF"
    assert market.is_curated is False


def test_market_config_allows_unknown_fields() -> None:
    payload = {
        "name": "Main Market",
        "lendingMarket": "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF",
        "somethingNew": "ignore me",
    }
    market = MarketConfig.model_validate(payload)
    assert market.name == "Main Market"
    # Unknown fields must not raise and remain accessible.
    assert market.model_extra is not None
    assert market.model_extra["somethingNew"] == "ignore me"


def test_reserve_metrics_keeps_decimals_as_strings() -> None:
    payload = {
        "reserve": "EGPE45iPkme8G8C1xFDNZoZeHdP3aRYtaAfAQuuwrcGZ",
        "liquidityToken": "EURC",
        "liquidityTokenMint": "HzwqbKZw8HxMN6bF2yFZNrht3c2iXXzpKcFu7uBEDKtr",
        "maxLtv": "0",
        "borrowApy": "0.040755456277808966",
        "supplyApy": "0.012736931925472206",
        "totalSupply": "572626.08840250675292",
        "totalBorrow": "331207.0453075084101040319913000775642331",
        "totalBorrowUsd": "379761.8027374324115953211198457940681039",
        "totalSupplyUsd": "656572.73511292208542",
    }
    metrics = ReserveMetrics.model_validate(payload)
    assert metrics.liquidity_token == "EURC"
    # High-precision decimals must survive as exact strings (no float rounding).
    assert metrics.total_borrow == "331207.0453075084101040319913000775642331"
    assert metrics.borrow_apy == "0.040755456277808966"


def test_oracle_price_parses_string_numerics() -> None:
    payload = {
        "mint": "HzwqbKZw8HxMN6bF2yFZNrht3c2iXXzpKcFu7uBEDKtr",
        "name": "EURC",
        "maxAgeInSeconds": "180",
        "price": "1.14657968",
        "timestamp": "1782074291",
    }
    price = OraclePrice.model_validate(payload)
    assert price.name == "EURC"
    assert price.price == "1.14657968"
    assert price.max_age_in_seconds == "180"


def test_staking_yield_parses() -> None:
    payload = {"apy": "0.0614289563253061952", "tokenMint": "mSoL..."}
    sy = StakingYield.model_validate(payload)
    assert sy.apy == "0.0614289563253061952"
    assert sy.token_mint == "mSoL..."


def test_kvault_metrics_parses_apys() -> None:
    payload = {
        "apy": "0.05",
        "apy24h": "0.04",
        "apy7d": "0.06",
        "tokenPrice": "1.0",
        "sharePrice": "1.01",
        "numberOfHolders": 42,
    }
    m = KvaultMetrics.model_validate(payload)
    assert m.apy == "0.05"
    assert m.apy_24h == "0.04"
    assert m.number_of_holders == 42


def test_vault_parses_address_and_state() -> None:
    payload = {
        "address": "VaultPubkey1111111111111111111111111111111",
        "programId": "ProgramId11111111111111111111111111111111",
        "state": {"tokenMint": "So11111111111111111111111111111111111111112"},
    }
    vault = Vault.model_validate(payload)
    assert vault.address == "VaultPubkey1111111111111111111111111111111"
    assert vault.state is not None
