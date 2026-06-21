# Contributing to kamino-py

Thanks for your interest in improving `kamino-py`!

## Development setup

```bash
git clone https://github.com/robertruben98/kamino-py.git
cd kamino-py
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quality gate

All of these must pass before a PR is merged (they also run in CI across
Python 3.9–3.13):

```bash
ruff check .       # lint
ruff format .      # format
mypy               # strict type checking
pytest             # unit tests (live integration tests are deselected)
```

To run the single live integration test against the real Kamino API:

```bash
pytest -m integration
```

## Conventions

- **Python 3.9 compatibility is required.** CI runs on 3.9, so avoid runtime
  PEP 604 unions (`X | None`) in pydantic field types and other runtime
  annotations; use `typing.Optional` / `typing.Union`. Bare `list[...]` /
  `dict[...]` are fine under `from __future__ import annotations`.
- New endpoints should be modelled with `extra="allow"` so unknown fields do
  not break parsing, and high-precision numeric values should stay as `str`.
- Follow TDD: add a failing `respx`-mocked test first, then the implementation.
- All public methods and models get Google-style docstrings and
  `Field(description=...)`.

## Reporting issues

Please open an issue at
<https://github.com/robertruben98/kamino-py/issues>.
