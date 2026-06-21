"""Synchronous and asynchronous clients for the Kamino Finance public API.

The clients wrap ``httpx`` and parse JSON responses into typed pydantic models.
Both clients expose the same read-only data methods and can be used as context
managers to ensure underlying HTTP connections are closed.

Example:
    >>> from kamino import KaminoClient
    >>> with KaminoClient() as client:
    ...     markets = client.get_markets()
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, Optional, TypeVar

import httpx
from pydantic import BaseModel

from kamino.exceptions import KaminoAPIError
from kamino.models import (
    KvaultMetrics,
    MarketConfig,
    OraclePrice,
    ReserveMetrics,
    StakingYield,
    Vault,
)

DEFAULT_BASE_URL = "https://api.kamino.finance"
DEFAULT_TIMEOUT = 30.0

M = TypeVar("M", bound=BaseModel)


def _parse_list(model: type[M], data: Any) -> list[M]:
    """Validate a JSON list payload into a list of ``model`` instances."""
    if not isinstance(data, list):
        raise KaminoAPIError(
            f"Expected a JSON array from the API but got {type(data).__name__}.",
        )
    return [model.model_validate(item) for item in data]


def _raise_for_status(response: httpx.Response) -> None:
    """Raise :class:`KaminoAPIError` if the response has an error status."""
    if response.is_success:
        return
    raise KaminoAPIError(
        f"Kamino API request to {response.request.url} failed with status {response.status_code}.",
        status_code=response.status_code,
        response_text=response.text,
    )


class KaminoClient:
    """Synchronous client for the Kamino Finance public API.

    Args:
        base_url: API base URL. Defaults to ``https://api.kamino.finance``. Any
            trailing slash is stripped.
        timeout: Request timeout in seconds. Defaults to ``30``.
        http_client: An optional pre-configured :class:`httpx.Client`. When
            provided, the caller is responsible for closing it; otherwise the
            client manages its own and closes it on :meth:`close`.

    The client is safe to use as a context manager::

        with KaminoClient() as client:
            markets = client.get_markets()
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)

    def __enter__(self) -> KaminoClient:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client if it is owned by this instance."""
        if self._owns_client:
            self._client.close()

    def _get(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        """Perform a GET request and return the decoded JSON body."""
        url = f"{self.base_url}{path}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        response = self._client.get(url, params=clean_params or None)
        _raise_for_status(response)
        return response.json()

    def get_markets(self, *, program_id: Optional[str] = None) -> list[MarketConfig]:
        """Get the configuration of all Kamino lending markets.

        Calls ``GET /v2/kamino-market``.

        Args:
            program_id: Optionally filter markets by KLend program id.

        Returns:
            A list of :class:`~kamino.models.MarketConfig`.
        """
        data = self._get("/v2/kamino-market", params={"programId": program_id})
        return _parse_list(MarketConfig, data)

    def get_market(self, pubkey: str, *, program_id: Optional[str] = None) -> MarketConfig:
        """Get the configuration of a single Kamino lending market.

        Calls ``GET /v2/kamino-market/{pubkey}``.

        Args:
            pubkey: Base58 public key of the lending market.
            program_id: Optionally specify the KLend program id.

        Returns:
            A :class:`~kamino.models.MarketConfig`.
        """
        data = self._get(f"/v2/kamino-market/{pubkey}", params={"programId": program_id})
        return MarketConfig.model_validate(data)

    def get_reserve_metrics(self, market_pubkey: str) -> list[ReserveMetrics]:
        """Get current metrics for all reserves in a lending market.

        Calls ``GET /kamino-market/{pubkey}/reserves/metrics``.

        Args:
            market_pubkey: Base58 public key of the lending market.

        Returns:
            A list of :class:`~kamino.models.ReserveMetrics`.
        """
        data = self._get(f"/kamino-market/{market_pubkey}/reserves/metrics")
        return _parse_list(ReserveMetrics, data)

    def get_vaults(self) -> list[Vault]:
        """Get all Kamino liquidity vaults (KVaults).

        Calls ``GET /kvaults/vaults``.

        Returns:
            A list of :class:`~kamino.models.Vault`.
        """
        data = self._get("/kvaults/vaults")
        return _parse_list(Vault, data)

    def get_vault(self, pubkey: str) -> Vault:
        """Get a single Kamino liquidity vault by its address.

        Calls ``GET /kvaults/vaults/{pubkey}``.

        Args:
            pubkey: Base58 public key of the vault.

        Returns:
            A :class:`~kamino.models.Vault`.
        """
        data = self._get(f"/kvaults/vaults/{pubkey}")
        return Vault.model_validate(data)

    def get_vault_metrics(self, pubkey: str) -> KvaultMetrics:
        """Get current metrics (APYs, balances, fees) for a vault.

        Calls ``GET /kvaults/vaults/{pubkey}/metrics``.

        Args:
            pubkey: Base58 public key of the vault.

        Returns:
            A :class:`~kamino.models.KvaultMetrics`.
        """
        data = self._get(f"/kvaults/vaults/{pubkey}/metrics")
        return KvaultMetrics.model_validate(data)

    def get_oracle_prices(self, *, markets: Optional[str] = None) -> list[OraclePrice]:
        """Get Kamino oracle prices.

        Calls ``GET /oracles/prices``.

        Args:
            markets: Optional comma-separated list of market pubkeys to scope
                the prices to.

        Returns:
            A list of :class:`~kamino.models.OraclePrice`.
        """
        data = self._get("/oracles/prices", params={"markets": markets})
        return _parse_list(OraclePrice, data)

    def get_staking_yields(self) -> list[StakingYield]:
        """Get staking yields for supported tokens.

        Calls ``GET /v2/staking-yields``.

        Returns:
            A list of :class:`~kamino.models.StakingYield`.
        """
        data = self._get("/v2/staking-yields")
        return _parse_list(StakingYield, data)


class AsyncKaminoClient:
    """Asynchronous client for the Kamino Finance public API.

    Mirrors :class:`KaminoClient` but exposes coroutine methods and wraps an
    :class:`httpx.AsyncClient`.

    Args:
        base_url: API base URL. Defaults to ``https://api.kamino.finance``. Any
            trailing slash is stripped.
        timeout: Request timeout in seconds. Defaults to ``30``.
        http_client: An optional pre-configured :class:`httpx.AsyncClient`. When
            provided, the caller is responsible for closing it.

    Use as an async context manager::

        async with AsyncKaminoClient() as client:
            markets = await client.get_markets()
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> AsyncKaminoClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client if owned by this instance."""
        if self._owns_client:
            await self._client.aclose()

    async def _get(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        """Perform a GET request and return the decoded JSON body."""
        url = f"{self.base_url}{path}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        response = await self._client.get(url, params=clean_params or None)
        _raise_for_status(response)
        return response.json()

    async def get_markets(self, *, program_id: Optional[str] = None) -> list[MarketConfig]:
        """Get the configuration of all Kamino lending markets.

        Calls ``GET /v2/kamino-market``. See :meth:`KaminoClient.get_markets`.
        """
        data = await self._get("/v2/kamino-market", params={"programId": program_id})
        return _parse_list(MarketConfig, data)

    async def get_market(self, pubkey: str, *, program_id: Optional[str] = None) -> MarketConfig:
        """Get a single lending market config.

        Calls ``GET /v2/kamino-market/{pubkey}``. See
        :meth:`KaminoClient.get_market`.
        """
        data = await self._get(f"/v2/kamino-market/{pubkey}", params={"programId": program_id})
        return MarketConfig.model_validate(data)

    async def get_reserve_metrics(self, market_pubkey: str) -> list[ReserveMetrics]:
        """Get current metrics for all reserves in a lending market.

        Calls ``GET /kamino-market/{pubkey}/reserves/metrics``. See
        :meth:`KaminoClient.get_reserve_metrics`.
        """
        data = await self._get(f"/kamino-market/{market_pubkey}/reserves/metrics")
        return _parse_list(ReserveMetrics, data)

    async def get_vaults(self) -> list[Vault]:
        """Get all Kamino liquidity vaults (KVaults).

        Calls ``GET /kvaults/vaults``. See :meth:`KaminoClient.get_vaults`.
        """
        data = await self._get("/kvaults/vaults")
        return _parse_list(Vault, data)

    async def get_vault(self, pubkey: str) -> Vault:
        """Get a single Kamino liquidity vault by address.

        Calls ``GET /kvaults/vaults/{pubkey}``. See
        :meth:`KaminoClient.get_vault`.
        """
        data = await self._get(f"/kvaults/vaults/{pubkey}")
        return Vault.model_validate(data)

    async def get_vault_metrics(self, pubkey: str) -> KvaultMetrics:
        """Get current metrics for a vault.

        Calls ``GET /kvaults/vaults/{pubkey}/metrics``. See
        :meth:`KaminoClient.get_vault_metrics`.
        """
        data = await self._get(f"/kvaults/vaults/{pubkey}/metrics")
        return KvaultMetrics.model_validate(data)

    async def get_oracle_prices(self, *, markets: Optional[str] = None) -> list[OraclePrice]:
        """Get Kamino oracle prices.

        Calls ``GET /oracles/prices``. See
        :meth:`KaminoClient.get_oracle_prices`.
        """
        data = await self._get("/oracles/prices", params={"markets": markets})
        return _parse_list(OraclePrice, data)

    async def get_staking_yields(self) -> list[StakingYield]:
        """Get staking yields for supported tokens.

        Calls ``GET /v2/staking-yields``. See
        :meth:`KaminoClient.get_staking_yields`.
        """
        data = await self._get("/v2/staking-yields")
        return _parse_list(StakingYield, data)


__all__ = ["AsyncKaminoClient", "KaminoClient"]
