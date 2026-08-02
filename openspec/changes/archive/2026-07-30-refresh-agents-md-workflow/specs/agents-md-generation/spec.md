# agents-md-generation delta spec

## MODIFIED Requirements

### Requirement: Workflow embeds curated best-practices and reference sources
The workflow SHALL embed a curated best-practices checklist and a list of public reference sources inside its skill body. The embedded checklist SHALL consist of source-attributed principles, each citing one or more public sources that established the principle. The embedded reference-source list SHALL be a closed set; adding, removing, or rebranding a source requires a new OpenSpec change. The workflow SHALL NOT perform live web research by default; it SHALL only perform live web refresh when the user explicitly requests it, or when the workflow detects that embedded guidance is likely stale.

#### Scenario: Default run uses embedded guidance
- **WHEN** the user invokes `/generate-agents` without any flag for network refresh
- **THEN** the workflow runs using only the embedded best-practices checklist and reference sources

#### Scenario: User requests live refresh
- **WHEN** the user invokes `/generate-agents --refresh` (or equivalent)
- **THEN** the workflow performs live web search against the embedded reference sources to update its guidance before generating the AGENTS.md

#### Scenario: Staleness heuristic triggers refresh
- **WHEN** the workflow determines embedded guidance is likely stale (e.g. an embedded source URL has changed shape or the codebase is on a much newer toolchain than the embedded references)
- **THEN** the workflow MAY run a live refresh, but SHALL NOT silently do so without reporting the refresh in its completion summary

## ADDED Requirements

### Requirement: Sourced principles list is concrete and citable
The workflow SHALL embed a Sourced Principles list covering, at minimum: command-first instructions; closure-defined completion; show-don't-tell examples; task-organized sections; escalation rules plus a Never list; explicit boundaries; three-tier NEVER/ASK/ALWAYS judgment; Toolchain First; length discipline (start 20-50 lines, ~150-line soft cap, 32 KiB Code hard cap); hand-written beats LLM-generated; file-scoped commands preferred; concrete pointers not lists; good and bad example pairing; project anchor stack with versions; cross-tool portability (Claude Code wrapper or symlink); living documentation updated in same PR as convention changes. Each principle SHALL cite one or more of the six canonical sources by URL inline.

#### Scenario: Each principle has a source citation
- **WHEN** a maintainer or user inspects the workflow's Sourced Principles list
- **THEN** every principle is followed by at least one source URL that established or documented it

#### Scenario: Cross-source convergence
- **WHEN** a principle is established by more than one of the six canonical sources
- **THEN** the citation lists all of them in order of authority (open standard first, then practitioner guides)

#### Scenario: Length discipline backed by named evidence
- **WHEN** the workflow's length-discipline rule (start 20-50 lines, soft cap ~150, hard cap 32 KiB Code) is questioned
- **THEN** the citation surfaces the GitHub Engineering analysis of 2,500+ repositories, the Gloaguen et al. 2026 ETH Zurich empirical study, and the Princeton agent-runtime study as named evidence

### Requirement: Writing-priority order is sourced from research, not invented
The workflow SHALL apply a writing-priority order that prioritizes operations over style: build/test commands first, definition of done second, escalation rules third, task-organized sections fourth, directory scoping for monorepos fifth, style preferences only after the first four are stable. This order SHALL be cited inline as derived from blakecrosley's synthesis and the GitHub Engineering analysis of 2,500+ repositories.

#### Scenario: Create mode drafts in priority order
- **WHEN** `/generate-agents` runs in create mode without an existing AGENTS.md
- **THEN** the workflow drafts sections in this priority order: commands → closure → escalation → task-organized → boundaries; style guidance is added last

#### Scenario: Update mode scores style rules after operational rules
- **WHEN** `/generate-agents` runs in update mode against an existing AGENTS.md
- **THEN** the workflow reports improvements to operational rules (commands, definition of done, escalation) before flagging style-rule trimming
