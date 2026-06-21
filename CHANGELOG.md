# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-21

### Added

- Initial release.
- Synchronous `KaminoClient` and asynchronous `AsyncKaminoClient`.
- Read-only data methods covering Kamino lending markets, reserves, liquidity
  vaults (KVaults), oracle prices, and staking yields:
  - `get_markets`, `get_market`
  - `get_reserve_metrics`
  - `get_vaults`, `get_vault`, `get_vault_metrics`
  - `get_oracle_prices`
  - `get_staking_yields`
- Typed pydantic v2 models with `extra="allow"` for forward compatibility.
- `KaminoAPIError` for non-success HTTP responses.
- `py.typed` marker for full type-checker support.

[Unreleased]: https://github.com/robertruben98/kamino-py/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/robertruben98/kamino-py/releases/tag/v0.1.0
