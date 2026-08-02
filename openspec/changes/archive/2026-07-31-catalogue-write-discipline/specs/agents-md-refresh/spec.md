# agents-md-refresh delta spec

## ADDED Requirements

### Requirement: browsecontent tags self-discipline violations on curated files
When `browsecontent` inspects curated files in the catalogue as part of its diff scan, it SHALL tag each curated file's diff item with `self-discipline violation: <category>` if the curated file fails the catalog self-discipline check (defined in `prompt-catalogue-management` capability, applied at `agents-md-generation` consumer invocation). Curated files that pass the check receive no extra tag. The tag is appended to the existing `[catalogue:<cat>]` tag and is operator-visible.

#### Scenario: Diff tags a self-discipline violation
- **WHEN** `browsecontent` inspects a curated file that exceeds 100 lines or has a missing `trigger:` field
- **THEN** the diff item is tagged `[catalogue:<cat>]` AND `self-discipline violation: <cat>`. Operator sees both labels on the same item.

#### Scenario: Diff does NOT tag files that pass
- **WHEN** `browsecontent` inspects a curated file that passes all four hygiene rules
- **THEN** the diff item receives only the `[catalogue:<cat>]` tag. The `self-discipline violation:` label is reserved exclusively for files that fail the check.

#### Scenario: Tagged item offers curatecontent follow-up
- **WHEN** the diff item is tagged `self-discipline violation: <cat>`
- **THEN** the suggested follow-up is explicitly `/refresh-agents-content curatecontent <cat>` (not `addcontent`), and the operator-facing summary text reads "operator action: curatecontent <cat> to repair the file before adding new content."
