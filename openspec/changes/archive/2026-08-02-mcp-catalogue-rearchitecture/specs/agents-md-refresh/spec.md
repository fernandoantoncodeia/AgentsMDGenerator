# agents-md-refresh Specification

## Purpose
Operator-only best-practices discovery for the central prompt catalogue. The capability fetches the six canonical public sources, diffs them against the central catalogue and the embedded Sourced Principles, and outputs deterministic `agentsmd` CLI commands or OpenSpec change paths for the operator to act on. It does not write to the catalogue or stage OpenSpec changes automatically.

## MODIFIED Requirements

### Requirement: Refresh workflow re-fetches the canonical source set
The operator-facing `browsecontent` skill (or `agentsmd browsecontent` command) SHALL re-fetch exactly six public sources for diff comparison: the agents.md open standard (`https://agents.md/` and `https://github.com/agentsmd/agents.md`), Builder.io's AGENTS.md guide (`https://www.builder.io/blog/agents-md`), MorphLLM's spec guide (`https://www.morphllm.com/agents-md-guide`), blakecrosley's patterns post (`https://blakecrosley.com/blog/agents-md-patterns`), ASDLC.io's spec (`https://asdlc.io/practices/agents-md-spec/`), and BetterClaw's best practices (`https://www.betterclaw.io/blog/agents-md-best-practices`). Adding, removing, or replacing any of these sources SHALL require a new OpenSpec change to the `agents-md-refresh` capability. Operators may pass repeatable `--source <url>` flags to the same action to fetch additional ad-hoc URLs in the same invocation; the ad-hoc URLs are appended to the canonical list and exist only for the current invocation's fetch + diff cycle. The source fetch MAY be performed through the MCP `catalogue_fetch_sources` tool or by the skill itself; either way, the server does not perform diffing or LLM reasoning.

#### Scenario: Refresh fetches all six sources
- **WHEN** the operator invokes `agentsmd browsecontent` (or the operator skill equivalent)
- **THEN** the action attempts to fetch all six URLs and reports a per-source success or failure with HTTP status

#### Scenario: Refresh accepts ad-hoc sources
- **WHEN** the operator invokes `agentsmd browsecontent --source https://example.com/new-guide --source https://example.com/another`
- **THEN** the action fetches the six canonical URLs AND the two ad-hoc URLs; the diff summary tags each numbered item with the source URL that drove it, distinguishing canonical from ad-hoc

#### Scenario: Refresh aborts on hard source failure
- **WHEN** any of the six sources returns a 4xx or 5xx response
- **THEN** the action reports the failing source(s) with the HTTP status and SHALL NOT propose any catalogue update. Ad-hoc source failures are reported but do not abort the canonical fetch.

#### Scenario: Adding a new source
- **WHEN** a future change wants to add a seventh canonical source to the authority set
- **THEN** it must do so by extending this requirement through a MODIFIED Requirements section in a new OpenSpec change. Ad-hoc `--source` flags cannot replace the canonical set; they are per-invocation only.

#### Scenario: Server fetch tool does not reason
- **WHEN** the action uses `catalogue_fetch_sources` via MCP
- **THEN** the server returns raw HTTP bodies and timestamps; the skill performs the diff, not the server

### Requirement: Refresh produces a structured diff against embedded guidance
The `browsecontent` action SHALL compare freshly-fetched content against two reference surfaces: the `prompt-catalogue/curated/<category>.md` files in the master repo AND the Sourced Principles list plus Writing-priority order embedded in `/update-agents`'s SKILL.md. The diff SHALL be presented as a numbered list of: new principles not present in either surface, refined principles present but materially changed in the live source, deprecated principles no longer supported by live sources, and proposed-curate suggestions (operator's call). The diff SHALL NOT be a unified patch; it SHALL be a readable summary in conversational form. Catalogue diffs in the summary are paired with the exact `agentsmd addcontent` or `agentsmd addcategory` command the operator should run.

#### Scenario: Refresh reports a non-empty diff
- **WHEN** the live sources contain new, refined, or deprecated guidance relative to either reference surface
- **THEN** the workflow prints a numbered list of additions, refinements, and removals, each with the source URL that drives the change, the suggested target surface, and the exact `agentsmd` command to run for catalogue changes

#### Scenario: Refresh reports no diff
- **WHEN** the live sources match both reference surfaces
- **THEN** the workflow reports `no drift detected` with the timestamp and per-source HTTP statuses, and does not propose any command

#### Scenario: Catalogue diff includes actionable command
- **WHEN** the diff suggests a new catalogue entry for `python-project`
- **THEN** the summary prints `Run: agentsmd addcontent python-project --body "..."` (or `agentsmd addcategory ...` for a new category)

### Requirement: Refresh is read-only by default
The `browsecontent` action SHALL NOT mutate any file by default. Its first three steps (fetch, diff, report) SHALL be read-only. Applying any catalogue update SHALL require the operator to invoke `agentsmd addcontent` or `agentsmd addcategory` directly, which writes into `prompt-catalogue/proposed/` (not `curated/`). Promoting content from `proposed/` to `curated/` requires the operator to invoke `agentsmd curatecontent` or `agentsmd curatecategory` explicitly.

#### Scenario: Refresh completes without writing
- **WHEN** the operator invokes `agentsmd browsecontent` and views the diff summary
- **THEN** no files in the catalogue or the SKILL.md have been modified

#### Scenario: User opts out of applying the diff
- **WHEN** the operator reads the diff summary and does not run any `agentsmd` command
- **THEN** the workflow reports `no catalogue update applied` and exits

### Requirement: Refresh proposes updates through OpenSpec
When the operator accepts a proposed Sourced Principles diff, the operator skill SHALL create a new OpenSpec change under `openspec/changes/refresh-agents-md-content-<YYYY-MM-DD>/` with a delta spec that MODIFIES the `agents-md-generation` capability's "Sourced principles list is concrete and citable" requirement. The change SHALL update the SKILL.md in its apply step. The workflow SHALL NOT hand-edit `openspec/specs/`; updating / finalizing the spec happens via the standard `openspec archive` invocation. Catalogue diffs do NOT use the OpenSpec lifecycle — they go through `agentsmd addcontent` / `agentsmd addcategory`.

#### Scenario: Refresh stages an OpenSpec change
- **WHEN** the operator accepts a Sourced Principles diff summary
- **THEN** the workflow creates a new directory `openspec/changes/refresh-agents-md-content-<date>/` with proposal.md, design.md (only if needed), spec delta, and tasks.md drafted for the user to review before apply

#### Scenario: User reviews before archive
- **WHEN** the staged OpenSpec change is created
- **THEN** the workflow reports the absolute path, lists the proposed SKILL.md edits inline, and waits for the user's explicit `openspec archive` invocation (does not auto-archive)

#### Scenario: Out-of-scope sections are not updatable by refresh
- **WHEN** the operator tries to accept an update that touches the Mandated Baseline, Conditional Catalog, or Validation Requirements of `agents-md-generation`
- **THEN** the workflow refuses and points to the OpenSpec rule that those sections require a manual spec change, not a refresh

#### Scenario: Catalogue updates never stage OpenSpec
- **WHEN** the operator accepts a catalogue diff
- **THEN** the workflow prints `agentsmd addcontent ...` or `agentsmd addcategory ...` commands and does NOT create an `openspec/changes/` directory

### Requirement: Refresh never touches the consumer repo's AGENTS.md
The refresh workflow SHALL operate only against the master repo's catalogue (`prompt-catalogue/`), the workflow's SKILL.md, the workflow's command file, and (for Sourced Principles diffs only) the OpenSpec change directory. It SHALL NOT scan, read, or modify any consumer project's AGENTS.md. Re-running `/update-agents` against a consumer project is the only way to apply refreshed guidance to that project.

#### Scenario: Refresh stays in this repo
- **WHEN** the operator invokes `agentsmd browsecontent`
- **THEN** the action's file operations are constrained to `prompt-catalogue/`, `.claude/skills/`, `.claude/commands/`, and for Sourced Principles, `openspec/changes/`. It never reaches any consumer repo.

### Requirement: Refresh reports source-freshness metadata
After every browse run, the workflow SHALL report the per-source last-fresh timestamp (HTTP `Last-Modified` if present, otherwise current fetch time) and the diff summary, so the operator has auditable data when deciding whether to accept.

#### Scenario: Refresh summary includes timestamps
- **WHEN** the workflow finishes
- **THEN** the completion summary lists each fetched source with its last-modified timestamp (when available) and the diff outcome

### Requirement: Refresh emits addcontent calls for catalogue updates instead of OpenSpec staging
When the operator accepts a proposed catalogue diff, the workflow SHALL emit `agentsmd addcontent` or `agentsmd addcategory` commands that append the proposed content into `prompt-catalogue/proposed/<category>.md` in the master repo. The workflow MUST NOT stage an OpenSpec change for catalogue updates; the OpenSpec lifecycle remains reserved for Sourced Principles updates inside the SKILL.md. The operator must copy and run the command manually; the workflow does not auto-execute it.

#### Scenario: Refresh emits an addcontent call for a new catalogue entry
- **WHEN** the operator accepts a proposed catalogue diff
- **THEN** the workflow reports `Run: agentsmd addcontent <cat> --body "<text>"` and the operator runs it; the command appends to `prompt-catalogue/proposed/<category>.md`. NO `openspec new change` is created for catalogue updates.

#### Scenario: Operator previews addcontent before invocation
- **WHEN** the diff summary is presented
- **THEN** the operator can read every suggested `agentsmd` command, edit the body inline, then run it manually. The workflow MUST NOT auto-invoke the command on its own from `browsecontent`.

### Requirement: Refresh reports each surface separately with a clear target label
When the diff has hits both in the catalogue (`prompt-catalogue/curated/` in the master repo) and in the embedded Sourced Principles inside `.claude/skills/update-agents/SKILL.md`, the workflow SHALL mark each numbered item with its target surface (`[catalogue:<category>]` or `[principles:<index>]`) so the operator knows which one the proposed update applies to. The OpenSpec lifecycle still governs Sourced Principles updates; catalogue updates go through `agentsmd` commands.

#### Scenario: Diff hits both surfaces
- **WHEN** the live sources propose a refinement to a Sourced Principle AND a new possible category
- **THEN** the workflow reports them as `[principles:7]` and `[catalogue:python-project]` respectively, with different follow-up actions offered (Sourced Principles through OpenSpec; catalogue through `agentsmd addcontent`)

### Requirement: browsecontent tags self-discipline violations on curated files
When `browsecontent` inspects curated files in the catalogue as part of its diff scan, it SHALL tag each curated file's diff item with `self-discipline violation: <category>` if the curated file fails the catalog self-discipline check (defined in `prompt-catalogue-management` capability, applied at `agents-md-generation` consumer invocation). Curated files that pass the check receive no extra tag. The tag is appended to the existing `[catalogue:<cat>]` tag and is operator-visible. The suggested repair command is `agentsmd curatecontent <category>`.

#### Scenario: Diff tags a self-discipline violation
- **WHEN** `browsecontent` inspects a curated file that exceeds 100 lines or has a missing `trigger:` field
- **THEN** the diff item is tagged `[catalogue:<cat>]` AND `self-discipline violation: <cat>`. Operator sees both labels on the same item.

#### Scenario: Diff does NOT tag files that pass
- **WHEN** `browsecontent` inspects a curated file that passes all four hygiene rules
- **THEN** the diff item receives only the `[catalogue:<cat>]` tag. The `self-discipline violation:` label is reserved exclusively for files that fail the check.

#### Scenario: Tagged item offers curatecontent follow-up
- **WHEN** the diff item is tagged `self-discipline violation: <cat>`
- **THEN** the suggested follow-up is explicitly `Run: agentsmd curatecontent <cat>` (not `agentsmd addcontent`), and the operator-facing summary text reads "operator action: curatecontent <cat> to repair the file before adding new content."

## ADDED Requirements

### Requirement: browsecontent is an operator-only skill
The `agents-md-refresh` capability SHALL NOT be exposed as a project slash command (`/refresh-agents-content`). It SHALL be available only to operators in the AgentsMDGenerator master repo, either as an `agentsmd browsecontent` command or as an operator-only skill invoked from the master repo. Project agents SHALL NOT be able to invoke the six-source crawler or any curation command.

#### Scenario: Operator runs browsecontent in master repo
- **WHEN** the operator runs `agentsmd browsecontent` from the master repo
- **THEN** the action fetches the six sources, diffs, and reports commands

#### Scenario: Project agent cannot invoke browsecontent
- **WHEN** a project agent tries to invoke `/refresh-agents-content` or `agentsmd browsecontent` from a consumer project
- **THEN** the command is not found and the workflow reports `error: browsecontent is an operator-only capability; run it in the AgentsMDGenerator master repo`

### Requirement: browsecontent never writes to the catalogue directly
The `browsecontent` action SHALL NOT call `catalogue_addcontent`, `catalogue_addcategory`, `catalogue_curatecontent`, or `catalogue_curatecategory`. It only emits text commands. The operator must copy and run the commands. This keeps the deterministic CLI as the only write surface for the catalogue.

#### Scenario: browsecontent emits only text
- **WHEN** the operator accepts a catalogue diff
- **THEN** the action prints `Run: agentsmd addcontent ...` but does not execute the tool or modify any file

#### Scenario: No MCP write calls from browsecontent
- **WHEN** tracing the `browsecontent` execution
- **THEN** there are no calls to `catalogue_addcontent`, `catalogue_addcategory`, `catalogue_curatecontent`, or `catalogue_curatecategory`

### Requirement: Discovery rules are classified as generic or project-specific
When the `browsecontent` diff suggests a new rule, it SHALL label it as either `[generic]` or `[project-specific]`. Generic rules are emitted as `agentsmd addcontent`/`agentsmd addcategory` commands. Project-specific rules are emitted as `Paste into your project's AGENTS.md:` text and never sent to the central catalogue.

#### Scenario: Generic rule is emitted as addcontent command
- **WHEN** the diff identifies a generic rule
- **THEN** the summary prints `[generic] Run: agentsmd addcontent <cat> --body "..."`

#### Scenario: Project-specific rule is emitted as local text
- **WHEN** the diff identifies a rule that only applies to a specific project context
- **THEN** the summary prints `[project-specific] Paste into your project's AGENTS.md: <rule>` and does not print an `agentsmd` command
