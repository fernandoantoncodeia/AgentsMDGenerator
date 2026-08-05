## Why

Today the MCP server and operator CLI only find the catalogue when the current working directory is the master repo checkout. That blocks the intended consumer workflow: install once, then run `/update-agents` in any project. We need a PATH-installed server that resolves the catalogue from an explicit root, an environment variable, the CWD, or a read-only snapshot shipped in the package, plus a one-command installer that wires the workflow into both Factory and Claude at the user level on any machine.

## What Changes

- Add catalogue-root resolution: `--catalogue-root` flag > `AGENTSMD_CATALOGUE_ROOT` env > `prompt-catalogue/` in CWD > read-only snapshot bundled in the installed package.
- Bundle a read-only copy of `curated/` in the distributed wheel so a PATH-installed `agentsmd-server` serves reads from any directory. Writes still require a writable root; writes against the bundled snapshot are refused.
- The MCP server startup no longer hard-fails when CWD lacks `prompt-catalogue/`; it resolves a root or fails with a message that names the resolution order.
- The operator CLI accepts `--catalogue-root` and resolves the same way; read commands may use the bundled snapshot, write commands require a writable root.
- New `agentsmd-install` entry point provisions user-level MCP config and the `update-agents` skill + command for both Factory (`~/.factory/`) and Claude (`~/.claude/`), idempotently.
- Bundle the `update-agents` skill and command as package assets so the installer works from a pip/pipx install with no repo checkout.

## Capabilities

### New Capabilities
- `agentsmd-distribution`: bundled read-only catalogue snapshot, bundled workflow assets, and the `agentsmd-install` provisioning entry point for Factory and Claude.

### Modified Capabilities
- `agentsmd-mcp-server`: add a catalogue-root resolution requirement and a `--catalogue-root` startup option.
- `agentsmd-operator-cli`: resolve the catalogue root from flag/env/CWD instead of requiring the master-repo CWD; refuse writes without a writable root.
- `prompt-catalogue-management`: allow a read-only snapshot in the distributed package while keeping the single canonical writable copy in the master repo.

## Impact

- Code: `agentsmd/catalogue.py` (root resolution), `agentsmd/server.py` and `agentsmd/cli.py` (`--catalogue-root`), `agentsmd/install.py` (new), `pyproject.toml` (bundle assets, new entry point).
- Distribution: enables `pipx install agentsmd` + `agentsmd-install` adoption on any machine.
- Backward compatible: running from the master repo CWD keeps working unchanged.
