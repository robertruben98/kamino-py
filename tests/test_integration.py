"""Live integration test against the real Kamino API.

This test hits the public, keyless ``GET /v2/kamino-market`` endpoint and is
marked ``integration`` so it is deselected by default (see ``addopts`` in
``pyproject.toml``). Run it explicitly with::

    pytest -m integration
"""

import pytest

from kamino import KaminoClient
from kamino.models import MarketConfig


@pytest.mark.integration
def test_live_get_markets_returns_primary_market() -> None:
    """The live API should return at least one market, including the primary one."""
    with KaminoClient() as client:
        markets = client.get_markets()

    assert len(markets) > 0
    assert all(isinstance(m, MarketConfig) for m in markets)
    # The protocol always exposes a primary market with a lending market pubkey.
    primary = [m for m in markets if m.is_primary]
    assert primary, "expected at least one primary market"
    assert primary[0].lending_market
