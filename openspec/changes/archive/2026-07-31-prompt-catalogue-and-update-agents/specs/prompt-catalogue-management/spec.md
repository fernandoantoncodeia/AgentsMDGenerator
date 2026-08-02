# prompt-catalogue-management Specification

## Purpose
Govern the operator-curated prompt catalogue that `/update-agents` reads and `/refresh-agents-content` manages. The catalogue is the single source for consumer-facing prompts (a hard requirement — see requirement #7 of the change). All catalogue updates flow through the proposed → curated gate.

## ADDED Requirements

### Requirement: Catalogue folder structure and invariants
The catalogue SHALL live at `prompt-catalogue/` at the repo root, with two subfolders: `curated/` and `proposed/`. Both SHALL contain one markdown file per category. The filename (without `.md` extension) is the category identifier. Categories use kebab-case. A category MAY exist in both folders simultaneously — that signals the operator an item is awaiting curation against an already-curated entry.

#### Scenario: Curated folder has one file per category
- **WHEN** the operator inspects `prompt-catalogue/curated/`
- **THEN** each file is named `<category>.md` and only one entry per category identifier lives there

#### Scenario: Proposed folder is the operator queue
- **WHEN** the operator inspects `prompt-catalogue/proposed/`
- **THEN** each file is named `<category>.md`; entries there have not yet been reviewed and promulgated into curated output

#### Scenario: Same category in both folders
- **WHEN** `<category>.md` exists in both `curated/` and `proposed/`
- **THEN** the operator sees two entries for the same category: the in-use curated version and the draft pending review. `curatecontent` resolves this.

### Requirement: Category file format
Each `<category>.md` file MUST carry YAML frontmatter with at least `title:` and `trigger:` fields. The body is the prompt text. The `title:` becomes the AGENTS.md section heading when spliced. The `trigger:` is a deterministic expression against a project scan. Optionally `trigger-confidence: heuristic` flags a non-deterministic trigger; the workflow surfaces heuristic matches in the completion summary rather than auto-splicing.

#### Scenario: Valid frontmatter parses
- **WHEN** a file's YAML frontmatter contains `title:` and `trigger:`
- **THEN** the workflow reads both fields and uses them in the splice decision

#### Scenario: Missing required frontmatter
- **WHEN** a file is missing `title:` or `trigger:`
- **THEN** the workflow reports the file as malformed in the completion summary and skips it

### Requirement: addcontent appends a proposed entry to the catalogue
The `/refresh-agents-content addcontent` action SHALL append a new entry to `prompt-catalogue/proposed/<category>.md`. The body of the entry is the prompt text supplied by the operator. If the proposed file already exists, the action appends another entry to that file; it MUST NOT silently overwrite. If `<category>` is not specified, the action rejects the call and asks the operator which category to map to.

#### Scenario: addcontent to a new proposed file
- **WHEN** the operator invokes `/refresh-agents-content addcontent --category shell-tooling --body "..."`
- **AND** `prompt-catalogue/proposed/shell-tooling.md` does not exist
- **THEN** the action creates the file with the supplied body and writes a YAML frontmatter header with the operator-supplied title (or a default generated from the category name)

#### Scenario: addcontent to an existing proposed file
- **WHEN** `prompt-catalogue/proposed/shell-tooling.md` already exists
- **AND** the operator invokes `/refresh-agents-content addcontent --category shell-tooling --body "..."`
- **THEN** the action appends the new entry with separator (e.g. `---` between entries) so multiple proposed items can coexist in one file

#### Scenario: addcontent rejects missing category
- **WHEN** the operator invokes `/refresh-agents-content addcontent` without `--category`
- **THEN** the action reports `error: --category is required` and writes nothing

### Requirement: curatecontent promotes one proposed entry to curated, merge-and-simplify
The `/refresh-agents-content curatecontent` action SHALL move one specific proposed entry to `prompt-catalogue/curated/<category>.md`. If any existing curated entry shares the same category, the action MUST perform a merge: identify overlap with the proposed entry, deduplicate, and apply the workflow's own length-discipline rule (target 30-50 lines, soft cap 150 lines, hard cap 32 KiB). The proposed entry MUST be removed from `proposed/<category>.md` after successful curation.

#### Scenario: curatecontent promotes a fresh proposal
- **WHEN** the operator invokes `/refresh-agents-content curatecontent` and selects an entry from `prompt-catalogue/proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` does not exist
- **THEN** the action creates the curated file with the proposed entry as the body and removes the entry from the proposed file

#### Scenario: curatecontent merges with existing curated content
- **WHEN** the operator invokes `/refresh-agents-content curatecontent` and selects an entry from `proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` already exists
- **THEN** the action reads both files, identifies semantically overlapping rules, deduplicates, applies the workflow's length-discipline trim rule, and writes the merged result to the curated file. The proposed entry is removed from the proposed file. The action reports `merged 2 entries` (or the actual count) in its completion summary.

#### Scenario: curatecontent enforces length discipline on merge
- **WHEN** the merged result would exceed the 150-line soft cap
- **THEN** the action trims the merged content to fit, citing the workflow's own sourced principle on length discipline in its completion summary

### Requirement: addcategory proposes a new category with a starter body
The `/refresh-agents-content addcategory` action SHALL create `prompt-catalogue/proposed/<new-category>.md` with a setup consisting of: a YAML frontmatter block (built from the operator-supplied `--name` and `--trigger`), the operator-supplied `--body` content as the starting body, and a trailing note that the operator should refine the body before invoking `curatecategory`. The action SHALL reject calls that omit `--body`; an empty or whitespace-only `--body` argument also fails validation. The action MUST NOT create anything in `prompt-catalogue/curated/`; new categories start in proposed and require curation. The action reports the suggestion in its completion summary.

#### Scenario: addcategory creates a proposed entry with body
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name new-language --trigger "*.go files present" --body "<starter content>"`
- **THEN** `prompt-catalogue/proposed/new-language.md` is created with title `New Language`, trigger matching Go files, and the supplied body as the seed content. The completion summary reports the new proposed file path and trigger rule.

#### Scenario: addcategory rejects missing body
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name new-language --trigger "*.go files present"`
- **AND** `--body` is absent or empty
- **THEN** the action refuses with `error: --body is required (a non-empty starter content) so the proposed entry is reviewable` and writes nothing

#### Scenario: addcategory refuses collision with existing curated category
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name python-project` and `prompt-catalogue/curated/python-project.md` already exists
- **THEN** the action refuses with `error: category already in curated; use curatecontent to refine the existing curated entry`

### Requirement: curatecategory accepts a proposed category into curated with remap
The `/refresh-agents-content curatecategory` action SHALL promote a `prompt-catalogue/proposed/<category>.md` entry to `prompt-catalogue/curated/<category>.md`. If other proposed entries appear to map semantically to this new category (matching by name keyword or by overlap in body content), the action MUST surface them as remapping candidates and SHALL NOT auto-remap. The operator must invoke each remap explicitly. After curation, the proposed file is renamed or emptied as appropriate.

#### Scenario: curatecategory promotes a new category with no remap candidates
- **WHEN** the operator invokes `/refresh-agents-content curatecategory` selecting a proposed entry
- **AND** no other proposed entries share the trigger-evidence
- **THEN** the action creates `prompt-catalogue/curated/<category>.md` with the proposed content and clears the proposed entry

#### Scenario: curatecategory surfaces remap candidates for operator validation
- **WHEN** the proposed entry creates a category that other proposed entries could be remapped to
- **THEN** the action lists them as `remap candidates: <other-category-1>, <other-category-2>` and waits for the operator to confirm each remap explicitly

### Requirement: Isolation contract — update-agents MUST NOT read proposed
The workflow `/update-agents` (driven by the `agents-md-generation` capability) MUST enumerate ONLY `prompt-catalogue/curated/*.md`. The workflow MUST NOT list, read, parse, or splice content from any file under `prompt-catalogue/proposed/`. The isolation is documented in the workflow's SKILL.md (top-of-file guardrail + guardrails section) and is enforced by operator review of skill changes per the OpenSpec lifecycle.

#### Scenario: Isolation upheld by skill review
- **WHEN** a maintainer changes the `/update-agents` SKILL.md
- **AND** the diff introduces any reference to `prompt-catalogue/proposed/`
- **THEN** the OpenSpec change review SHALL reject the change as a guardrail violation, citing this requirement

#### Scenario: Hard-skill guardrail documented
- **WHEN** a maintainer or reviewer inspects the top of `.claude/skills/update-agents/SKILL.md`
- **THEN** the file's first sentence declares the isolation rule: this workflow reads only `prompt-catalogue/curated/`, never `prompt-catalogue/proposed/`

### Requirement: Self-additions from workflow execution MUST route through refresh-agents-content
When `/update-agents` or any other workflow in this repo identifies a rule that should be added to a consumer-facing AGENTS.md (e.g. the Build Error Feedback Loop rule surfaces during execution, or a `browsecontent` run suggests a new category), the workflow MUST NOT silently write that rule into the catalogue. The workflow MUST surface a `/refresh-agents-content addcontent` or `/refresh-agents-content addcategory` invocation that the operator can run directly. This is requirement #7 in operating form.

#### Scenario: Self-addition surfaces as addcontent call
- **WHEN** during execution the workflow identifies a useful new prompt rule that should land in the consumer AGENTS.md
- **THEN** the workflow reports the candidate as `proposes: /refresh-agents-content addcontent --category <cat> --body <text>` and does NOT auto-write

#### Scenario: Self-addition surfaces as addcategory call
- **WHEN** during execution the workflow identifies a new category of prompt that no curated entry covers
- **THEN** the workflow reports `proposes: /refresh-agents-content addcategory --name <cat> --trigger <rule>` and does NOT auto-write

### Requirement: Catalogue updates bypass OpenSpec
Updates to `prompt-catalogue/` (whether to `curated/` or `proposed/`) SHALL NOT route through `openspec new change` / `openspec archive`. The catalogue's only discipline is the proposed → curated operator gate. The OpenSpec lifecycle continues to govern changes to the workflow itself (commands, skills, this synced spec).

#### Scenario: Catalogue write does not stage OpenSpec change
- **WHEN** the operator runs `/refresh-agents-content addcontent` and the action writes to `prompt-catalogue/proposed/`
- **THEN** no `openspec/changes/<slug>/` directory is created

#### Scenario: Workflow change still requires OpenSpec
- **WHEN** the operator changes any `.claude/skills/update-agents/SKILL.md` or `.claude/skills/refresh-agents-content/SKILL.md` content
- **THEN** the change SHALL be staged under `openspec/changes/<slug>/` per the project's standard discipline
