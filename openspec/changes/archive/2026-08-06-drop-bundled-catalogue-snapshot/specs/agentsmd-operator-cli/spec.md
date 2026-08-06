## REMOVED Requirements

### Requirement: CLI operates only on the master catalogue directory
**Reason**: Replaced by a resolution requirement without the read-only bundled-snapshot fallback (see ADDED below). The bundled-snapshot write-refusal scenario is obsolete.
**Migration**: All CLI commands now require a resolvable `prompt-catalogue/` root via `--catalogue-root`, `AGENTSMD_CATALOGUE_ROOT`, or the current working directory.

## ADDED Requirements

### Requirement: CLI resolves the catalogue root from flag, environment, or working directory
The CLI SHALL resolve the catalogue root in this precedence order: the `--catalogue-root` option, the `AGENTSMD_CATALOGUE_ROOT` environment variable, then a `prompt-catalogue/` directory in the current working directory. All commands (`list`, `status`, `addcontent`, `addcategory`, `curatecontent`, `curatecategory`) require a resolvable root. If no root resolves, the CLI SHALL refuse with an error that names the resolution order.

#### Scenario: CLI refuses to run outside master repo
- **WHEN** the operator runs a command with no `--catalogue-root`, no `AGENTSMD_CATALOGUE_ROOT`, and no `prompt-catalogue/` in the current directory
- **THEN** the CLI refuses with an error naming the resolution order and performs no file operations

#### Scenario: Explicit root is honored
- **WHEN** the operator runs `agentsmd --catalogue-root /path/to/prompt-catalogue curatecontent <cat>`
- **THEN** the CLI operates on that directory regardless of the current working directory
