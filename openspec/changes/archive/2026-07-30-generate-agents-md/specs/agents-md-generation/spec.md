## ADDED Requirements

### Requirement: Workflow generates an AGENTS.md on demand
The `/generate-agents` workflow SHALL be invokable from any project root, and SHALL produce an AGENTS.md at the resolved project path. When an optional path argument is supplied, the workflow SHALL write the file at that path; otherwise it SHALL write to the project root.

#### Scenario: First-time generation in an empty repo
- **WHEN** the user invokes `/generate-agents` in a repo with no AGENTS.md
- **THEN** the workflow creates a new AGENTS.md at the project root containing the mandated baseline section plus any conditional catalog sections whose triggers fire from a scan of the repo

#### Scenario: Generation at a specific path
- **WHEN** the user invokes `/generate-agents docs/team/AGENTS.md`
- **THEN** the workflow creates AGENTS.md at `docs/team/AGENTS.md` and applies the same mandated + conditional logic

### Requirement: Mandated baseline section is always present
The workflow SHALL always include the "be a colleague" baseline section in every AGENTS.md it produces or updates. The section SHALL convey the collaborator stance (faithful reporting of test outcomes and verification steps, no manufactured green results, accurate rather than defensive status) and the user-facing prose rules (complete sentences, no unexplained jargon, appropriate expansion of technical terms).

#### Scenario: Update mode retains mandated section
- **WHEN** the user re-invokes `/generate-agents` on an existing AGENTS.md that is missing the mandated section
- **THEN** the workflow adds or restores the mandated section before writing the updated file

#### Scenario: Update mode preserves accurate mandated content
- **WHEN** the existing AGENTS.md already contains the mandated "be a colleague" section with content matching best-practices
- **THEN** the workflow SHALL NOT silently rewrite correct content into something false or weaker

### Requirement: Conditional catalog sections are applied only by trigger
The workflow SHALL maintain a catalog of commonly-used best-practice sections, each gated by a detection trigger against the target repo. The workflow SHALL include a catalog section in the output only when its trigger fires.

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

#### Scenario: Unrelated trigger does not fire
- **WHEN** the target repo contains Go sources and no Python, no OpenSpec, no Windows COM, and no docs system
- **THEN** the output AGENTS.md SHALL NOT include the Python, Windows COM, OpenSpec, or self-documentation catalog sections (triggers do not fire)

### Requirement: Update mode reads, evaluates, optimizes, returns updated file
The workflow SHALL operate in update mode whenever an AGENTS.md already exists. It SHALL read the existing file, evaluate it against the embedded best-practices checklist, ensure the mandated section is present, apply only the conditional catalog sections whose triggers fire, cut verbose or non-imperative content, and write the improved file in place. After editing, the workflow SHALL re-read the resulting file and trim anything redundant or non-actionable.

#### Scenario: Update removes redundant content
- **WHEN** the existing AGENTS.md contains a long prose paragraph explaining a rule
- **THEN** the workflow rewrites the rule as a short, imperative instruction and removes the explanatory paragraph

#### Scenario: Update adds missing trigger-fired section
- **WHEN** the existing AGENTS.md is missing a catalog section whose trigger fires from the repo
- **THEN** the workflow adds that section in the updated file

#### Scenario: Update preserves project-specific content
- **WHEN** the existing AGENTS.md contains project-specific rules not present in the catalog
- **THEN** the workflow preserves them in the updated file unchanged

#### Scenario: Update applies trim pass
- **WHEN** the workflow writes the updated AGENTS.md
- **THEN** it re-reads the entire file and removes verbose, redundant, or non-actionable content before reporting completion

### Requirement: Workflow embeds curated best-practices and reference sources
The workflow SHALL embed a curated best-practices checklist and a list of public reference sources inside its skill body. The workflow SHALL NOT perform live web research by default; it SHALL only perform live web refresh when the user explicitly requests it, or when the workflow detects that embedded guidance is likely stale.

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
- Which mandated and conditional catalog sections ended up in the output.
- Which existing rules were trimmed, rewritten, or preserved verbatim.
- Whether a live refresh was performed and against which sources.

#### Scenario: Successful generation report
- **WHEN** the workflow completes successfully
- **THEN** it produces a summary that lists the sections present in the file, the changes applied to existing content, and any side effects (e.g. CLAUDE.md mirror suggestion, refresh invocation)

#### Scenario: Failure report
- **WHEN** the workflow cannot write the file (e.g. permission error, invalid path)
- **THEN** it reports the failure with the exact cause and does not claim success
