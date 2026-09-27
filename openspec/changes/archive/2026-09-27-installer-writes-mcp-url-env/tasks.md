## 1. Installer writes the env var

- [x] 1.1 Add `_resolve_shell_rc(home, shell_env)` to pick `~/.zshrc` or `~/.bashrc` from `$SHELL`, defaulting to `~/.zshrc`.
- [x] 1.2 Add `_write_env_var(rc_path, server_command)` that inserts/updates a marker-delimited `export AGENTSMD_MCP_URL=...` block idempotently.
- [x] 1.3 Wire both into `main()`, gated by a new `--no-shell-env` flag (default: write it), independent of `--tool`.
- [x] 1.4 Echo the profile path written and a reminder to open a new shell or `source` it.

## 2. Tests

- [x] 2.1 `tests/test_install_env.py`: fresh write creates the marker block with the correct value.
- [x] 2.2 Re-running with a different `--server-command` updates the value in place without duplicating the block.
- [x] 2.3 Unrelated existing content in the rc file is preserved byte-for-byte outside the marker block.
- [x] 2.4 `--no-shell-env` skips the write entirely.
- [x] 2.5 `$SHELL` unset or unrecognized falls back to `~/.zshrc`.

## 3. Docs and verification

- [x] 3.1 Update `INSTALL.md` to document the shell-profile write and `--no-shell-env`.
- [x] 3.2 Run the focused test file.
- [x] 3.3 Validate the OpenSpec change strictly.
