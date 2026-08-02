# agents-md-refresh delta spec

## MODIFIED Requirements

### Requirement: Refresh workflow re-fetches the canonical source set
The `/refresh-agents-content browsecontent` action SHALL re-fetch exactly six public sources for diff comparison: the agents.md open standard (`https://agents.md/` and `https://github.com/agentsmd/agents.md`), Builder.io's AGENTS.md guide (`https://www.builder.io/blog/agents-md`), MorphLLM's spec guide (`https://www.morphllm.com/agents-md-guide`), blakecrosley's patterns post (`https://blakecrosley.com/blog/agents-md-patterns`), ASDLC.io's spec (`https://asdlc.io/practices/agents-md-spec/`), and BetterClaw's best practices (`https://www.betterclaw.io/blog/agents-md-best-practices`). Adding, removing, or replacing any of these sources SHALL require a new OpenSpec change to the `agents-md-refresh` capability. Operators may pass repeatable `--source <url>` flags to the same action to fetch additional ad-hoc URLs in the same invocation; the ad-hoc URLs are appended to the canonical list and exist only for the current invocation's fetch + diff cycle.

#### Scenario: Refresh fetches all six sources
- **WHEN** the operator invokes `/refresh-agents-content browsecontent`
- **THEN** the action attempts to fetch all six URLs and reports a per-source success or failure with HTTP status

#### Scenario: Refresh accepts ad-hoc sources
- **WHEN** the operator invokes `/refresh-agents-content browsecontent --source https://example.com/new-guide --source https://example.com/another`
- **THEN** the action fetches the six canonical URLs AND the two ad-hoc URLs; the diff summary tags each numbered item with the source URL that drove it, distinguishing canonical from ad-hoc

#### Scenario: Refresh aborts on hard source failure
- **WHEN** any of the six sources returns a 4xx or 5xx response
- **THEN** the action reports the failing source(s) with the HTTP status and SHALL NOT propose any catalogue update. Ad-hoc source failures are reported but do not abort the canonical fetch.

#### Scenario: Adding a new source
- **WHEN** a future change wants to add a seventh canonical source to the authority set
- **THEN** it must do so by extending this requirement through a MODIFIED Requirements section in a new OpenSpec change. Ad-hoc `--source` flags cannot replace the canonical set; they are per-invocation only.

### Requirement: Refresh produces a structured diff against embedded guidance
The `browsecontent` action SHALL compare freshly-fetched content against two reference surfaces: the `prompt-catalogue/curated/<category>.md` files AND the Sourced Principles list plus Writing-priority order embedded in `/update-agents`'s SKILL.md. The diff SHALL be presented as a numbered list of: new principles not present in either surface, refined principles present but materially changed in the live source, deprecated principles no longer supported by live sources, and proposed-curate suggestions (operator's call). The diff SHALL NOT be a unified patch; it SHALL be a readable summary in conversational form.

#### Scenario: Refresh reports a non-empty diff
- **WHEN** the live sources contain new, refined, or deprecated guidance relative to either reference surface
- **THEN** the workflow prints a numbered list of additions, refinements, and removals, each with the source URL that drives the change and the suggested target (catalogue category and frontmatter field, or Sourced Principles index inside the SKILL.md)

#### Scenario: Refresh reports no diff
- **WHEN** the live sources match both reference surfaces
- **THEN** the workflow reports `no drift detected` with the timestamp and per-source HTTP statuses, and does not propose any change

### Requirement: Refresh proposes updates through OpenSpec
When the operator accepts a proposed Sourced Principles diff, the workflow SHALL create a new OpenSpec change under `openspec/changes/refresh-agents-md-content-<YYYY-MM-DD>/` with a delta spec that MODIFIES the `agents-md-generation` capability's "Sourced principles list is concrete and citable" requirement. The change SHALL update the SKILL.md in its apply step. The workflow SHALL NOT hand-edit `openspec/specs/`; updating / finalizing the spec happens via the standard `openspec archive` invocation. Catalogue diffs do NOT use the OpenSpec lifecycle — they go through `addcontent` into `prompt-catalogue/proposed/`.

#### Scenario: Refresh stages an OpenSpec change
- **WHEN** the operator accepts a Sourced Principles diff summary
- **THEN** the workflow creates a new directory `openspec/changes/refresh-agents-md-content-<date>/` with proposal.md, design.md (only if needed), spec delta, and tasks.md drafted for the user to review before apply

#### Scenario: User reviews before archive
- **WHEN** the staged OpenSpec change is created
- **THEN** the workflow reports the absolute path, lists the proposed SKILL.md edits inline, and waits for the user's explicit `openspec archive` invocation (does not auto-archive)

#### Scenario: Out-of-scope sections are not updatable by refresh
- **WHEN** the operator tries to accept an update that touches the Mandated Baseline, Conditional Catalog, or Validation Requirements of `agents-md-generation`
- **THEN** the workflow refuses and points to the OpenSpec rule that those sections require a manual spec change, not a refresh

### Requirement: Refresh is read-only by default
The `browsecontent` action SHALL NOT mutate any file by default. Its first three steps (fetch, diff, report) SHALL be read-only. Applying any catalogue update SHALL require the operator to invoke `addcontent` directly, which writes into `prompt-catalogue/proposed/` (not `curated/`). Promoting content from `proposed/` to `curated/` requires the operator to invoke `curatecontent` explicitly.

#### Scenario: Refresh completes without writing
- **WHEN** the operator invokes `/refresh-agents-content browsecontent` and views the diff summary
- **THEN** no files in the catalogue or the SKILL.md have been modified

#### Scenario: User opts out of applying the diff
- **WHEN** the operator reads the diff summary and does not invoke addcontent or curatecontent
- **THEN** the workflow reports `no catalogue update applied` and exits

### Requirement: Refresh never touches the consumer repo's AGENTS.md
The refresh workflow SHALL operate only against this repo's own catalogue (`prompt-catalogue/`), the workflow's SKILL.md, the workflow's command file, and (for Sourced Principles diffs only) the OpenSpec change directory. It SHALL NOT scan, read, or modify any consumer project's AGENTS.md. Re-running `/update-agents` against a consumer project is the only way to apply refreshed guidance to that project.

#### Scenario: Refresh stays in this repo
- **WHEN** the operator invokes `/refresh-agents-content browsecontent`
- **THEN** the action's file operations are constrained to `prompt-catalogue/`, `.claude/skills/`, `.claude/commands/`, and for Sourced Principles, `openspec/changes/`. It never reaches any consumer repo.

### Requirement: Refresh reports source-freshness metadata
After every browse run, the workflow SHALL report the per-source last-fresh timestamp (HTTP `Last-Modified` if present, otherwise current fetch time) and the diff summary, so the operator has auditable data when deciding whether to accept.

#### Scenario: Refresh summary includes timestamps
- **WHEN** the workflow finishes
- **THEN** the completion summary lists each fetched source with its last-modified timestamp (when available) and the diff outcome

## ADDED Requirements

### Requirement: Refresh emits addcontent calls for catalogue updates instead of OpenSpec staging
When the operator accepts a proposed catalogue diff, the workflow SHALL emit `/refresh-agents-content addcontent` actions that append the proposed content into `prompt-catalogue/proposed/<category>.md`. The workflow MUST NOT stage an OpenSpec change for catalogue updates; the OpenSpec lifecycle remains reserved for Sourced Principles updates inside the SKILL.md.

#### Scenario: Refresh emits an addcontent call for a new catalogue entry
- **WHEN** the operator accepts a proposed catalogue diff
- **THEN** the workflow reports a `/refresh-agents-content addcontent --category <cat> --body <text>` invocation that the operator runs; the call appends to `prompt-catalogue/proposed/<category>.md`. NO `openspec new change` is created for catalogue updates.

#### Scenario: Operator previews addcontent before invocation
- **WHEN** the diff summary is presented
- **THEN** the operator can read every suggested `addcontent` invocation, edit the body inline, then run it manually with `/refresh-agents-content addcontent ...`. The workflow MUST NOT auto-invoke addcontent on its own from `browsecontent`.

### Requirement: Refresh reports each surface separately with a clear target label
When the diff has hits both in the catalogue (`prompt-catalogue/curated/`) and in the embedded Sourced Principles inside `.claude/skills/update-agents/SKILL.md`, the workflow SHALL mark each numbered item with its target surface (`[catalogue:<category>]` or `[principles:<index>]`) so the operator knows which one the proposed update applies to. The OpenSpec lifecycle still governs Sourced Principles updates; catalogue updates go straight into `proposed/`.

#### Scenario: Diff hits both surfaces
- **WHEN** the live sources propose a refinement to a Sourced Principle AND a new possible category
- **THEN** the workflow reports them as `[principles:7]` and `[catalogue:python-project]` respectively, with different follow-up actions offered (Sourced Principles through OpenSpec; catalogue through addcontent)
