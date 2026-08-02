## Why

Teams starting a new project, or maintaining one over time, need a high-quality AGENTS.md file that reliably teaches AI coding agents the project's conventions, build/test commands, and guardrails. Writing this by hand is slow, drifts as the project changes, and varies in quality. We need a workflow that can be run at project start to bootstrap AGENTS.md, and re-run any time to read, evaluate, optimize, and return an improved version, drawing on a curated set of public best-practice sources.

## What Changes

- Add a `/generate-agents` slash command (Claude distribution only) that creates or updates an AGENTS.md in the target repo.
- Add a `generate-agents-md` skill that carries the full workflow logic: detection (create vs. update modes), mandated-section enforcement, conditional catalog application, best-practice scoring, and embedded reference sources.
- Encode the "be a colleague" stance (Anthropic guidance: faithful reporting, clear user-facing prose, no manufactured green results) as the single section mandated in every generated AGENTS.md.
- Encode the remaining items from the project maintainer's commonly-used checklist as a conditional catalog whose triggers fire only when relevant to the target project (Python, Windows COM, OpenSpec usage, self-documentation systems, etc.).
- Provide an optional live web refresh path against the reference sources, used only when explicitly requested or when embedded guidance is suspected stale.

## Capabilities

### New Capabilities
- `agents-md-generation`: defines the workflow that produces and maintains a target project's AGENTS.md, including the mandated baseline section and the conditional catalog.

### Modified Capabilities
<!-- None. This change introduces a new capability only. -->

## Impact

- Adds two new files under `.claude/`:
  - `.claude/commands/generate-agents.md`
  - `.claude/skills/generate-agents-md/SKILL.md`
- No existing commands, skills, or specs are modified.
- Synced on archive: `openspec/specs/agents-md-generation/spec.md` will be created from the delta spec.
