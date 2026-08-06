# agentsmd-operator-cli Specification

## Purpose
TBD - created by archiving change mcp-catalogue-rearchitecture. Update Purpose after archive.
## Requirements
### Requirement: CLI provides addcontent command
The `agentsmd addcontent <category> --body <text>` command SHALL append a new entry to `prompt-catalogue/proposed/<category>.md`, applying the same pre-trim rules as the MCP `catalogue_addcontent` tool. If the proposed file does not exist, the CLI creates it with frontmatter inherited from the curated category if one exists.

#### Scenario: Operator adds a bullet to proposed
- **WHEN** the operator runs `agentsmd addcontent python-project --body "..."`
- **THEN** the CLI appends the trimmed body to `prompt-catalogue/proposed/python-project.md`, creating the file if necessary, and prints the resulting file path

#### Scenario: Operator adds without body
- **WHEN** the operator runs `agentsmd addcontent python-project` without `--body`
- **THEN** the CLI refuses with `error: --body is required` and writes nothing

### Requirement: CLI provides addcategory command
The `agentsmd addcategory <name> --trigger <rule> --body <text>` command SHALL create `prompt-catalogue/proposed/<name>.md` with the supplied frontmatter and trimmed body. It SHALL reject collisions with existing curated categories.

#### Scenario: Operator proposes a new category
- **WHEN** the operator runs `agentsmd addcategory go-project --trigger "*.go files present" --body "..."`
- **THEN** the CLI creates `prompt-catalogue/proposed/go-project.md` and prints the file path

#### Scenario: Operator collides with curated category
- **WHEN** the operator runs `agentsmd addcategory python-project` and `prompt-catalogue/curated/python-project.md` exists
- **THEN** the CLI refuses with `error: category already in curated; use curatecontent` and writes nothing

### Requirement: CLI provides curatecontent command
The `agentsmd curatecontent <category>` command SHALL merge `prompt-catalogue/proposed/<category>.md` into `prompt-catalogue/curated/<category>.md`, applying dedupe, self-discipline checks, and the same refusal profile as the previous `curatecontent` action. It SHALL support `--force` for size and bullet-length overrides only.

#### Scenario: Operator curates content
- **WHEN** the operator runs `agentsmd curatecontent python-project`
- **THEN** the CLI merges the proposed body into the curated file, removes the proposed entry, and prints the merged file path

#### Scenario: CLI refuses over-cap merge
- **WHEN** the merged result would exceed 100 lines or contain a bullet >200 chars
- **THEN** the CLI refuses with a trim diff and a `Suggested fix:` line, leaving the proposed file unchanged

#### Scenario: Force override for size violations
- **WHEN** the operator runs `agentsmd curatecontent python-project --force`
- **THEN** the CLI proceeds despite the size or bullet-length violation and records the override in the output

### Requirement: CLI provides curatecategory command
The `agentsmd curatecategory <name>` command SHALL promote `prompt-catalogue/proposed/<name>.md` to `prompt-catalogue/curated/<name>.md`, applying the same cap checks and refusal profile as `curatecontent`. It SHALL surface remap candidates and require operator confirmation before any remap.

#### Scenario: Operator curates a new category
- **WHEN** the operator runs `agentsmd curatecategory go-project`
- **THEN** the CLI creates `prompt-catalogue/curated/go-project.md` and removes the proposed entry

#### Scenario: CLI surfaces remap candidates
- **WHEN** the proposed category overlaps with existing categories
- **THEN** the CLI prints the proposed entry and a list of remap candidates, then waits for explicit confirmation before any remap

### Requirement: CLI provides list command
The `agentsmd list` command SHALL print the names of all curated and all proposed categories, marking which categories exist in both states.

#### Scenario: Operator lists catalogue state
- **WHEN** the operator runs `agentsmd list`
- **THEN** the CLI prints a curated list, a proposed list, and a `pending curation` list for categories present in both folders

### Requirement: CLI provides status command
The `agentsmd status` command SHALL run the catalog self-discipline scan against every curated file and print the findings. It is read-only.

#### Scenario: Operator checks catalogue hygiene
- **WHEN** the operator runs `agentsmd status`
- **THEN** the CLI prints one line per curated file: `ok`, `>100 lines`, `bullet N exceeds 200 chars`, or `missing trigger:`, without modifying any file

### Requirement: CLI contains no LLM logic
The CLI SHALL NOT invoke any LLM, perform web summarization, embed text, or otherwise use model inference. It is a deterministic file-operation tool.

#### Scenario: CLI source inspection shows no LLM
- **WHEN** a maintainer inspects the CLI source code
- **THEN** there is no LLM dependency, no inference call, and no prompt construction

### Requirement: CLI resolves the catalogue root from flag, environment, or working directory
The CLI SHALL resolve the catalogue root in this precedence order: the `--catalogue-root` option, the `AGENTSMD_CATALOGUE_ROOT` environment variable, then a `prompt-catalogue/` directory in the current working directory. All commands (`list`, `status`, `addcontent`, `addcategory`, `curatecontent`, `curatecategory`) require a resolvable root. If no root resolves, the CLI SHALL refuse with an error that names the resolution order.

#### Scenario: CLI refuses to run outside master repo
- **WHEN** the operator runs a command with no `--catalogue-root`, no `AGENTSMD_CATALOGUE_ROOT`, and no `prompt-catalogue/` in the current directory
- **THEN** the CLI refuses with an error naming the resolution order and performs no file operations

#### Scenario: Explicit root is honored
- **WHEN** the operator runs `agentsmd --catalogue-root /path/to/prompt-catalogue curatecontent <cat>`
- **THEN** the CLI operates on that directory regardless of the current working directory

