# AgentsMDGenerator

OpenSpec workflow bundle. Ships `.claude/commands/<name>.md` plus a paired `.claude/skills/<name>/SKILL.md`; mirror the same shape in `.factory/` when a workflow targets both. The repo now also hosts the `agentsmd` Python package: the MCP server that serves the prompt catalogue and the deterministic operator CLI. Every behavior-affecting edit goes through `openspec/changes/<slug>/` and ships via `openspec archive`. Consumer-facing prompt content lives in `prompt-catalogue/curated/` and is served to consumer projects via MCP; skills stay operational and never carry prompt bodies.

## Commands

- Stage a change: `openspec new change <slug>`
- Author artifacts: `openspec instructions <artifact> --change <slug>` then write them under `openspec/changes/<slug>/`
- Validate: `openspec validate <slug> --strict`
- Inspect: `openspec show <slug> --json --deltas-only`
- Ship: `openspec archive <slug> -y`
- List active changes: `openspec list`
- Check status of one: `openspec status --change <slug> --json`

**Never hand-edit `openspec/specs/`.** Only `openspec archive` writes there.

## Be a colleague

Surface the misconception before editing files. If the user's request rests on a wrong assumption, or you spot a bug adjacent to what was asked, say so. Report outcomes faithfully: if a check did not run, say so; do not manufacture "all green." When something passes, state it plainly. User-facing prose: complete sentences, expand technical terms, no semantic backtracking.

## When adding or changing a workflow or agentsmd capability

Workflows travel in pairs (slash command + skill). Mirror edits across both `.claude/` (and `.factory/` when applicable) inside the same change. The `agentsmd` package and its entry points (`agentsmd`, `agentsmd-server`) follow the same OpenSpec lifecycle: any behavior-affecting change to catalogue reads, writes, triggers, or transports requires an OpenSpec change.

1. `openspec new change <slug>` and write `proposal.md`, `design.md`, `specs/<capability>/spec.md` (with `## ADDED Requirements`, `## MODIFIED Requirements`, or `## REMOVED Requirements`), and `tasks.md` under `openspec/changes/<slug>/`.
2. Spec deltas use `### Requirement: <name>` headings plus `#### Scenario: <name>` blocks with `**WHEN**` / `**THEN**`.
3. Implement the slash command, the skill, and any `agentsmd` code changes. Mirror edits to `.factory/` if the workflow targets both.
4. Done when ALL pass:
   - `openspec validate <slug> --strict` exits 0.
   - `openspec show <slug> --json --deltas-only` lists every requirement you authored.
5. `openspec archive <slug> -y` to ship.

## When the embedded guidance drifts

This repo's AGENTS.md is itself product output. To refresh it against the catalogue, run `/update-agents` against this directory with the MCP server configured: the workflow reads `catalogue://categories` and `catalogue://curated/<category>` from the local `agentsmd-server` and re-emits the file. To re-derive the Sourced Principles from the canonical six-source authority set, run `agentsmd browsecontent` in the master repo; it emits `agentsmd addcontent` / `agentsmd addcategory` commands for catalogue updates and stages an OpenSpec change only for Sourced Principles updates inside the `/update-agents` skill. Do NOT edit AGENTS.md by hand when `/update-agents` would do it for you — exception: a one-line correction is fine if the mistake is purely cosmetic and you re-run `/update-agents` in the same session to verify.

## Fix your own errors

When the user reports a build error caused by something you did, or any mistake pattern you repeated, add a short imperative rule to this file under the most relevant section. One or two sentences stating what to always do or never do. Confirm to the user that this file has been updated.

## When a tool call fails

A tool-call mechanics failure (malformed JSON, rejected params, schema validation error) is not a decision point. Retry with a simpler, safer form. Only stop and ask after two materially different approaches have both failed.
