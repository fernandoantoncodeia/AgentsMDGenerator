## Why

We are dropping the checkout-less (PyPI/pipx) distribution in favor of editable local installs (`pip install -e <checkout>`). With a checkout always present, the read-only bundled `curated/` snapshot is never consulted: the server launches via `bin/agentsmd-serve` and resolves the live `prompt-catalogue/`. The snapshot is also inert under editable installs (the build-time asset copy does not run) and risks silently drifting from the live catalogue. Remove it to simplify catalogue-root resolution and packaging.

## What Changes

- Remove the bundled read-only `curated/` snapshot from the package (drop the `force-include` of `prompt-catalogue/curated`).
- Remove the bundled-snapshot fallback from catalogue-root resolution; precedence becomes `--catalogue-root` > `AGENTSMD_CATALOGUE_ROOT` > `prompt-catalogue/` in CWD.
- Remove the read-only refusal path (`catalogue_is_read_only`, `_require_writable`); a resolved root is always a real, writable directory.
- Remove the read-only startup notice in the server.

## Capabilities

### Modified Capabilities
- `agentsmd-distribution`: remove the bundled read-only catalogue snapshot requirement. The workflow-asset bundling and the `agentsmd-install` provisioning entry point are unchanged.
- `agentsmd-mcp-server`: catalogue-root resolution no longer includes a bundled fallback.
- `agentsmd-operator-cli`: catalogue-root resolution no longer includes a read-only fallback; all commands require a resolvable root.
- `prompt-catalogue-management`: drop the "distributed package may ship a read-only snapshot" allowance.

## Impact

- Code: `agentsmd/catalogue.py`, `agentsmd/server.py`, `pyproject.toml`.
- Distribution: editable install (`pip install -e <checkout>`); the server serves the live catalogue via `bin/agentsmd-serve`.
- Backward compatible for the master-repo/checkout workflow; only the never-used checkout-less path is removed.
