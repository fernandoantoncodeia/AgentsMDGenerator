## Why

The current `/generate-agents` hard-codes its conditional catalog (C1-C9) inside the workflow's SKILL.md and embeds no discoverable curated/proposed distinction. Operators have no in-repo place to draft prompts, no operator review gate before new content reaches consumers, and no browsing surface for what is alive vs. awaiting review. The current `/generate-agents-refresh` only touches the generator's own principles, not the project-level prompts. Operators want a single browseable catalogue with promoting-visible per-category separation, two flows (`/update-agents` for the consumer project's AGENTS.md and `/refresh-agents-content` for catalogue management), and curation discipline that keeps operators in control.

## What Changes

- Add a `prompt-catalogue/` folder at the repo root, with `curated/<category>.md` (one markdown file per category; this is what `/update-agents` reads) and `proposed/<category>.md` (one markdown file per category; this is the operator queue, written first by every catalogue update).
- Rename `/generate-agents` to `/update-agents`. First invocation creates AGENTS.md; subsequent invocations refresh the file. When a trigger-equivalent matches the consumer project's scan but no curated category covers it, the workflow auto-emits a `/refresh-agents-content addcategory` invocation that writes a starter entry into `prompt-catalogue/proposed/<derived>.md`. The auto-add is reflected in the completion summary; the operator curates via `curatecategory` later.
- Add the new flow `/refresh-agents-content` with five documented actions: `addcontent`, `curatecontent`, `browsecontent`, `addcategory`, `curatecategory`. `browsecontent` reuses the existing six-source authority set (agents.md open standard + Builder.io + MorphLLM + blakecrosley + ASDLC.io + BetterClaw) and emits `addcontent` calls.
- Enforce hard isolation: `/update-agents` MUST NOT read `prompt-catalogue/proposed/`. The catalogue gates all content through proposed → curated operator review; no live-write bypass.
- Move the existing C1-C9 catalog content out of `.claude/skills/generate-agents-md/SKILL.md` and into `prompt-catalogue/curated/<category>.md` so the SKILL.md stays operational-only.
- Delete the superseded slash commands and skills: `.claude/commands/generate-agents.md`, `.claude/commands/generate-agents-refresh.md`, `.claude/skills/generate-agents-md/`, `.claude/skills/agents-md-refresh/`. The `.claude/commands/opsx/*` siblings are untouched.
- Catalogue updates bypass the OpenSpec lifecycle (they are project content, not workflow behavior); the proposed/curated gate is the only discipline that applies to them.
- Requirement #7 (added in clarification): prompts to add to AGENTS.md MUST only live in the catalogue and be updated from there. The skills contain operational content only — never consumer-facing prompt content. All existing C1-C9 content and any future category content lives in `prompt-catalogue/curated/`.

## Capabilities

### New Capabilities
- `prompt-catalogue-management`: governs the catalogue folder structure, the curated/proposed split, the isolation contract enforced by `/update-agents`, and the lifecycle semantics of the five `/refresh-agents-content` actions (addcontent, curatecontent, browsecontent, addcategory, curatecategory).

### Modified Capabilities
- `agents-md-generation`: the workflow's slash command becomes `/update-agents`; reads only `prompt-catalogue/curated/`; first-call creation + subsequent refresh + missing-applicable-category detection are made explicit; CLAUDE.md mirror behavior already added by `add-claude-md-mirror` is preserved; the catalog content is gone from the skill (per requirement #7).

- `agents-md-refresh`: the workflow's slash command disappears (folded into `/refresh-agents-content browsecontent`); the capability itself stays and now governs the catalogue-side browse behaviour — fetch the six-source authority set, diff against `prompt-catalogue/curated/`, emit `addcontent` calls rather than staging an OpenSpec change.

## Impact

**Files to add:**
- `.claude/commands/update-agents.md` (replaces `generate-agents.md`)
- `.claude/commands/refresh-agents-content.md` (new)
- `.claude/skills/update-agents/SKILL.md` (replaces `generate-agents-md/SKILL.md`)
- `.claude/skills/refresh-agents-content/SKILL.md` (new)
- `prompt-catalogue/curated/` — seeded with the existing C1-C9 promoted to per-category markdown files (e.g. `build-error-feedback-loop.md`, `short-and-imperative.md`, `python-project.md`, `windows-com.md`, `self-documentation.md`, `openspec-driven.md`, `tool-erratic.md`, `openspec-cli.md`, `shell-tooling.md`)
- `prompt-catalogue/proposed/` — empty starter, ready for operator queue

**Files to delete:**
- `.claude/commands/generate-agents.md`
- `.claude/commands/generate-agents-refresh.md`
- `.claude/skills/generate-agents-md/` (entire folder)
- `.claude/skills/agents-md-refresh/` (entire folder)

**Files modified:**
- `openspec/specs/agents-md-generation/spec.md` — receives `## MODIFIED Requirements` for the rename, the catalogue-read model, the missing-category detection, and the catalog-content extraction.
- `openspec/specs/agents-md-refresh/spec.md` — receives `## MODIFIED Requirements` for the new browsecontent semantics and the OpenSpec-bypass.
- `openspec/changes/archive/2026-07-30-generate-agents-md/` — stays as a historical archive; superseded but not deleted.
- `openspec/changes/archive/2026-07-30-refresh-agents-md-workflow/` — stays as a historical archive; its content is now partly superseded.
- `AGENTS.md` (this repo's, generated by the previous archived change) — gets a small update reflecting the new skill names. Generated by `/update-agents` in a follow-up invocation, not edited by hand.
- `.claude/skills/agents-md-refresh/` deletion also triggers archive already done — the new world has no equivalent folder.

**No consumer-project impact** at this snapshot because the catalogue ships with the workflow installation; once archived, every fresh consumer invocation gets the seeded curated catalogue automatically.
