## ADDED Requirements

### Requirement: Package bundles a read-only curated snapshot
The distributed package SHALL include a read-only snapshot of `curated/` so a PATH-installed `agentsmd-server` can serve curated reads from any directory without a repo checkout. The snapshot SHALL be used only as the lowest-precedence catalogue source and SHALL never be written to.

#### Scenario: Snapshot ships in the wheel
- **WHEN** the wheel is built and inspected
- **THEN** it contains the curated category markdown files under a package data path

#### Scenario: Snapshot serves reads after pipx install
- **WHEN** `agentsmd-server` is started from an arbitrary directory after `pipx install`
- **THEN** curated categories are readable over MCP without any repo checkout or environment variable

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
