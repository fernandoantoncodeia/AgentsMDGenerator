## Why

Claude Code does not read `AGENTS.md` natively. It picks up the content only when the consumer repo has a `CLAUDE.md` whose first line is `@AGENTS.md` (Claude Code's `@imports` syntax — first hop picks up the file). Today `/generate-agents` only *suggests* this mirror in its completion summary; consumers forget, so most generated AGENTS.md files stay invisible to Claude Code. Move the mirror into the workflow itself so it always exists alongside AGENTS.md.

## What Changes

- Create-mode now writes a one-line `CLAUDE.md` at the consumer repo root whose first line is `@AGENTS.md`, in addition to writing `AGENTS.md`.
- Update-mode now also refreshes `CLAUDE.md`: if it already starts with `@AGENTS.md`, leave it untouched. If it exists with unrelated content, prepend `@AGENTS.md\n\n` so existing content survives. If it does not exist, create with `@AGENTS.md\n`. If it is a symlink, leave it (already acts as the mirror).
- The completion summary moves CLAUDE.md from "Suggestion" to a first-class artifact with its own row (created, refreshed, or already-valid).
- The existing guardrail "Do NOT auto-mirror to CLAUDE.md; offer only" is revoked in favor of the new behavior.

## Capabilities

### New Capabilities
<!-- None. This change modifies an existing capability only. -->

### Modified Capabilities
- `agents-md-generation`: a new requirement enforces the one-line CLAUDE.md mirror in both create and update modes, plus the reporting requirement is updated so the mirror is listed as a written/refreshed artifact (not as a suggestion).

## Impact

- One modified file: `.claude/skills/generate-agents-md/SKILL.md`
  - Create-mode steps add a CLAUDE.md write at the end.
  - Update-mode steps add a CLAUDE.md resolve-and-update step.
  - Completion-summary block adds a CLAUDE.md row.
  - One guardrail removed (the "offer only" line) and replaced with the new mirror logic.
- Consumer repos now always get a `CLAUDE.md` next to `AGENTS.md`. They retain any pre-existing `CLAUDE.md` content; nothing else about their workflow files is touched.
- Existing `openspec/specs/agents-md-generation/spec.md` will receive a `## MODIFIED Requirements` block on archive.
