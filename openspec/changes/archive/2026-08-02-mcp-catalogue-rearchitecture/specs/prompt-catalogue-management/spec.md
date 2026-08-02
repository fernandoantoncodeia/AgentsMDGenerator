# prompt-catalogue-management Specification

## Purpose
Defines the lifecycle and invariants of the central prompt catalogue. The catalogue lives only in the AgentsMDGenerator master repo and is accessed through the MCP server (project reads and proposals) or the deterministic `agentsmd` operator CLI (curation and direct operator edits). No consumer project hosts a local catalogue.

## MODIFIED Requirements

### Requirement: Catalogue folder structure and invariants
The catalogue SHALL live at `prompt-catalogue/` in the AgentsMDGenerator master repo, with two subfolders: `curated/` and `proposed/`. Both SHALL contain one markdown file per category. The filename (without `.md` extension) is the category identifier. Categories use kebab-case. A category MAY exist in both folders simultaneously — that signals the operator an item is awaiting curation against an already-curated entry. Consumer projects SHALL NOT contain a `prompt-catalogue/` directory.

#### Scenario: Curated folder has one file per category
- **WHEN** the operator inspects `prompt-catalogue/curated/` in the master repo
- **THEN** each file is named `<category>.md` and only one entry per category identifier lives there

#### Scenario: Proposed folder is the operator queue
- **WHEN** the operator inspects `prompt-catalogue/proposed/` in the master repo
- **THEN** each file is named `<category>.md`; entries there have not yet been reviewed and promulgated into curated output

#### Scenario: Same category in both folders
- **WHEN** `<category>.md` exists in both `curated/` and `proposed/` in the master repo
- **THEN** the operator sees two entries for the same category: the in-use curated version and the draft pending review. `agentsmd curatecontent` resolves this in the master repo.

#### Scenario: Consumer project has no catalogue folder
- **WHEN** the operator inspects a consumer project after this change
- **THEN** there is no `prompt-catalogue/` directory; the project reads the catalogue via MCP

### Requirement: Category file format
Each `<category>.md` file in the master repo MUST carry YAML frontmatter with at least `title:` and `trigger:` fields. The body is the prompt text. The `title:` becomes the AGENTS.md section heading when spliced. The `trigger:` is a deterministic expression against a project scan, evaluated by the project skill. Optionally `trigger-confidence: heuristic` flags a non-deterministic trigger; the workflow surfaces heuristic matches in the completion summary rather than auto-splicing.

#### Scenario: Valid frontmatter parses
- **WHEN** a file's YAML frontmatter contains `title:` and `trigger:`
- **THEN** the workflow reads both fields via MCP and uses them in the splice decision

#### Scenario: Missing required frontmatter
- **WHEN** a file is missing `title:` or `trigger:`
- **THEN** the workflow reports the file as malformed in the completion summary and skips it

### Requirement: addcontent appends a proposed entry to the catalogue
The `catalogue_addcontent` MCP tool (project skill) and the `agentsmd addcontent` CLI operator command SHALL append a new entry to `prompt-catalogue/proposed/<category>.md` in the master repo. Both surfaces SHALL pre-trim the supplied body BEFORE writing: drop duplicates against existing curated and proposed bullets in the same category (≤30 char edit distance), drop verbose trailing clauses (`where X`, `in which case`, `; note that Y` once the leading commands are present), and split any bullet longer than 200 chars at its first sentence boundary into two bullets. If a resulting bullet is still >200 chars, refuse the call rather than write. Operators can opt out of the trim pass with `--no-trim-tails` per invocation; the dedupe and length caps are mandatory (no opt-out flag). The pre-trim pass is reported in the tool or command result.

#### Scenario: addcontent dedupes near-duplicates in same category
- **WHEN** a caller invokes `catalogue_addcontent` (or `agentsmd addcontent`) with a bullet that has ≤30 char edit distance against an existing curated bullet in the same category
- **THEN** the surface drops the duplicate bullet, writes only new content, and reports `addcontent: dedupe <n> bullets vs curated` in the result

#### Scenario: addcontent splits an over-long bullet
- **WHEN** a caller supplies a bullet >200 chars
- **THEN** the surface splits at the first sentence boundary and writes two bullets. If either half is still >200 chars, the surface refuses with `addcontent: bullet too long (≥200 chars after split)` and writes nothing.

#### Scenario: addcontent drops a redundant trailer
- **WHEN** a caller supplies a bullet ending with `where requirements.txt is substituted by the actual filename` and the leading imperative already covers the substitution
- **THEN** the surface drops the trailer and reports `addcontent: trim tail on bullet 1 (dropped "<trailer text>")`. Operator can disable with `--no-trim-tails` on the CLI.

#### Scenario: addcontent to a new proposed file
- **WHEN** a caller invokes `catalogue_addcontent` or `agentsmd addcontent` for category `shell-tooling` and `prompt-catalogue/proposed/shell-tooling.md` does not exist
- **THEN** the surface creates the file with the supplied body (after pre-trim) and writes a YAML frontmatter header with the supplied title (or a default generated from the category name)

#### Scenario: addcontent to an existing proposed file
- **WHEN** `prompt-catalogue/proposed/shell-tooling.md` already exists
- **AND** a caller invokes `catalogue_addcontent` or `agentsmd addcontent` for `shell-tooling`
- **THEN** the surface appends the new entry (after pre-trim) with separator (e.g. `---` between entries) so multiple proposed items can coexist in one file

#### Scenario: addcontent rejects missing category
- **WHEN** a caller invokes `catalogue_addcontent` without a category or `agentsmd addcontent` without a positional category
- **THEN** the surface reports `error: --category is required` and writes nothing

### Requirement: curatecontent promotes one proposed entry to curated, merge-and-simplify
The `catalogue_curatecontent` MCP tool (operator only) and the `agentsmd curatecontent` CLI command SHALL move one specific proposed entry to `prompt-catalogue/curated/<category>.md` in the master repo. Both surfaces SHALL perform a merge against any existing curated entry: identify overlap with the proposed entry, deduplicate (≤30 char edit distance), apply the length-discipline rule (per-category ≤100 lines, per-bullet ≤200 chars). The proposed entry MUST be removed from `proposed/<category>.md` after successful curation. **`--force` override.** If the merged file would exceed 100 lines OR any bullet would exceed 200 chars, the surface SHALL refuse with a trim diff (one line per violation) and write nothing. The operator can pass `--force` to override size or bullet-length refusals; `--force` MAY NOT override a missing-`trigger:` field failure.

#### Scenario: curatecontent promotes a fresh proposal
- **WHEN** an operator invokes `agentsmd curatecontent` (or `catalogue_curatecontent` via an operator client) and selects a category from `prompt-catalogue/proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` does not exist
- **THEN** the surface creates the curated file with the proposed entry as the body and removes the entry from the proposed file

#### Scenario: curatecontent merges with existing curated content
- **WHEN** an operator invokes `agentsmd curatecontent` and selects a category from `proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` already exists
- **THEN** the surface reads both files, identifies semantically overlapping rules, deduplicates (≤30 char edit distance), applies the length-discipline trim rule, and writes the merged result to the curated file. The proposed entry is removed from the proposed file. The surface reports `merged 2 entries` (or the actual count) in its result.

#### Scenario: curatecontent refuses merged file over the per-category cap
- **WHEN** the merged curated file would exceed the 100-line per-category cap
- **THEN** the surface refuses with `curatecontent: refused — merged would be <line-count> lines (cap 100)` followed by a `Suggested fix:` line listing which bullets to drop. The proposed file is unchanged.

#### Scenario: curatecontent refuses bullet-length violation
- **WHEN** the merged curated file would contain a bullet >200 chars
- **THEN** the surface refuses with `curatecontent: refused — bullet <n> exceeds 200 chars in merged output` and a `Suggested fix:` line showing how the bullet would split at the first sentence boundary. The proposed file is unchanged.

#### Scenario: curatecontent --force override
- **WHEN** the operator has read the trim diff and chooses to accept the size violation
- **AND** invokes `agentsmd curatecontent --force` (or `catalogue_curatecontent` with a force flag)
- **THEN** the surface proceeds with the merge despite the violation and records `curatecontent: --force applied, accepted <violation>` in the result. The proposed file is removed.

#### Scenario: curatecontent cannot --force past missing trigger
- **WHEN** the merged file's YAML frontmatter is missing `trigger:`
- **AND** the operator invokes `agentsmd curatecontent --force` or `catalogue_curatecontent` with force
- **THEN** the surface still refuses with `curatecontent: refused — missing trigger: field is non-overridable; --force cannot resolve it` and writes nothing.

#### Scenario: curatecontent enforces length discipline on merge
- **WHEN** the merged result would exceed the 100-line per-category cap
- **THEN** the surface refuses with `curatecontent: refused — merged would be <line-count> lines (cap 100)` followed by a `Suggested fix:` line. Operator passes `--force` to override and accept the over-cap merge. This supersedes the previous soft-trim behaviour; soft-trim is no longer performed.

#### Scenario: Project skill is blocked from curatecontent
- **WHEN** a project skill attempts to call `catalogue_curatecontent`
- **THEN** the MCP server refuses with `error: curatecontent is restricted to operators; use agentsmd curatecontent in the master repo`

### Requirement: addcategory proposes a new category with a starter body
The `catalogue_addcategory` MCP tool and the `agentsmd addcategory` CLI command SHALL create `prompt-catalogue/proposed/<new-category>.md` in the master repo with a setup consisting of: a YAML frontmatter block (built from the supplied `name` and `trigger`), and the supplied `body` content as the starting body, after the same pre-trim pass that `addcontent` runs (dedupe against proposed files ONLY — there is no curated file yet — trim verbose trailers, split bullets >200 chars at sentence boundary). `body` is REQUIRED; empty/whitespace-only `body` is rejected. The surface MUST NOT create anything in `prompt-catalogue/curated/`. The surface reports the suggested file path and trigger rule plus any trim-pass log in its result.

#### Scenario: addcategory creates a proposed entry with body
- **WHEN** a caller invokes `catalogue_addcategory` or `agentsmd addcategory` with name `new-language`, trigger `*.go files present`, and non-empty body
- **THEN** `prompt-catalogue/proposed/new-language.md` is created with title derived from the first sentence of body, trigger matching Go files, and the supplied body as the seed content after pre-trim. The result reports the new proposed file path, trigger rule, and any trim-pass log.

#### Scenario: addcategory rejects missing body
- **WHEN** a caller invokes `catalogue_addcategory` or `agentsmd addcategory` with name `new-language`, trigger `*.go files present`, and absent or empty body
- **THEN** the surface refuses with `error: --body is required (D8 + spec). Re-run with at least a one-sentence starter body so the operator has something to refine.` and writes nothing

#### Scenario: addcategory refuses collision with existing curated category
- **WHEN** a caller invokes `catalogue_addcategory` or `agentsmd addcategory` with name `python-project` and `prompt-catalogue/curated/python-project.md` already exists
- **THEN** the surface refuses with `error: category already in curated; use curatecontent to refine the existing curated entry`

### Requirement: curatecategory accepts a proposed category into curated with remap
The `catalogue_curatecategory` MCP tool (operator only) and the `agentsmd curatecategory` CLI command SHALL promote a `prompt-catalogue/proposed/<category>.md` entry to `prompt-catalogue/curated/<category>.md` in the master repo. After promotion, the resulting curated file is checked against the same contract as `curatecontent`: ≤100 lines per file, ≤200 chars per bullet, mandatory `trigger:` field. **Refusal profile.** If any cap is violated, the surface refuses with a trim diff and writes nothing; the operator passes `--force` to override size violations only. The remap-candidates behaviour from before is preserved.

#### Scenario: curatecategory promotes a new category with no remap candidates
- **WHEN** an operator invokes `agentsmd curatecategory` (or `catalogue_curatecategory` via an operator client) selecting a proposed entry
- **AND** no other proposed entries share the trigger-evidence
- **THEN** the surface creates `prompt-catalogue/curated/<category>.md` with the proposed content after cap verification and clears the proposed entry

#### Scenario: curatecategory surfaces remap candidates for operator validation
- **WHEN** the proposed entry creates a category that other proposed entries could be remapped to
- **THEN** the surface lists them as `remap candidates: <other-category-1>, <other-category-2>` and waits for the operator to confirm each remap explicitly

#### Scenario: curatecategory refuses over-cap result
- **WHEN** after promotion the curated file would exceed 100 lines or any bullet would exceed 200 chars
- **THEN** the surface refuses with the same shape as `curatecontent`'s refusal (trim diff with `Suggested fix:` lines), and writes nothing. Operator passes `--force` to override size and bullet-length; `--force` cannot override a missing-`trigger:` field.

#### Scenario: Project skill is blocked from curatecategory
- **WHEN** a project skill attempts to call `catalogue_curatecategory`
- **THEN** the MCP server refuses with `error: curatecategory is restricted to operators; use agentsmd curatecategory in the master repo`

### Requirement: Isolation contract — update-agents MUST NOT read proposed
The workflow `/update-agents` (driven by the `agents-md-generation` capability) MUST enumerate ONLY the curated categories returned by the MCP server via `catalogue://categories`. The workflow MUST NOT list, read, parse, or splice content from any proposed catalogue resource. The isolation is documented in the workflow's SKILL.md and is enforced by the MCP server (proposed resources are readable but not spliced by the skill).

#### Scenario: Isolation upheld by skill review
- **WHEN** a maintainer changes the `/update-agents` SKILL.md
- **AND** the diff introduces any reference to `catalogue://proposed/` or `prompt-catalogue/proposed/`
- **THEN** the OpenSpec change review SHALL reject the change as a guardrail violation, citing this requirement

#### Scenario: Hard-skill guardrail documented
- **WHEN** a maintainer or reviewer inspects the top of `.claude/skills/update-agents/SKILL.md`
- **THEN** the file's first sentence declares the isolation rule: this workflow reads only curated category bodies via `catalogue://curated/<category>` and never uses proposed resources for splicing

### Requirement: Self-additions from workflow execution MUST route through refresh-agents-content
When `/update-agents` or any other workflow in this repo identifies a rule that should be added to a consumer-facing AGENTS.md (e.g. the Build Error Feedback Loop rule surfaces during execution, or a `browsecontent` run suggests a new category), the workflow MUST NOT silently write that rule into the master catalogue. For generic rules the workflow MUST surface a `catalogue_addcontent` or `catalogue_addcategory` MCP tool call that the operator can later curate. For project-specific rules the workflow MUST print the rule text locally and not call any MCP tool. This is requirement #7 in operating form.

#### Scenario: Self-addition surfaces as addcontent call
- **WHEN** during execution the workflow identifies a useful new prompt rule that is generic enough for many projects
- **THEN** the workflow reports the candidate as `proposes: catalogue_addcontent(category="<cat>", body="<text>")` and does NOT auto-write

#### Scenario: Self-addition surfaces as addcategory call
- **WHEN** during execution the workflow identifies a new generic category of prompt that no curated entry covers
- **THEN** the workflow reports `proposes: catalogue_addcategory(name="<cat>", trigger="<rule>", body="<starter>")` and does NOT auto-write

#### Scenario: Project-specific rule stays local
- **WHEN** during execution the workflow identifies a rule that only applies to the current project
- **THEN** the workflow reports `Project-specific rule: <rule>` and does NOT call any catalogue tool

### Requirement: Catalogue updates bypass OpenSpec
Updates to `prompt-catalogue/` (whether to `curated/` or `proposed/`) in the master repo SHALL NOT route through `openspec new change` / `openspec archive`. The catalogue's only discipline is the proposed → curated operator gate. The OpenSpec lifecycle continues to govern changes to the workflow code, the MCP server, and the operator CLI.

#### Scenario: Catalogue write does not stage OpenSpec change
- **WHEN** the operator runs `agentsmd addcontent` or a project skill calls `catalogue_addcontent` and the action writes to `prompt-catalogue/proposed/`
- **THEN** no `openspec/changes/<slug>/` directory is created

#### Scenario: Workflow change still requires OpenSpec
- **WHEN** the operator changes any `.claude/skills/update-agents/SKILL.md`, `agentsmd/` source code, or Dockerfile
- **THEN** the change SHALL be staged under `openspec/changes/<slug>/` per the project's standard discipline

### Requirement: build-error-feedback-loop content must direct through catalogue flow
The `prompt-catalogue/curated/build-error-feedback-loop.md` entry's body MUST direct the operator through the catalogue flow for generic rules (`agentsmd addcontent` / `agentsmd addcategory` / `agentsmd curatecontent` / `agentsmd curatecategory` in the master repo, or `catalogue_addcontent` / `catalogue_addcategory` from a project skill), and through the project's own `AGENTS.md` for project-specific rules. It MUST include an explicit Never list forbidding direct edits to `AGENTS.md` for generic rules, direct edits to `prompt-catalogue/curated/` in the master repo, and any skill file's body. Specifying what to put in AGENTS.md as a generic rule, the curated folder, or the SKILL.md is forbidden; the entry routes through the catalogue flow only. Project-specific rules are explicitly allowed to be pasted into the project's own `AGENTS.md`.

#### Scenario: build-error-feedback-loop redirects mistakes through addcontent
- **WHEN** a maintainer reads `prompt-catalogue/curated/build-error-feedback-loop.md`
- **THEN** the entry's first imperative line for generic rules is to invoke `catalogue_addcontent` (project skill) or `agentsmd addcontent` (operator) for an existing category, or `catalogue_addcategory` / `agentsmd addcategory` for a new category. The entry does NOT instruct the operator to edit `AGENTS.md` for generic rules, `curated/`, or any skill file directly.

#### Scenario: build-error-feedback-loop allows project-specific rules locally
- **WHEN** a maintainer reads `prompt-catalogue/curated/build-error-feedback-loop.md`
- **THEN** the entry explicitly states that project-specific rules (e.g. a build error unique to this repo) can be pasted directly into the project's own `AGENTS.md` and do not belong in the central catalogue

#### Scenario: build-error-feedback-loop carries an explicit Never list
- **WHEN** a maintainer reads `prompt-catalogue/curated/build-error-feedback-loop.md`
- **THEN** the entry contains explicit Never statements covering: hand-edit a project's `AGENTS.md` outside `/update-agents` for generic rules; hand-edit `prompt-catalogue/curated/*.md` outside `agentsmd curatecontent`/`curatecategory`; embed consumer-facing prompt bodies in `.claude/skills/<name>/SKILL.md`.

### Requirement: Catalogue self-discipline rules and pre-trim contract
The catalogue's mechanical hygiene is governed by four rules. Every `catalogue_addcontent`, `catalogue_addcategory`, `agentsmd addcontent`, and `agentsmd addcategory` write action SHALL honour these rules. Operators cannot opt out of dedupe or bullet-length caps; the trim-tails phase is opt-out per call on the CLI (and surfaced as a flag for the MCP tools).

- Per-category file budget: ≤100 lines (D11).
- Per-bullet length cap: ≤200 chars; over-length bullets split at the first sentence boundary, halves stay separate unless folded by dedupe.
- Dedupe: any new bullet whose edit distance against an existing curated or proposed bullet in the same category is ≤30 chars is dropped as a duplicate.
- Frontmatter: every curated entry MUST carry `title:` AND `trigger:`; absence is a non-overridable contract violation; `--force` cannot resolve it.

#### Scenario: Dedupe drops near-duplicate bullets
- **WHEN** a caller supplies a bullet whose edit-distance against an existing curated bullet in the same category is ≤30 chars
- **THEN** the surface drops the duplicate and reports `addcontent: dedupe <n> bullets vs curated` (or the analogous `curatecontent`/`addcategory` log line)

#### Scenario: Split-at-sentence for over-length bullets
- **WHEN** a caller supplies a bullet >200 chars
- **THEN** the surface splits at the first sentence boundary. Either half >200 chars fails the action with `bullet too long (≥200 chars after split)`.

#### Scenario: Opt-out flag documented
- **WHEN** the operator passes `--no-trim-tails` to `agentsmd addcontent` or `agentsmd addcategory` (or the equivalent MCP tool flag)
- **THEN** the trim-tails phase is skipped and the supplied body is written verbatim (subject to dedupe and length caps). The result records `addcontent: --no-trim-tails applied`.

### Requirement: Catalog self-discipline scan at /update-agents time
Every invocation of `/update-agents` (whose capability is `agents-md-generation`) SHALL read the central catalogue via the MCP server after the splice pass and emit a `Catalog self-discipline check:` section in the consumer's completion summary. The scan is read-only; it does NOT refuse the `/update-agents` invocation. Findings per file:

- `ok` — all four rules pass.
- `<n> lines (cap 100)` — over the per-category cap (file over 100 lines).
- `bullet <i> exceeds 200 chars (n chars)` — over-length bullet.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category dedupe candidate.
- `missing trigger:` — HARD finding, named in the summary as a contract violation.

#### Scenario: Self-discipline check surfaces findings
- **WHEN** a curated file exceeds 100 lines or contains an over-length bullet
- **THEN** the `/update-agents` completion summary has a `Catalog self-discipline check:` section listing each curated file with its findings. The summary still reports the splice outcome; the scan is non-blocking.

#### Scenario: Self-discipline check flags missing trigger field
- **WHEN** a curated file lacks the `trigger:` field
- **THEN** the file is flagged in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is named in the summary; the operator is expected to invoke `agentsmd curatecontent <category>` in the master repo to repair the file.

## ADDED Requirements

### Requirement: Catalogue lives only in the AgentsMDGenerator master repo
The catalogue SHALL NOT be embedded in or copied to consumer projects. The only canonical copy is the `prompt-catalogue/` directory in the AgentsMDGenerator master repo. The MCP server serves this directory. Consumer projects read from the server and never host a local copy.

#### Scenario: Master repo contains the catalogue
- **WHEN** the operator inspects the AgentsMDGenerator master repo
- **THEN** `prompt-catalogue/curated/` and `prompt-catalogue/proposed/` exist and are the only canonical catalogue locations

#### Scenario: Consumer project does not contain the catalogue
- **WHEN** the operator inspects a consumer project after running `/update-agents`
- **THEN** there is no `prompt-catalogue/` directory, and the generated AGENTS.md does not depend on one

### Requirement: MCP curation tools are restricted to operators
The MCP tools `catalogue_curatecontent` and `catalogue_curatecategory` SHALL require an operator credential or transport origin. When called by a project skill, the MCP server SHALL refuse with an explicit error. The `agentsmd` CLI in the master repo is the primary operator surface for curation.

#### Scenario: Operator curates via CLI
- **WHEN** the operator runs `agentsmd curatecontent python-project` in the master repo
- **THEN** the command succeeds and promotes the proposed entry to curated

#### Scenario: Project skill is blocked from curation tools
- **WHEN** a project skill calls `catalogue_curatecontent` or `catalogue_curatecategory`
- **THEN** the MCP server returns `error: curation tools are restricted to operators` and writes nothing

### Requirement: Project skill can propose to the catalogue
The MCP tools `catalogue_addcontent` and `catalogue_addcategory` SHALL be available to the project skill. They write only to `prompt-catalogue/proposed/` in the master repo. This is the only way a project agent may affect the catalogue.

#### Scenario: Project proposes a generic bullet
- **WHEN** a project skill calls `catalogue_addcontent(category="python-project", body="...")`
- **THEN** the MCP server appends the trimmed body to `prompt-catalogue/proposed/python-project.md` in the master repo and returns success

#### Scenario: Project proposes a new category
- **WHEN** a project skill calls `catalogue_addcategory(name="go-project", trigger="*.go files present", body="...")`
- **THEN** the MCP server creates `prompt-catalogue/proposed/go-project.md` in the master repo and returns the file path
