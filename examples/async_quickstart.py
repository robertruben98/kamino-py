"""Asynchronous quickstart for kamino-py.

Run with::

    python examples/async_quickstart.py

Hits the live, keyless Kamino public API.
"""

import asyncio

from kamino import AsyncKaminoClient


async def main() -> None:
    async with AsyncKaminoClient() as client:
        vaults = await client.get_vaults()
        print(f"Found {len(vaults)} KVaults")

        if vaults:
            first = vaults[0]
            metrics = await client.get_vault_metrics(first.address)
            print(f"Vault {first.address}")
            print(f"  APY (current): {metrics.apy}")
            print(f"  APY (30d):     {metrics.apy_30d}")
            print(f"  Holders:       {metrics.number_of_holders}")

        yields = await client.get_staking_yields()
        print(f"\nStaking yields for {len(yields)} tokens (first 5):")
        for sy in yields[:5]:
            print(f"  {sy.token_mint}  {sy.apy}")


if __name__ == "__main__":
    asyncio.run(main())
