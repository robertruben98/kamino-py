"""Pydantic models for Kamino Finance public API responses.

All models use ``extra="allow"`` so that new fields added by the API do not
break parsing. High-precision numeric values are returned by the API as JSON
strings (to preserve arbitrary precision) and are therefore modelled as ``str``
rather than ``float`` to avoid rounding.

Field names follow Python ``snake_case`` conventions and are mapped to the
API's ``camelCase`` keys via pydantic aliases. Models can be constructed using
either the alias or the Python attribute name (``populate_by_name=True``).
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class KaminoModel(BaseModel):
    """Base model shared by all Kamino response models.

    Configures pydantic to accept unknown fields (forward compatibility),
    populate fields by either alias or attribute name, and keep extra fields
    accessible via :attr:`~pydantic.BaseModel.model_extra`.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )


class MarketConfig(KaminoModel):
    """Configuration for a single Kamino lending market.

    Returned by ``GET /v2/kamino-market`` (as a list) and
    ``GET /v2/kamino-market/{pubkey}`` (single).

    Attributes:
        name: Human-readable market name (e.g. ``"Main Market"``).
        lending_market: Base58 public key of the lending market account.
        is_primary: Whether this is the protocol's primary market.
        description: Free-form description of the market.
        lookup_table: Base58 address of the market's address lookup table.
        is_curated: Whether the market is a curated (third-party) market.
    """

    name: Optional[str] = Field(default=None, description="Human-readable market name.")
    lending_market: Optional[str] = Field(
        default=None,
        alias="lendingMarket",
        description="Base58 public key of the lending market account.",
    )
    is_primary: Optional[bool] = Field(
        default=None, alias="isPrimary", description="Whether this is the primary market."
    )
    description: Optional[str] = Field(
        default=None, description="Free-form description of the market."
    )
    lookup_table: Optional[str] = Field(
        default=None,
        alias="lookupTable",
        description="Base58 address of the market's address lookup table.",
    )
    is_curated: Optional[bool] = Field(
        default=None,
        alias="isCurated",
        description="Whether the market is a curated third-party market.",
    )


class ReserveMetrics(KaminoModel):
    """Current metrics for a single reserve within a lending market.

    Returned by ``GET /kamino-market/{pubkey}/reserves/metrics`` (as a list).

    Numeric values are high-precision decimal strings as provided by the API.

    Attributes:
        reserve: Base58 public key of the reserve account.
        liquidity_token: Symbol of the reserve's liquidity token (e.g. ``"USDC"``).
        liquidity_token_mint: Base58 mint address of the liquidity token.
        max_ltv: Maximum loan-to-value ratio for the reserve, as a decimal string.
        borrow_apy: Current borrow APY, as a decimal string (e.g. ``"0.04075"``).
        supply_apy: Current supply APY, as a decimal string.
        total_supply: Total supplied amount in token units, as a decimal string.
        total_borrow: Total borrowed amount in token units, as a decimal string.
        total_supply_usd: Total supplied value in USD, as a decimal string.
        total_borrow_usd: Total borrowed value in USD, as a decimal string.
    """

    reserve: Optional[str] = Field(
        default=None, description="Base58 public key of the reserve account."
    )
    liquidity_token: Optional[str] = Field(
        default=None,
        alias="liquidityToken",
        description="Symbol of the reserve's liquidity token.",
    )
    liquidity_token_mint: Optional[str] = Field(
        default=None,
        alias="liquidityTokenMint",
        description="Base58 mint address of the liquidity token.",
    )
    max_ltv: Optional[str] = Field(
        default=None, alias="maxLtv", description="Maximum loan-to-value ratio (decimal string)."
    )
    borrow_apy: Optional[str] = Field(
        default=None, alias="borrowApy", description="Current borrow APY (decimal string)."
    )
    supply_apy: Optional[str] = Field(
        default=None, alias="supplyApy", description="Current supply APY (decimal string)."
    )
    total_supply: Optional[str] = Field(
        default=None,
        alias="totalSupply",
        description="Total supplied amount in token units (decimal string).",
    )
    total_borrow: Optional[str] = Field(
        default=None,
        alias="totalBorrow",
        description="Total borrowed amount in token units (decimal string).",
    )
    total_supply_usd: Optional[str] = Field(
        default=None,
        alias="totalSupplyUsd",
        description="Total supplied value in USD (decimal string).",
    )
    total_borrow_usd: Optional[str] = Field(
        default=None,
        alias="totalBorrowUsd",
        description="Total borrowed value in USD (decimal string).",
    )


class OraclePrice(KaminoModel):
    """A single oracle price entry.

    Returned by ``GET /oracles/prices`` (as a list when no ``markets`` filter
    is applied).

    Attributes:
        mint: Base58 mint address of the priced token.
        name: Token symbol (e.g. ``"EURC"``).
        price: Token price as a high-precision decimal string.
        max_age_in_seconds: Maximum acceptable staleness of the price, in seconds
            (string).
        timestamp: Unix timestamp of the price observation, as a string.
    """

    mint: Optional[str] = Field(
        default=None, description="Base58 mint address of the priced token."
    )
    name: Optional[str] = Field(default=None, description="Token symbol.")
    price: Optional[str] = Field(default=None, description="Token price (decimal string).")
    max_age_in_seconds: Optional[str] = Field(
        default=None,
        alias="maxAgeInSeconds",
        description="Maximum acceptable price staleness in seconds.",
    )
    timestamp: Optional[str] = Field(
        default=None, description="Unix timestamp of the price observation (string)."
    )


class StakingYield(KaminoModel):
    """Staking yield for a single token mint.

    Returned by ``GET /v2/staking-yields`` (as a list).

    Attributes:
        apy: Annualized staking yield, as a decimal string.
        token_mint: Base58 mint address of the staked token.
    """

    apy: Optional[str] = Field(
        default=None, description="Annualized staking yield (decimal string)."
    )
    token_mint: Optional[str] = Field(
        default=None, alias="tokenMint", description="Base58 mint address of the staked token."
    )


class KvaultMetrics(KaminoModel):
    """Current metrics for a Kamino liquidity vault (KVault).

    Returned by ``GET /kvaults/vaults/{pubkey}/metrics``.

    All APY and amount fields are high-precision decimal strings. Only the most
    commonly used fields are declared explicitly; any additional fields returned
    by the API remain available via :attr:`~pydantic.BaseModel.model_extra`.

    Attributes:
        apy: Annualized percentage yield (decimal string).
        apy_24h: Trailing 24-hour APY (decimal string).
        apy_7d: Trailing 7-day APY (decimal string).
        apy_30d: Trailing 30-day APY (decimal string).
        apy_90d: Trailing 90-day APY (decimal string).
        apy_365d: Trailing 365-day APY (decimal string).
        token_price: Underlying token price in USD (decimal string).
        share_price: Vault share price (decimal string).
        tokens_available: Idle tokens available in the vault (decimal string).
        tokens_invested: Tokens currently deployed in strategies (decimal string).
        number_of_holders: Number of distinct vault share holders.
    """

    apy: Optional[str] = Field(default=None, description="Annualized percentage yield.")
    apy_24h: Optional[str] = Field(
        default=None, alias="apy24h", description="Trailing 24-hour APY."
    )
    apy_7d: Optional[str] = Field(default=None, alias="apy7d", description="Trailing 7-day APY.")
    apy_30d: Optional[str] = Field(default=None, alias="apy30d", description="Trailing 30-day APY.")
    apy_90d: Optional[str] = Field(default=None, alias="apy90d", description="Trailing 90-day APY.")
    apy_365d: Optional[str] = Field(
        default=None, alias="apy365d", description="Trailing 365-day APY."
    )
    token_price: Optional[str] = Field(
        default=None, alias="tokenPrice", description="Underlying token price in USD."
    )
    share_price: Optional[str] = Field(
        default=None, alias="sharePrice", description="Vault share price."
    )
    tokens_available: Optional[str] = Field(
        default=None, alias="tokensAvailable", description="Idle tokens available in the vault."
    )
    tokens_invested: Optional[str] = Field(
        default=None,
        alias="tokensInvested",
        description="Tokens currently deployed in strategies.",
    )
    number_of_holders: Optional[int] = Field(
        default=None, alias="numberOfHolders", description="Number of distinct vault share holders."
    )


class Vault(KaminoModel):
    """A Kamino liquidity vault (KVault).

    Returned by ``GET /kvaults/vaults`` (as a list) and
    ``GET /kvaults/vaults/{pubkey}`` (single).

    Attributes:
        address: Base58 public key of the vault.
        program_id: Base58 program id that owns the vault.
        state: Raw on-chain vault state object as returned by the API. The exact
            shape is preserved as a dict to avoid coupling to internal layout.
    """

    address: Optional[str] = Field(default=None, description="Base58 public key of the vault.")
    program_id: Optional[str] = Field(
        default=None, alias="programId", description="Base58 program id that owns the vault."
    )
    state: Optional[dict[str, Any]] = Field(
        default=None, description="Raw on-chain vault state object."
    )


__all__ = [
    "KaminoModel",
    "KvaultMetrics",
    "MarketConfig",
    "OraclePrice",
    "ReserveMetrics",
    "StakingYield",
    "Vault",
]
