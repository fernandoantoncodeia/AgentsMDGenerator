## 1. Specs

- [x] 1.1 Remove the bundled read-only snapshot requirement from `agentsmd-distribution`
- [x] 1.2 Modify `agentsmd-mcp-server` resolution requirement to drop the bundled fallback
- [x] 1.3 Modify `agentsmd-operator-cli` resolution requirement to drop the read-only fallback
- [x] 1.4 Modify `prompt-catalogue-management` to drop the read-only snapshot allowance
- [x] 1.5 `openspec validate drop-bundled-catalogue-snapshot --strict`

## 2. Code

- [x] 2.1 Drop the `force-include` of `prompt-catalogue/curated` in `pyproject.toml`
- [x] 2.2 Remove `_bundled_catalogue_dir`, the bundled fallback in `resolve_catalogue_dir`, `catalogue_is_read_only`, and `_require_writable` (and its calls) in `agentsmd/catalogue.py`
- [x] 2.3 Remove the read-only startup notice in `agentsmd/server.py`
- [x] 2.4 Verify server stdio handshake and `agentsmd status` / `agentsmd list`

## 3. Archive

- [x] 3.1 `openspec archive drop-bundled-catalogue-snapshot -y`
