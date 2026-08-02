# agents-md-generation Specification

## Purpose
TBD - created by archiving change generate-agents-md. Update Purpose after archive.
## Requirements
### Requirement: Workflow generates an AGENTS.md on demand
The `/update-agents` workflow SHALL be invokable from any project root, and SHALL produce an AGENTS.md at the resolved project path. When an optional path argument is supplied, the workflow SHALL write the file at that path (skipping the CLAUDE.md mirror step when the path is outside the consumer repo root); otherwise it SHALL write to the project root. The workflow SHALL act as an MCP client to read the catalogue; the catalogue no longer lives in the project.

#### Scenario: First-time generation in an empty repo
- **WHEN** the user invokes `/update-agents` in a repo with no AGENTS.md and a valid MCP configuration
- **THEN** the workflow creates a new AGENTS.md at the project root containing the mandated baseline section plus the curated catalogue sections whose triggers fire from a scan of the repo, reading those bodies via MCP

#### Scenario: Generation at a specific path
- **WHEN** the user invokes `/update-agents docs/team/AGENTS.md` and MCP is reachable
- **THEN** the workflow creates AGENTS.md at `docs/team/AGENTS.md` and applies the same mandated + curated logic; the CLAUDE.md mirror step reports `mirror skipped` per the mirror requirements

#### Scenario: Generation requires MCP configuration
- **WHEN** the user invokes `/update-agents` and no MCP configuration is present
- **THEN** the workflow refuses with `error: no MCP server configured; create .agentsmd/mcp.json or set AGENTSMD_MCP_URL` and writes nothing

### Requirement: Mandated baseline section is always present
The workflow SHALL always include the "be a colleague" baseline section in every AGENTS.md it produces or updates. The section SHALL convey the collaborator stance (faithful reporting of test outcomes and verification steps, no manufactured green results, accurate rather than defensive status) and the user-facing prose rules (complete sentences, no unexplained jargon, appropriate expansion of technical terms).

#### Scenario: Update mode retains mandated section
- **WHEN** the user re-invokes `/generate-agents` on an existing AGENTS.md that is missing the mandated section
- **THEN** the workflow adds or restores the mandated section before writing the updated file

#### Scenario: Update mode preserves accurate mandated content
- **WHEN** the existing AGENTS.md already contains the mandated "be a colleague" section with content matching best-practices
- **THEN** the workflow SHALL NOT silently rewrite correct content into something false or weaker

### Requirement: Conditional catalog sections are applied only by trigger
The workflow SHALL read category metadata and bodies exclusively through the configured MCP server, using the `catalogue://categories` resource for metadata and `catalogue://curated/<category>` resources for bodies. Each category's `trigger:` field SHALL be evaluated against a deterministic scan of the target repo; the workflow SHALL splice the category into the output only when its trigger fires. The workflow MUST NOT enumerate or read files from a local `prompt-catalogue/` directory. Conditions that match a trigger-equivalent but have no entry in the central catalogue SHALL trigger an auto-add to the master catalogue via `catalogue_addcategory` with the operator later curating via `agentsmd curatecategory` in the master repo.

#### Scenario: Python trigger fires
- **WHEN** the target repo contains Python sources (e.g. `pyproject.toml`, `requirements*.txt`, `setup.py`, `*.py`)
- **THEN** the output AGENTS.md includes the Python-project hints catalog section, reading its body via `catalogue://curated/python-project`

#### Scenario: Windows COM trigger fires
- **WHEN** the target repo contains Windows COM automation code (e.g. pywin32, comtypes, office automation imports)
- **THEN** the output AGENTS.md includes the Windows COM hints catalog section, reading its body via MCP

#### Scenario: OpenSpec trigger fires
- **WHEN** the target repo contains an `openspec/` directory
- **THEN** the output AGENTS.md includes the OpenSpec-driven-changes catalog section, reading its body via MCP

#### Scenario: Self-documentation trigger fires
- **WHEN** the target repo has a documentation or spec system (e.g. README-driven development, ADR directory, docs site config)
- **THEN** the output AGENTS.md includes the self-documentation hints catalog section, reading its body via MCP

#### Scenario: Python curated entry fires
- **WHEN** the target repo contains Python sources AND the MCP server reports `python-project` in `catalogue://categories`
- **THEN** the output AGENTS.md includes the python-project section, fetched from `catalogue://curated/python-project`

#### Scenario: Python trigger matches but no curated entry exists
- **WHEN** the target repo contains Python sources but the MCP server does not list `python-project` in `catalogue://categories`
- **AND** the MCP server does not list `python-project` in `catalogue://proposed-list` either
- **THEN** the workflow auto-emits `catalogue_addcategory(name="python-project", trigger="*.py files present", body="<starter>")` via MCP and reports `Auto-added to proposed catalogue: python-project (matched by: *.py files present)`. The workflow does not splice the proposed entry into AGENTS.md in the same invocation.

#### Scenario: OpenSpec curated entry fires
- **WHEN** the target repo contains an `openspec/` directory AND the MCP server lists `openspec-driven` in `catalogue://categories`
- **THEN** the output AGENTS.md includes the openspec-driven section, fetched via MCP

#### Scenario: Unrelated trigger does not fire
- **WHEN** the target repo contains Go sources and no Python, no OpenSpec, no Windows COM, and no docs system
- **THEN** the output AGENTS.md SHALL NOT include the python-project, openspec-driven, windows-com, or self-documentation sections

#### Scenario: Hard isolation against proposed folder for splice decisions
- **WHEN** the workflow decides what to splice into AGENTS.md
- **THEN** it reads ONLY curated category bodies through the MCP server; it does not list or read any proposed resource or any local `prompt-catalogue/` directory

#### Scenario: Auto-add to proposed is the only way to seed new categories
- **WHEN** the workflow detects a trigger that has no curated coverage
- **THEN** it MUST propose the entry through the MCP server; it MUST NOT write directly to any local or remote `curated/` directory and it MUST NOT splice the proposed entry into AGENTS.md in the same invocation

### Requirement: Update mode reads, evaluates, optimizes, returns updated file
The workflow SHALL operate in update mode whenever an AGENTS.md already exists. It SHALL read the existing file, evaluate it against the embedded principles, ensure the mandated section is present, splice curated categories whose triggers fire, cut verbose or non-imperative content, write the improved file in place, then re-read and trim. After editing, the workflow SHALL report any "applicable but not curated" categories in the completion summary without auto-adding them. If the MCP server is unreachable in update mode, the workflow SHALL preserve the existing AGENTS.md and report the failure.

#### Scenario: Update removes redundant content
- **WHEN** the existing AGENTS.md contains a long prose paragraph explaining a rule
- **THEN** the workflow rewrites the rule as a short, imperative instruction and removes the explanatory paragraph

#### Scenario: Update adds missing trigger-fired section
- **WHEN** the existing AGENTS.md is missing a catalog section whose trigger fires from the repo
- **THEN** the workflow adds that section in the updated file, reading the body via MCP

#### Scenario: Update adds trigger-fired curated section
- **WHEN** the existing AGENTS.md is missing a curated category whose trigger fires from the repo
- **THEN** the workflow adds that section in the updated file, reading the body via MCP

#### Scenario: Update preserves project-specific content
- **WHEN** the existing AGENTS.md contains project-specific rules not present in any curated category or in the mandated baseline
- **THEN** the workflow preserves them in the updated file unchanged

#### Scenario: Update applies trim pass
- **WHEN** the workflow writes the updated AGENTS.md
- **THEN** it re-reads the entire file and removes verbose, redundant, or non-actionable content before reporting completion

#### Scenario: Update fails gracefully when MCP is unreachable
- **WHEN** the existing AGENTS.md is present and the MCP server is unreachable
- **THEN** the workflow leaves the existing AGENTS.md unchanged and reports `error: MCP server unreachable; existing AGENTS.md preserved`

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

### Requirement: Workflow reports what changed and why
When the workflow writes or updates AGENTS.md, it SHALL report a short summary of:
- Whether it created a new file or updated an existing one.
- Which mandated section and which curated categories ended up in the output.
- Which existing rules were trimmed, rewritten, or preserved verbatim.
- Whether the CLAUDE.md mirror state was created / refreshed / already-valid / already-valid symlink / mirror skipped / failed.
- Any "Categories applicable but not present in curated catalogue" listing with the trigger-evidence for each.
- The MCP server endpoint used and, if unreachable, the failure reason.

#### Scenario: Successful generation report
- **WHEN** the workflow completes successfully via MCP
- **THEN** it produces a summary that lists the MCP endpoint, the sections present in the file, the curated categories spliced, the changes applied to existing content, the CLAUDE.md mirror outcome, and any applicable-but-not-curated categories

#### Scenario: Failure report
- **WHEN** the workflow cannot write AGENTS.md (e.g. permission error, invalid path, MCP unreachable)
- **THEN** it reports the failure with the exact cause and does not claim success

#### Scenario: Mirror failure makes partial state explicit
- **WHEN** AGENTS.md was written successfully but the CLAUDE.md mirror step failed
- **THEN** the completion summary names both outcomes: which file succeeded, which failed, and the exact cause of the mirror failure

#### Scenario: Offline failure report
- **WHEN** the MCP server is unreachable
- **THEN** the summary reports the configured endpoint and the exact connection error, and explicitly states whether the existing AGENTS.md was preserved or no file existed

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

### Requirement: One-line CLAUDE.md mirror is always present at the consumer root
The workflow SHALL guarantee that a `CLAUDE.md` file exists at the consumer repo root alongside AGENTS.md after every invocation, in both create and update modes. The mirror SHALL be a regular (non-symlink) text file whose first line, after trimming whitespace, is exactly the literal string `@AGENTS.md` (Claude Code's `@imports` syntax). The mirror SHALL be written at the same resolved consumer root where AGENTS.md is written; if AGENTS.md is written to a non-root path supplied via a `--path`-style argument, the mirror SHALL be skipped and the completion summary SHALL report the skip with the exact reason.

#### Scenario: Mirror created when CLAUDE.md does not exist
- **WHEN** the workflow reaches the mirror step and `CLAUDE.md` does not exist at the consumer root
- **THEN** the workflow creates `CLAUDE.md` whose content is exactly `@AGENTS.md\n` and reports `created at CLAUDE.md`

#### Scenario: Mirror leaves existing valid CLAUDE.md untouched
- **WHEN** `CLAUDE.md` exists at the consumer root and its first line, after trimming whitespace, equals `@AGENTS.md`
- **THEN** the workflow does not modify the file and reports `already-valid at CLAUDE.md`

#### Scenario: Mirror leaves symlink CLAUDE.md untouched
- **WHEN** `CLAUDE.md` at the consumer root is a symbolic link
- **THEN** the workflow does not modify the link, does not chase its target, and reports `already-valid symlink at CLAUDE.md` with the link target in parentheses

#### Scenario: Mirror preserves pre-existing content by prepending
- **WHEN** `CLAUDE.md` exists at the consumer root, is not a symlink, and its first line, after trimming whitespace, is not `@AGENTS.md`
- **THEN** the workflow prepends `@AGENTS.md\n\n` followed by the original file content (preserving every byte), writes the result, and reports `refreshed CLAUDE.md (preserved N existing lines)` where N is the count of non-empty original lines

#### Scenario: Empty or whitespace-only CLAUDE.md is treated as missing
- **WHEN** `CLAUDE.md` exists at the consumer root, is not a symlink, and reads as empty or only whitespace
- **THEN** the workflow replaces its content with `@AGENTS.md\n` and reports `created at CLAUDE.md` (not `refreshed`)

#### Scenario: Mirror skipped when AGENTS.md target is not the consumer root
- **WHEN** the user invokes `/generate-agents` with a path argument that resolves outside the consumer repo root (e.g. `docs/team/AGENTS.md`)
- **THEN** the workflow skips the mirror step and the completion summary reports `mirror skipped — AGENTS.md target <resolved path> is not the consumer root`

#### Scenario: Mirror failure aborts the workflow
- **WHEN** the mirror step raises an exception (permission denied, read-only filesystem, missing parent directory)
- **THEN** the workflow does NOT claim success, the completion summary reports the failure with the exact cause, and any partial state (AGENTS.md written successfully, mirror not written) is named explicitly

### Requirement: Workflow only carries operational content; consumer prompts live in the catalogue
The workflow's SKILL.md SHALL contain only operational content: mandated baseline template, Sourced Principles list, reference source list, mode detection, CLAUDE.md mirror step, completion-summary rules, guardrails. The workflow SHALL NOT embed any consumer-facing prompt body in the SKILL.md or in any other skill file. Consumer-facing prompts live exclusively in `prompt-catalogue/curated/<category>.md`, and any new or refined prompt content lives in `prompt-catalogue/proposed/<category>.md` until curated. Requirement #7 enforces this.

#### Scenario: No consumer prompt body in the skill
- **WHEN** a maintainer inspects any `.claude/skills/update-agents/SKILL.md` (and any sibling skill files of `/update-agents` and `/refresh-agents-content`)
- **THEN** the file contains no imperative rules, trigger rules, or section bodies that are intended to be spliced into a consumer's AGENTS.md — only operational rules describing the workflow's own behavior

#### Scenario: New prompt content routes through proposed catalogue
- **WHEN** the workflow itself surfaces a rule that should land in a consumer's AGENTS.md (e.g. the Build Error Feedback Loop entry that is currently a catalog item, or a self-suggested rule from execution)
- **THEN** the workflow MUST NOT silently write that rule into `prompt-catalogue/curated/`; it MUST direct the operator to `/refresh-agents-content addcontent` so the entry lands in `proposed/<category>.md` for review

### Requirement: Category file format and trigger evaluation
Each category file in the central catalogue MUST carry YAML frontmatter with at least a `title:` and a `trigger:` field. The workflow fetches the body via `catalogue://curated/<category>` and splices it verbatim into AGENTS.md under the `title:` heading. The `trigger:` field MUST be a deterministic, evaluable expression against a project scan (presence/absence of files or directories, or presence of manifest contents). The project skill evaluates the trigger locally; the MCP server does not evaluate triggers. Triggers that cannot be expressed deterministically SHALL carry a `trigger-confidence: heuristic` flag and the workflow SHALL surface such matches in the completion summary rather than auto-splicing.

#### Scenario: Valid category file format
- **WHEN** a category file's frontmatter contains `title:` and `trigger:` fields
- **THEN** the workflow reads the metadata via `catalogue://categories` and uses the title as the section heading and the trigger as the local matcher; the body is fetched via `catalogue://curated/<category>`

#### Scenario: Missing trigger field
- **WHEN** a category file is missing the `trigger:` frontmatter field
- **THEN** the workflow reports the malformed file in the completion summary and skips it

#### Scenario: Heuristic trigger flagged
- **WHEN** a category file carries `trigger-confidence: heuristic`
- **THEN** the workflow surfaces a `heuristic match: <category>` note in the completion summary rather than auto-splicing

#### Scenario: Trigger evaluation stays in the project
- **WHEN** the workflow evaluates a trigger
- **THEN** the evaluation happens in the project skill using only the metadata from `catalogue://categories`; the MCP server does not receive project files or paths for trigger evaluation

### Requirement: Catalog self-discipline scan runs at every /update-agents invocation
After the splice pass, every `/update-agents` invocation SHALL read `catalogue://categories` and, for each curated category, request the body via `catalogue://curated/<category>` to emit a `Catalog self-discipline check:` section in the completion summary. The scan is read-only; it MUST NOT refuse the `/update-agents` invocation. Per curated file, the workflow outputs one of:

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
- **THEN** the file is named in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is flagged; the operator is expected to invoke `agentsmd curatecontent <category>` in the master repo to repair it.

#### Scenario: Self-discipline scan reports clean state
- **WHEN** all curated files pass the four hygiene rules
- **THEN** the completion summary has a `Catalog self-discipline check: all files ok` line. The scan still runs; the absence of findings is itself a positive signal in the consumer report.

#### Scenario: Self-discipline scan runs over MCP
- **WHEN** the workflow performs the self-discipline scan
- **THEN** it reads each curated file body via `catalogue://curated/<category>` and metadata via `catalogue://categories`; it does not read a local `prompt-catalogue/curated/` directory

### Requirement: MCP client configuration and graceful offline failure
The workflow SHALL discover the MCP server from `.agentsmd/mcp.json` at the consumer root, or from the `AGENTSMD_MCP_URL` environment variable, or from a `--mcp-url` command-line argument. If none of these are present, the workflow SHALL refuse to run. If a configuration is present but the server is unreachable, the workflow SHALL fail gracefully: in create mode it writes nothing; in update mode it preserves the existing AGENTS.md; in both cases it reports the exact connection error.

#### Scenario: Configuration from file
- **WHEN** `.agentsmd/mcp.json` exists with a valid `serverUrl` and `transport` field
- **THEN** the workflow connects to that server and uses it for all catalogue reads and writes

#### Scenario: Configuration from environment variable
- **WHEN** `AGENTSMD_MCP_URL` is set to a valid MCP server URL
- **THEN** the workflow uses that URL and treats the transport as SSE unless a `AGENTSMD_MCP_TRANSPORT` env var says otherwise

#### Scenario: Configuration from CLI argument
- **WHEN** the user invokes `/update-agents --mcp-url http://localhost:3000/sse`
- **THEN** the workflow uses that URL for this invocation, overriding any file or env configuration

#### Scenario: Missing configuration
- **WHEN** no configuration is present
- **THEN** the workflow refuses with `error: no MCP server configured; create .agentsmd/mcp.json or set AGENTSMD_MCP_URL` and writes nothing

#### Scenario: Unreachable server in create mode
- **WHEN** the project has no AGENTS.md and the MCP server is unreachable
- **THEN** the workflow writes nothing and reports `error: MCP server unreachable; no AGENTS.md created`

#### Scenario: Unreachable server in update mode
- **WHEN** the project has an existing AGENTS.md and the MCP server is unreachable
- **THEN** the workflow preserves the existing AGENTS.md and reports `error: MCP server unreachable; existing AGENTS.md preserved`

### Requirement: Project-specific rules stay in the project's AGENTS.md
When a rule discovered during `/update-agents` execution is specific to the consumer project (e.g. a build error pattern unique to that repo, a naming convention that only applies to that project), the workflow SHALL NOT propose it to the central catalogue via MCP. It SHALL surface the rule as text that the user can paste into the project's AGENTS.md under a project-specific section. Generic rules SHALL be proposed via `catalogue_addcontent` or `catalogue_addcategory` to the MCP server.

#### Scenario: Project-specific rule is surfaced locally
- **WHEN** the workflow identifies a rule that only applies to the current project
- **THEN** it prints `Project-specific rule (do not send to catalogue): <rule>` and does not call any MCP tool

#### Scenario: Generic rule is proposed to catalogue
- **WHEN** the workflow identifies a generic rule that applies to many projects
- **THEN** it emits the MCP tool call `catalogue_addcontent(category="...", body="...")` or `catalogue_addcategory(name="...", trigger="...", body="...")` for the operator to review and curate

### Requirement: No local catalogue in consumer projects
The workflow SHALL NOT create, read, or write a `prompt-catalogue/` directory in the consumer project. The catalogue is hosted in the master repo only.

#### Scenario: Local catalogue is ignored
- **WHEN** a consumer project still contains a `prompt-catalogue/` directory from a previous version
- **THEN** the workflow does not read it and reports `Ignoring local prompt-catalogue/; use the MCP server instead`

