"""kamino-py: a typed Python client for the Kamino Finance public API.

Provides synchronous (:class:`KaminoClient`) and asynchronous
(:class:`AsyncKaminoClient`) clients for read-only access to Kamino Finance
data on Solana: lending markets, reserves, liquidity vaults, oracle prices,
and staking yields.
"""

from kamino.client import AsyncKaminoClient, KaminoClient
from kamino.exceptions import KaminoAPIError, KaminoError
from kamino.models import (
    KaminoModel,
    KvaultMetrics,
    MarketConfig,
    OraclePrice,
    ReserveMetrics,
    StakingYield,
    Vault,
)

__version__ = "0.1.0"

__all__ = [
    "AsyncKaminoClient",
    "KaminoClient",
    "KaminoAPIError",
    "KaminoError",
    "KaminoModel",
    "KvaultMetrics",
    "MarketConfig",
    "OraclePrice",
    "ReserveMetrics",
    "StakingYield",
    "Vault",
    "__version__",
]
