## ADDED Requirements

### Requirement: Installer provisions AGENTSMD_MCP_URL in the user's shell profile

The `agentsmd-install` entry point SHALL, in addition to writing MCP server registrations, insert an `export AGENTSMD_MCP_URL="<server-command>"` line into the current user's shell profile (`~/.zshrc` for zsh, `~/.bashrc` for bash, defaulting to `~/.zshrc` when the shell cannot be determined), bounded by idempotency marker comments. This SHALL run once per invocation regardless of `--tool`, and SHALL be skippable via `--no-shell-env`.

#### Scenario: Fresh install writes the env var

- **WHEN** `agentsmd-install` runs on a machine whose shell profile has no prior `AGENTSMD_MCP_URL` marker block
- **THEN** the resolved shell profile gains a marker-delimited block exporting `AGENTSMD_MCP_URL` set to the resolved `--server-command` value

#### Scenario: Re-running the installer updates the value in place

- **WHEN** `agentsmd-install --server-command <new>` runs again on a profile that already has the marker block
- **THEN** the block's exported value is updated to `<new>` and no duplicate block or line is added

#### Scenario: Unrelated shell profile content is preserved

- **WHEN** the shell profile contains other exports or configuration outside the marker block
- **THEN** that content is left byte-for-byte unchanged

#### Scenario: Opt-out flag skips the shell profile write

- **WHEN** `agentsmd-install --no-shell-env` runs
- **THEN** no shell profile is read or written, and the completion output does not mention a profile path

#### Scenario: Unrecognized shell falls back to zsh

- **WHEN** `$SHELL` is unset or does not name `zsh` or `bash`
- **THEN** the installer targets `~/.zshrc`
