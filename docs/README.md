# Omniverse Performance documentation (Sphinx source)

This folder is the **source** for the built HTML documentation. The content you edit lives here.

## What lives where

| Location | Purpose |
|----------|---------|
| **`docs/`** (this folder) | Sphinx project and **all documentation source**: `.md` files, `conf.py`, `_static/`, and so on. This is the single source of truth for the docs. |
| **`docs/about/`**, **`docs/get-started/`**, **`docs/workflows/`**, **`docs/reference/`**, **`docs/skill-tree/`** | The markdown (`.md`) files that become the built site. Edit these to change the documentation. |
| **`docs/_build/html/`** | Generated when you build. **Not in git** (refer to `.gitignore`). CI or a publish step should build and deploy from source. |

## Summary

- `docs/` holds the documentation **source only** — built HTML is generated locally or by CI and is not committed.
- The `.md` files live in `docs/` and its subfolders.

## Build

### Prerequisites

- Python 3.10–3.12
- [`uv`](https://docs.astral.sh/uv/) (installer: `curl -LsSf https://astral.sh/uv/install.sh | sh` on Linux/macOS, `irm https://astral.sh/uv/install.ps1 | iex` on Windows)

### With `uv`

```bash
uv run --directory docs --group docs sphinx-build -b html . _build/html
# Output: docs/_build/html/index.html (do not commit _build/)
```

Or use the Makefile:

```bash
cd docs
make docs-html      # build once
make docs-live      # live-reload server on http://localhost:8000
make docs-clean     # remove _build/
make docs-linkcheck # external-link check
```

### Dependencies

The docs dependencies are declared once, in [`pyproject.toml`](pyproject.toml) (the
`docs` dependency group), and pinned for reproducible builds in [`uv.lock`](uv.lock).
`uv sync --group docs` installs exactly those versions — CI does the same.

If you must use plain `pip` instead of `uv`, export the pinned set first:

```bash
uv export --only-group docs --no-hashes > requirements.txt
pip install -r requirements.txt
```
