## MODIFIED Requirements

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
