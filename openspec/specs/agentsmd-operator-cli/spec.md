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
The `agentsmd curatecategory <name>` command SHALL promote `prompt-catalogue/proposed/<name>.md` to `prompt-catalogue/curated/<name>.md`, applying the same cap checks and refusal profile as `curatecontent`. It SHALL treat another proposed entry as a remap candidate ONLY when that entry's `trigger:` shares distinctive evidence with `<name>`'s trigger; common words (such as "project", "contains", "file", "source", "directory") are ignored. When one or more genuine remap candidates exist, the command SHALL list them and stop WITHOUT promoting or modifying any file, unless `--no-remap` is passed; with `--no-remap` it SHALL promote `<name>` as-is and leave the other proposed entries untouched. When no genuine candidate exists, the command SHALL promote without prompting. `--force` overrides size and bullet-length caps only.

#### Scenario: Operator curates a new category
- **WHEN** the operator runs `agentsmd curatecategory go-project` and no other proposed entry shares distinctive trigger evidence with it
- **THEN** the CLI creates `prompt-catalogue/curated/go-project.md` and removes the proposed entry

#### Scenario: CLI surfaces remap candidates
- **WHEN** another proposed entry shares distinctive trigger evidence with `<name>` and `--no-remap` is not passed
- **THEN** the CLI lists the overlapping entries as `remap candidates:` and exits without promoting or modifying any file

#### Scenario: Unrelated proposed entries do not block promotion
- **WHEN** other proposed entries exist but none share distinctive trigger evidence with `<name>`
- **THEN** the CLI promotes `<name>` without listing any remap candidates

#### Scenario: Operator promotes despite candidates with --no-remap
- **WHEN** genuine remap candidates exist and the operator runs `agentsmd curatecategory <name> --no-remap`
- **THEN** the CLI promotes `<name>` as-is, removes its proposed entry, and leaves the other proposed entries untouched

### Requirement: CLI provides list command
The `agentsmd list` command SHALL print the names of all curated and all proposed categories, marking which categories exist in both states.

#### Scenario: Operator lists catalogue state
- **WHEN** the operator runs `agentsmd list`
- **THEN** the CLI prints a curated list, a proposed list, and a `pending curation` list for categories present in both folders

### Requirement: CLI provides status command
The `agentsmd status` command SHALL run the catalog self-discipline scan against every curated file and print the findings. The scan SHALL consider only real markdown list items (lines beginning with `-` or `*`); prose paragraphs and headings are not treated as bullets. Near-duplicate findings SHALL use the length-relative rule (edit distance ≤30 chars AND ≤40% of the shorter bullet's length). It is read-only.

#### Scenario: Operator checks catalogue hygiene
- **WHEN** the operator runs `agentsmd status`
- **THEN** the CLI prints one line per curated file: `ok`, `>100 lines`, `bullet N exceeds 200 chars`, `near-duplicate vs bullet N`, or `missing trigger:`, without modifying any file

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

### Requirement: CLI provides recurate command
The `agentsmd recurate <name>` command SHALL re-sweep an existing curated category in place. It SHALL re-run the trailer trim and drop near-duplicate list items (keeping the first occurrence) using the same length-relative near-duplicate rule as the scan, while preserving non-bullet content (prose and headings) and the frontmatter. It SHALL require an existing `prompt-catalogue/curated/<name>.md` and SHALL NOT read or modify `proposed/`. It applies the same cap checks and refusal profile as `curatecontent`: `--force` overrides size and bullet-length caps only, and a missing `trigger:` is non-overridable. `--no-trim-tails` skips the trailer-trim phase.

#### Scenario: Operator re-sweeps a curated category
- **WHEN** the operator runs `agentsmd recurate <name>` on a curated file that contains a genuine near-duplicate list item
- **THEN** the CLI drops the later duplicate, preserves all other content and the frontmatter, rewrites the curated file, and reports the dropped bullet

#### Scenario: recurate refuses without a curated entry
- **WHEN** the operator runs `agentsmd recurate <name>` and `prompt-catalogue/curated/<name>.md` does not exist
- **THEN** the CLI refuses with an error and writes nothing

#### Scenario: recurate leaves distinct short bullets intact
- **WHEN** a curated file has short, similarly-worded but distinct list items (such as one-line command references)
- **THEN** the length-relative rule does not treat them as duplicates and recurate keeps them all

