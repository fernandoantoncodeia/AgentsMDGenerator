# Tasks

## 1. Catalogue root resolution
- [x] 1.1 Add `set_catalogue_root`, `resolve_catalogue_dir`, `curated_dir()`, `proposed_dir()` to `catalogue.py`
- [x] 1.2 Implement precedence: override > `AGENTSMD_CATALOGUE_ROOT` > `./prompt-catalogue` > bundled snapshot, with candidate normalization
- [x] 1.3 Add `catalogue_is_read_only()` and `_require_writable()`; guard all write ops
- [x] 1.4 Replace `CURATED_DIR` / `PROPOSED_DIR` / `_ensure_catalogue_root` uses with the resolver

## 2. Server and CLI options
- [x] 2.1 Add `--catalogue-root` to `server.py main()`; resolve at startup; drop hard CWD-only check
- [x] 2.2 Add group-level `--catalogue-root` to `cli.py`; read cmds tolerate bundled, write cmds require writable
- [x] 2.3 Remove `_ensure_master_repo()` in favor of resolution

## 3. Packaging and assets
- [x] 3.1 Add hatchling `force-include` for the curated snapshot and workflow assets
- [x] 3.2 Add `agentsmd-install` entry point in `pyproject.toml`
- [x] 3.3 Implement bundled-snapshot path lookup in `catalogue.py`

## 4. Installer
- [x] 4.1 Implement `agentsmd/install.py` with `--tool` and `--server-command` options
- [x] 4.2 Merge `agentsmd` stdio entry into `~/.factory/mcp.json` and `~/.claude.json` (preserve other keys)
- [x] 4.3 Copy bundled `update-agents` skill + command into `~/.factory/` and `~/.claude/`
- [x] 4.4 Make idempotent and report written paths

## 5. Verification
- [x] 5.1 Build wheel; confirm curated snapshot and workflow assets are present
- [x] 5.2 Install into a temp env; start `agentsmd-server` from an unrelated CWD; confirm curated reads via MCP
- [x] 5.3 Confirm write command refuses against the bundled snapshot
- [x] 5.4 Run `agentsmd-install --tool factory` into a temp HOME; confirm merge + assets; re-run and confirm idempotence
- [x] 5.5 Confirm master-repo CWD behavior is unchanged (list/status/curate)
