# agents-md-generation delta spec

## ADDED Requirements

### Requirement: Catalog self-discipline scan runs at every /update-agents invocation
After the splice pass, every `/update-agents` invocation SHALL walk `prompt-catalogue/curated/*.md` and emit a `Catalog self-discipline check:` section in the completion summary. The scan is read-only; it MUST NOT refuse the `/update-agents` invocation. Per curated file, the workflow outputs one of:

- `ok` — the file passes all four hygiene rules.
- `<n> lines (cap 100)` — the file exceeds the per-category cap from D11.
- `bullet <i> exceeds 200 chars (<n> chars)` — over-length bullet.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category dedupe candidate.
- `missing trigger:` — HARD contract violation, named in the summary.

#### Scenario: Self-discipline scan surfaces oversize curated file
- **WHEN** a curated file exceeds 100 lines
- **THEN** the completion summary has a `Catalog self-discipline check:` section listing the file with its `>100 lines` finding. The workflow still emits the consumer AGENTS.md as normal; the scan is informative.

#### Scenario: Self-discipline scan surfaces missing trigger
- **WHEN** a curated file lacks `trigger:` frontmatter
- **THEN** the file is named in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is flagged; the operator is expected to invoke `curatecontent` on the file to repair.

#### Scenario: Self-discipline scan reports clean state
- **WHEN** all curated files pass the four hygiene rules
- **THEN** the completion summary has a `Catalog self-discipline check: all files ok` line. The scan still runs; the absence of findings is itself a positive signal in the consumer report.
