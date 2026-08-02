# agents-md-refresh Specification

## Purpose
Refresh the `/generate-agents` workflow's embedded best-practices and reference sources against current public guidance, and propose updates through the OpenSpec change lifecycle.

## ADDED Requirements

### Requirement: Refresh workflow re-fetches the canonical source set
The `/generate-agents-refresh` workflow SHALL re-fetch exactly six public sources for diff comparison: the agents.md open standard (`https://agents.md/` and `https://github.com/agentsmd/agents.md`), Builder.io's AGENTS.md guide (`https://www.builder.io/blog/agents-md`), MorphLLM's spec guide (`https://www.morphllm.com/agents-md-guide`), blakecrosley's patterns post (`https://blakecrosley.com/blog/agents-md-patterns`), ASDLC.io's spec (`https://asdlc.io/practices/agents-md-spec/`), and BetterClaw's best practices (`https://www.betterclaw.io/blog/agents-md-best-practices`). Adding, removing, or replacing any of these sources SHALL require a new OpenSpec change to the `agents-md-refresh` capability.

#### Scenario: Refresh fetches all six sources
- **WHEN** the user invokes `/generate-agents-refresh`
- **THEN** the workflow attempts to fetch all six URLs and reports a per-source success or failure

#### Scenario: Refresh aborts on hard source failure
- **WHEN** any of the six sources returns a 4xx or 5xx response
- **THEN** the workflow reports the failing source(s) with the HTTP status and SHALL NOT propose any update

#### Scenario: Adding a new source
- **WHEN** a future change wants to add a seventh source to the authority set
- **THEN** it must do so by extending this requirement through a MODIFIED Requirements section in a new OpenSpec change

### Requirement: Refresh produces a structured diff against embedded guidance
The workflow SHALL compare the freshly-fetched content against the Sourced Principles list and Writing-priority order embedded in `/generate-agents`'s SKILL.md. The diff SHALL be presented as a numbered list of: new principles (not present in the embedded list), refined principles (present but with materially different wording or evidence in the live source), and deprecated principles (live sources no longer support). The diff SHALL NOT be a unified patch; it SHALL be a readable summary in conversational form.

#### Scenario: Refresh reports a non-empty diff
- **WHEN** the live sources contain new, refined, or deprecated guidance relative to the embedded Sourced Principles list
- **THEN** the workflow prints a numbered list of additions, refinements, and removals, each with the source URL that drives the change

#### Scenario: Refresh reports no diff
- **WHEN** the live sources match the embedded Sourced Principles list and Writing-priority order
- **THEN** the workflow reports "no drift detected" with the timestamp and per-source HTTP statuses, and does not propose any change

### Requirement: Refresh is read-only by default
The workflow SHALL NOT mutate any file in the repo by default. Its first three steps (fetch, diff, report) SHALL be read-only. Applying any proposed update SHALL require an explicit user decision in the conversational summary.

#### Scenario: Refresh completes without writing
- **WHEN** the user invokes `/generate-agents-refresh` and views the diff summary
- **THEN** no files in the repo have been modified

#### Scenario: User opts out of applying the diff
- **WHEN** the user reads the diff summary and does not request application
- **THEN** the workflow reports "no update applied" and exits

### Requirement: Refresh proposes updates through OpenSpec
When the user accepts the proposed update, the workflow SHALL create a new OpenSpec change under `openspec/changes/refresh-agents-md-content-<YYYY-MM-DD>/` with a delta spec that MODIFIES the `agents-md-generation` capability's "Sourced principles list is concrete and citable" requirement. The change SHALL update the SKILL.md in its apply step. The workflow SHALL NOT hand-edit `openspec/specs/`; updating / finalizing the spec happens via the standard `openspec archive` invocation.

#### Scenario: Refresh stages an OpenSpec change
- **WHEN** the user accepts the proposed diff summary
- **THEN** the workflow creates a new directory `openspec/changes/refresh-agents-md-content-<date>/` with proposal.md, design.md (only if needed), spec delta, and tasks.md drafted for the user to review before apply

#### Scenario: User reviews before archive
- **WHEN** the staged OpenSpec change is created
- **THEN** the workflow reports the absolute path, lists the proposed SKILL.md edits inline, and waits for the user's explicit `openspec archive` invocation (does not auto-archive)

#### Scenario: Out-of-scope sections are not updatable by refresh
- **WHEN** the user tries to accept an update that touches the Mandated Baseline, Conditional Catalog, or Validation Requirements of `agents-md-generation`
- **THEN** the workflow refuses and points to the OpenSpec rule that those sections require a manual spec change, not a refresh

### Requirement: Refresh never touches the consumer repo's AGENTS.md
The refresh workflow SHALL operate only against this repo's own SKILL.md, command file, and OpenSpec change directory. It SHALL NOT scan, read, or modify any consumer project's AGENTS.md. Re-running `/generate-agents` against a consumer project is the only way to apply refreshed guidance to that project.

#### Scenario: Refresh stays in this repo
- **WHEN** the user invokes `/generate-agents-refresh`
- **THEN** the workflow's file operations are constrained to this repo (`.claude/`, `openspec/changes/`) and never reach any consumer repo

### Requirement: Refresh reports source-freshness metadata
After every run, the workflow SHALL report the per-source last-fresh timestamp (HTTP `Last-Modified` if present, otherwise current fetch time) and the diff summary, so the user has auditable data when deciding whether to accept.

#### Scenario: Refresh summary includes timestamps
- **WHEN** the workflow finishes
- **THEN** the completion summary lists each fetched source with its last-modified timestamp (when available) and the diff outcome
