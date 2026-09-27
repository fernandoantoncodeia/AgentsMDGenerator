# agentsmd-distribution Specification

## Purpose
TBD - created by archiving change portable-catalogue-and-installer. Update Purpose after archive.

## Requirements

### Requirement: Package bundles the update-agents workflow assets
The distributed package SHALL include the `update-agents` skill and slash-command source so the installer can provision them without a repo checkout.

#### Scenario: Assets ship in the wheel
- **WHEN** the wheel is built and inspected
- **THEN** it contains the `update-agents` SKILL.md and command markdown as package data

### Requirement: Installer provisions user-level configuration for Factory and Claude
The package SHALL provide an `agentsmd-install` entry point that writes a user-level MCP server registration and installs the `update-agents` skill and command at the user level for both Factory (`~/.factory/`) and Claude (`~/.claude/`). The installer SHALL be idempotent and SHALL merge into existing configuration files rather than overwrite unrelated entries.

#### Scenario: Fresh install wires both tools
- **WHEN** `agentsmd-install` runs on a machine with no prior agentsmd configuration
- **THEN** `~/.factory/mcp.json` and `~/.claude.json` gain an `agentsmd` stdio server entry, and the `update-agents` skill and command are present under both `~/.factory/` and `~/.claude/`

#### Scenario: Re-running the installer is safe
- **WHEN** `agentsmd-install` runs a second time
- **THEN** it updates the `agentsmd` entry in place and leaves other MCP servers, skills, and commands untouched

#### Scenario: Installer targets a specific tool
- **WHEN** `agentsmd-install --tool factory` runs
- **THEN** only Factory user-level configuration is written and Claude configuration is left unchanged

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
