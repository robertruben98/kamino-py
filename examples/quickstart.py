"""Synchronous quickstart for kamino-py.

Run with::

    python examples/quickstart.py

Hits the live, keyless Kamino public API.
"""

from kamino import KaminoClient


def main() -> None:
    with KaminoClient() as client:
        markets = client.get_markets()
        print(f"Found {len(markets)} markets")

        primary = next((m for m in markets if m.is_primary), markets[0])
        print(f"Primary market: {primary.name} ({primary.lending_market})")

        reserves = client.get_reserve_metrics(primary.lending_market)
        print(f"\nTop reserves in {primary.name}:")
        for reserve in reserves[:5]:
            print(
                f"  {reserve.liquidity_token:>8}  "
                f"supply APY {reserve.supply_apy}  "
                f"borrow APY {reserve.borrow_apy}"
            )

        print("\nA few oracle prices:")
        for price in client.get_oracle_prices()[:5]:
            print(f"  {price.name:>8}  {price.price}")


if __name__ == "__main__":
    main()
