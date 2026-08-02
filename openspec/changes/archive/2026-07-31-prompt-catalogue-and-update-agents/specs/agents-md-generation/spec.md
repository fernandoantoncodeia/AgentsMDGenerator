# agents-md-generation delta spec

## MODIFIED Requirements

### Requirement: Workflow generates an AGENTS.md on demand
The `/update-agents` workflow SHALL be invokable from any project root, and SHALL produce an AGENTS.md at the resolved project path. When an optional path argument is supplied, the workflow SHALL write the file at that path (skipping the CLAUDE.md mirror step when the path is outside the consumer repo root); otherwise it SHALL write to the project root.

#### Scenario: First-time generation in an empty repo
- **WHEN** the user invokes `/update-agents` in a repo with no AGENTS.md
- **THEN** the workflow creates a new AGENTS.md at the project root containing the mandated baseline section plus the curated catalogue sections whose triggers fire from a scan of the repo

#### Scenario: Generation at a specific path
- **WHEN** the user invokes `/update-agents docs/team/AGENTS.md`
- **THEN** the workflow creates AGENTS.md at `docs/team/AGENTS.md` and applies the same mandated + curated logic; the CLAUDE.md mirror step reports `mirror skipped` per the mirror requirements

### Requirement: Conditional catalog sections are applied only by trigger
The workflow SHALL read category content exclusively from `prompt-catalogue/curated/*.md`. Each category file's `trigger:` frontmatter field SHALL be evaluated against a deterministic scan of the target repo; the workflow SHALL splice the category into the output only when its trigger fires. The workflow MUST NOT read `prompt-catalogue/proposed/` for splicing decisions. Conditions that match a trigger-equivalent but have no entry in `prompt-catalogue/curated/` SHALL trigger an auto-add to `prompt-catalogue/proposed/<derived>.md` via a `/refresh-agents-content addcategory` invocation with the operator later curating via `curatecategory`.

#### Scenario: Python trigger fires
- **WHEN** the target repo contains Python sources (e.g. `pyproject.toml`, `requirements*.txt`, `setup.py`, `*.py`)
- **THEN** the output AGENTS.md includes the Python-project hints catalog section

#### Scenario: Windows COM trigger fires
- **WHEN** the target repo contains Windows COM automation code (e.g. pywin32, comtypes, office automation imports)
- **THEN** the output AGENTS.md includes the Windows COM hints catalog section

#### Scenario: OpenSpec trigger fires
- **WHEN** the target repo contains an `openspec/` directory
- **THEN** the output AGENTS.md includes the OpenSpec-driven-changes catalog section

#### Scenario: Self-documentation trigger fires
- **WHEN** the target repo has a documentation or spec system (e.g. README-driven development, ADR directory, docs site config)
- **THEN** the output AGENTS.md includes the self-documentation hints catalog section

#### Scenario: Python curated entry fires
- **WHEN** the target repo contains Python sources AND `prompt-catalogue/curated/python-project.md` exists
- **THEN** the output AGENTS.md includes the python-project section

#### Scenario: Python trigger matches but no curated entry exists
- **WHEN** the target repo contains Python sources but no `prompt-catalogue/curated/python-project.md` exists
- **AND** no proposed category covers Python either
- **THEN** the workflow auto-emits `/refresh-agents-content addcategory --name python-project --trigger "*.py files present" --body "<starter>"` and writes the placeholder to `prompt-catalogue/proposed/python-project.md`. The completion summary reports `Auto-added to proposed catalogue: python-project (matched by: *.py files present)`.

#### Scenario: OpenSpec curated entry fires
- **WHEN** the target repo contains an `openspec/` directory AND `prompt-catalogue/curated/openspec-driven.md` exists
- **THEN** the output AGENTS.md includes the openspec-driven section

#### Scenario: Unrelated trigger does not fire
- **WHEN** the target repo contains Go sources and no Python, no OpenSpec, no Windows COM, and no docs system
- **THEN** the output AGENTS.md SHALL NOT include the python-project, openspec-driven, windows-com, or self-documentation sections

#### Scenario: Hard isolation against proposed folder for splice decisions
- **WHEN** the workflow decides what to splice into AGENTS.md
- **THEN** it enumerates ONLY files inside `prompt-catalogue/curated/`; files under `prompt-catalogue/proposed/` are not eligible to be spliced regardless of content

#### Scenario: Auto-add to proposed is the only way to seed new categories
- **WHEN** the workflow detects a trigger that has no curated coverage
- **THEN** it MUST write the auto-add into `prompt-catalogue/proposed/`; it MUST NOT write directly into `prompt-catalogue/curated/` and it MUST NOT splice the proposed entry into AGENTS.md in the same invocation

### Requirement: Workflow reports what changed and why
When the workflow writes or updates AGENTS.md, it SHALL report a short summary of:
- Whether it created a new file or updated an existing one.
- Which mandated section and which curated categories ended up in the output.
- Which existing rules were trimmed, rewritten, or preserved verbatim.
- Whether the CLAUDE.md mirror state was created / refreshed / already-valid / already-valid symlink / mirror skipped / failed.
- Any "Categories applicable but not present in curated catalogue" listing with the trigger-evidence for each.

#### Scenario: Successful generation report
- **WHEN** the workflow completes successfully
- **THEN** it produces a summary that lists the sections present in the file, the curated categories spliced, the changes applied to existing content, the CLAUDE.md mirror outcome, and any applicable-but-not-curated categories

#### Scenario: Failure report
- **WHEN** the workflow cannot write AGENTS.md (e.g. permission error, invalid path)
- **THEN** it reports the failure with the exact cause and does not claim success

#### Scenario: Mirror failure makes partial state explicit
- **WHEN** AGENTS.md was written successfully but the CLAUDE.md mirror step failed
- **THEN** the completion summary names both outcomes: which file succeeded, which failed, and the exact cause of the mirror failure

### Requirement: Update mode reads, evaluates, optimizes, returns updated file
The workflow SHALL operate in update mode whenever an AGENTS.md already exists. It SHALL read the existing file, evaluate it against the embedded principles, ensure the mandated section is present, splice curated categories whose triggers fire, cut verbose or non-imperative content, write the improved file in place, then re-read and trim. After editing, the workflow SHALL report any "applicable but not curated" categories in the completion summary without auto-adding them.

#### Scenario: Update removes redundant content
- **WHEN** the existing AGENTS.md contains a long prose paragraph explaining a rule
- **THEN** the workflow rewrites the rule as a short, imperative instruction and removes the explanatory paragraph

#### Scenario: Update adds missing trigger-fired section
- **WHEN** the existing AGENTS.md is missing a catalog section whose trigger fires from the repo
- **THEN** the workflow adds that section in the updated file

#### Scenario: Update adds trigger-fired curated section
- **WHEN** the existing AGENTS.md is missing a curated category whose trigger fires from the repo
- **THEN** the workflow adds that section in the updated file

#### Scenario: Update preserves project-specific content
- **WHEN** the existing AGENTS.md contains project-specific rules not present in any curated category or in the mandated baseline
- **THEN** the workflow preserves them in the updated file unchanged

#### Scenario: Update applies trim pass
- **WHEN** the workflow writes the updated AGENTS.md
- **THEN** it re-reads the entire file and removes verbose, redundant, or non-actionable content before reporting completion

## ADDED Requirements

### Requirement: Workflow only carries operational content; consumer prompts live in the catalogue
The workflow's SKILL.md SHALL contain only operational content: mandated baseline template, Sourced Principles list, reference source list, mode detection, CLAUDE.md mirror step, completion-summary rules, guardrails. The workflow SHALL NOT embed any consumer-facing prompt body in the SKILL.md or in any other skill file. Consumer-facing prompts live exclusively in `prompt-catalogue/curated/<category>.md`, and any new or refined prompt content lives in `prompt-catalogue/proposed/<category>.md` until curated. Requirement #7 enforces this.

#### Scenario: No consumer prompt body in the skill
- **WHEN** a maintainer inspects any `.claude/skills/update-agents/SKILL.md` (and any sibling skill files of `/update-agents` and `/refresh-agents-content`)
- **THEN** the file contains no imperative rules, trigger rules, or section bodies that are intended to be spliced into a consumer's AGENTS.md — only operational rules describing the workflow's own behavior

#### Scenario: New prompt content routes through proposed catalogue
- **WHEN** the workflow itself surfaces a rule that should land in a consumer's AGENTS.md (e.g. the Build Error Feedback Loop entry that is currently a catalog item, or a self-suggested rule from execution)
- **THEN** the workflow MUST NOT silently write that rule into `prompt-catalogue/curated/`; it MUST direct the operator to `/refresh-agents-content addcontent` so the entry lands in `proposed/<category>.md` for review

### Requirement: Category file format and trigger evaluation
Each `prompt-catalogue/curated/<category>.md` file MUST carry YAML frontmatter with at least a `title:` and a `trigger:` field. The body is free-form markdown that the workflow splices verbatim into AGENTS.md under the `title:` heading. The `trigger:` field MUST be a deterministic, evaluable expression against a project scan (presence/absence of files or directories, or presence of manifest contents). Triggers that cannot be expressed deterministically SHALL carry a `trigger-confidence: heuristic` flag and the workflow SHALL surface such matches in the completion summary rather than auto-splicing.

#### Scenario: Valid category file format
- **WHEN** a category file's frontmatter contains `title:` and `trigger:` fields
- **THEN** the workflow reads the file and uses the title as the section heading and the trigger as the matcher

#### Scenario: Missing trigger field
- **WHEN** a category file is missing the `trigger:` frontmatter field
- **THEN** the workflow reports the malformed file in the completion summary and skips it

#### Scenario: Heuristic trigger flagged
- **WHEN** a category file carries `trigger-confidence: heuristic`
- **THEN** the workflow surfaces a `heuristic match: <category>` note in the completion summary rather than auto-splicing
