## MODIFIED Requirements

### Requirement: CLI operates only on the master catalogue directory
The CLI SHALL resolve the catalogue root in this precedence order: the `--catalogue-root` option, the `AGENTSMD_CATALOGUE_ROOT` environment variable, then a `prompt-catalogue/` directory in the current working directory. Read commands (`list`, `status`) MAY additionally fall back to the read-only snapshot bundled in the package. Write commands (`addcontent`, `addcategory`, `curatecontent`, `curatecategory`) SHALL require a writable resolved root and SHALL refuse to run against the bundled read-only snapshot. If no root resolves, the CLI SHALL refuse with an error that names the resolution order.

#### Scenario: CLI refuses to run outside master repo
- **WHEN** the operator runs a write command with no `--catalogue-root`, no `AGENTSMD_CATALOGUE_ROOT`, and no `prompt-catalogue/` in the current directory
- **THEN** the CLI refuses with an error naming the resolution order and performs no file operations

#### Scenario: Explicit root is honored
- **WHEN** the operator runs `agentsmd --catalogue-root /path/to/prompt-catalogue curatecontent <cat>`
- **THEN** the CLI operates on that directory regardless of the current working directory

#### Scenario: Writes against the bundled snapshot are refused
- **WHEN** only the read-only bundled snapshot is resolvable and the operator runs a write command
- **THEN** the CLI refuses with an error stating the resolved catalogue is read-only
