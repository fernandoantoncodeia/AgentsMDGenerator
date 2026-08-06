## MODIFIED Requirements

### Requirement: Sourced principles list is concrete and citable
The workflow SHALL embed a Sourced Principles list covering, at minimum: command-first instructions; closure-defined completion; show-don't-tell examples; task-organized sections; escalation rules plus a Never list; explicit boundaries; three-tier NEVER/ASK/ALWAYS judgment; Toolchain First; length discipline (start 20-50 lines, ~512-line cap, 32 KiB Code hard cap); hand-written beats LLM-generated; file-scoped commands preferred; concrete pointers not lists; good and bad example pairing; project anchor stack with versions; cross-tool portability (Claude Code wrapper or symlink); living documentation updated in same PR as convention changes. The length-discipline numbers are defaults; the workflow SHALL read the effective AGENTS.md line and byte caps from `catalogue://config`. Each principle SHALL cite one or more of the six canonical sources by URL inline.

#### Scenario: Each principle has a source citation
- **WHEN** a maintainer or user inspects the workflow's Sourced Principles list
- **THEN** every principle is followed by at least one source URL that established or documented it

#### Scenario: Cross-source convergence
- **WHEN** a principle is established by more than one of the six canonical sources
- **THEN** the citation lists all of them in order of authority (open standard first, then practitioner guides)

#### Scenario: Length discipline backed by named evidence
- **WHEN** the workflow's length-discipline rule (start 20-50 lines, cap ~512, hard cap 32 KiB Code) is questioned
- **THEN** the citation surfaces the GitHub Engineering analysis of 2,500+ repositories, the Gloaguen et al. 2026 ETH Zurich empirical study, and the Princeton agent-runtime study as named evidence

### Requirement: Catalog self-discipline scan runs at every /update-agents invocation
After the splice pass, every `/update-agents` invocation SHALL read `catalogue://categories` and, for each curated category, request the body via `catalogue://curated/<category>` to emit a `Catalog self-discipline check:` section in the completion summary. The scan is read-only; it MUST NOT refuse the `/update-agents` invocation. The per-category line cap is the configured value (default 32; read from `catalogue://config`). Per curated file, the workflow outputs one of:

- `ok` — the file passes all four hygiene rules.
- `<n> lines (cap <configured>)` — the file exceeds the per-category cap.
- `bullet <i> exceeds 200 chars (<n> chars)` — over-length bullet.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category dedupe candidate.
- `missing trigger:` — HARD contract violation, named in the summary.

#### Scenario: Self-discipline scan surfaces oversize curated file
- **WHEN** a curated file exceeds the configured per-category cap
- **THEN** the completion summary has a `Catalog self-discipline check:` section listing the file with its over-cap finding. The workflow still emits the consumer AGENTS.md as normal; the scan is informative.

#### Scenario: Self-discipline scan surfaces missing trigger
- **WHEN** a curated file lacks `trigger:` frontmatter
- **THEN** the file is named in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is flagged; the operator is expected to invoke `agentsmd curatecontent <category>` in the master repo to repair it.

#### Scenario: Self-discipline scan reports clean state
- **WHEN** all curated files pass the four hygiene rules
- **THEN** the completion summary has a `Catalog self-discipline check: all files ok` line. The scan still runs; the absence of findings is itself a positive signal in the consumer report.

#### Scenario: Self-discipline scan runs over MCP
- **WHEN** the workflow performs the self-discipline scan
- **THEN** it reads each curated file body via `catalogue://curated/<category>` and metadata via `catalogue://categories`; it does not read a local `prompt-catalogue/curated/` directory
