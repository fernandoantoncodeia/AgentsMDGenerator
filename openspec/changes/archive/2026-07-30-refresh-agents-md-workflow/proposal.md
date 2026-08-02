# Refresh & Source-Anchored Best Practices

## Why

The `/generate-agents` workflow shipped with an embedded best-practices checklist and reference-source list, but the principles were generic and unattributed. Without a runnable refresh path, the embedded guidance will drift as the open-standard ecosystem evolves (new research, new practitioner consensus, deprecated patterns). We need two things: (a) authoritative sourcing — each principle cites the concrete public source it came from — so the workflow's guidance is defensible, and (b) a runnable refresh workflow that re-discovers best practices, diffs them against the embedded guidance, and proposes updates through the OpenSpec change lifecycle. Cadence and invocation are out of scope here — the user explicitly defers that — but the refresh *ability* and *invocation* are in.

## What Changes

- **Source-anchored principles**: the `/generate-agents` skill's best-practices checklist now lists 16 concrete principles, each attributed to one or more of six public sources (AGENTS.md open standard, Builder.io, MorphLLM, blakecrosley, ASDLC.io, BetterClaw). Length discipline (150 lines soft cap / 32 KiB Code hard cap) is now backed by named cross-source evidence including the Princeton agent-runtime study and the Gloaguen et al. 2026 empirical research.
- **New refresh capability**: a separate `/generate-agents-refresh` slash command + `agents-md-refresh` skill that re-fetches the canonical and practitioner sources, diffs the live principles against the embedded ones, and proposes updates through the OpenSpec change lifecycle. Cadence is the user's call — only the *ability* and *invocation* land here.
- **Stay within the project's OpenSpec rule**: refreshing the workflow's own SKILL.md remains a behavior change, so it must travel through `openspec archive`. The refresh workflow proposes; the user approves; the OpenSpec change archives.

## Capabilities

### New Capabilities

- `agents-md-refresh`: a workflow that re-discovers current best practices from a fixed set of public sources and proposes updates to `/generate-agents`'s embedded guidance through the OpenSpec change lifecycle.

### Modified Capabilities

- `agents-md-generation`: the workflow's best-practices checklist is upgraded from a generic list to a 16-item sourced principles list with explicit length discipline. The writing-priority order is updated to match blakecrosley's synthesis. Tool support notes (Claude Code wrapper) are added.

## Impact

- Adds two new files under `.claude/`:
  - `.claude/commands/generate-agents-refresh.md`
  - `.claude/skills/agents-md-refresh/SKILL.md`
- Modifies one existing file (its content is already updated; this change brings the spec in sync):
  - `.claude/skills/generate-agents-md/SKILL.md` — sourced-principles upgrade.
- Proposes cadence / scheduling as a follow-up the user drives.
- No CLAUDE.md / AGENTS.md mirror changes.
