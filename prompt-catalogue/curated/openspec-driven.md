---
title: OpenSpec Driven Changes
trigger: openspec/ directory exists at the repo root
---

- Every behavior-affecting change goes through OpenSpec: proposal + delta spec under `openspec/changes/<slug>` then `openspec archive`.
- Check `openspec/specs/` and `openspec/changes/` before starting a change to avoid duplicates and conflicts.
- Never hand-edit `openspec/specs/`. Only `openspec archive` writes there.
- Spec deltas use `### Requirement: <name>` headings with `#### Scenario: <name>` blocks containing `**WHEN**` and `**THEN**` clauses.
- Skip only for purely cosmetic, no-behavior-change tweaks.
- Batch any unspecced direct-prompt changes into one retroactive change before ending a session.
- Mirror OpenSpec edits to `.factory/` when the workflow targets both surfaces.
