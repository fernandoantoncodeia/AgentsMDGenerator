## ADDED Requirements

### Requirement: Server resolves the catalogue root from multiple sources
The server SHALL resolve the catalogue directory in this precedence order: the `--catalogue-root` startup option, the `AGENTSMD_CATALOGUE_ROOT` environment variable, a `prompt-catalogue/` directory in the current working directory, then a read-only snapshot bundled in the installed package. A configured root MAY be the `prompt-catalogue` directory itself or a directory that contains it. If none resolve, the server SHALL exit with an error that names the resolution order.

#### Scenario: Explicit root wins
- **WHEN** the server starts with `--catalogue-root /path/to/prompt-catalogue`
- **THEN** it serves categories from that directory regardless of the current working directory

#### Scenario: Environment variable is honored
- **WHEN** `AGENTSMD_CATALOGUE_ROOT` is set and no `--catalogue-root` is given
- **THEN** the server serves categories from the environment-specified directory

#### Scenario: Working directory fallback preserves existing behavior
- **WHEN** no option or environment variable is set but the current working directory contains `prompt-catalogue/`
- **THEN** the server serves categories from `./prompt-catalogue` as before

#### Scenario: Bundled snapshot serves reads anywhere
- **WHEN** the server is launched from a directory with no `prompt-catalogue/` and no root is configured
- **THEN** it serves curated categories from the read-only snapshot bundled in the installed package

#### Scenario: No catalogue resolvable
- **WHEN** no root resolves and no bundled snapshot is present
- **THEN** the server exits with an error naming the resolution order (flag, environment variable, working directory, bundled snapshot)
