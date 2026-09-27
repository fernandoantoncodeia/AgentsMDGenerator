## Why

`update-agents` resolves its MCP endpoint in strict order: `--mcp-url` → `AGENTSMD_MCP_URL` → consumer-root `.agentsmd/mcp.json` → refuse. `agentsmd-install` currently only writes the native `~/.factory/mcp.json` and `~/.claude.json` registrations, which the skill's own discovery order never checks. Every new consumer project therefore needs a hand-written `.agentsmd/mcp.json` even on a machine where the server is already installed, and users hit `error: no MCP server configured` despite a working install.

## What Changes

- `agentsmd-install` additionally writes `export AGENTSMD_MCP_URL="<server_command>"` into the current user's shell profile, idempotently, bounded by marker comments so re-running the installer updates the value in place instead of duplicating lines.
- Shell profile target is resolved from `$SHELL` (zsh → `~/.zshrc`, bash → `~/.bashrc`), defaulting to `~/.zshrc` when `$SHELL` is unset or unrecognized.
- Add a `--no-shell-env` flag to skip this step for users who manage their shell profile manually.
- Installer output states the profile path written and reminds the user to open a new shell (or `source` the file) for the variable to take effect.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agentsmd-distribution`: installer also provisions `AGENTSMD_MCP_URL` in the user's shell profile, with an opt-out flag.

## Impact

Affected files: `agentsmd/install.py`, `INSTALL.md`, `tests/test_install_env.py` (new). No change to the MCP server, catalogue, or `update-agents` skill discovery order itself — this only makes step 2 of that existing order reliably satisfied out of the box. No new dependencies.
