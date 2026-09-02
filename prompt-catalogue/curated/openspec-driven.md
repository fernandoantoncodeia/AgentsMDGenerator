---
title: Openspec Driven
trigger: openspec/ directory exists at the repo root
---
- Every behavior-affecting change goes through OpenSpec: proposal + delta spec under `openspec/changes/<slug>` then `openspec archive`.
- Check `openspec/specs/` and `openspec/changes/` before starting a change to avoid duplicates and conflicts.
- Never hand-edit `openspec/specs/`. Only `openspec archive` writes there.
- Spec deltas use `### Requirement: <name>` headings with `#### Scenario: <name>` blocks containing `**WHEN**` and `**THEN**` clauses.
- Skip only for purely cosmetic, no-behavior-change tweaks.
- Batch any unspecced direct-prompt changes into one retroactive change before ending a session.
- Mirror OpenSpec edits to `.factory/` when the workflow targets both surfaces.
- Never modify installed or upstream OpenSpec skills, commands, schemas, or repositories. Keep framework-owned files updateable.
- Use supported OpenSpec and team trigger points for ownership, and project-owned Factory hooks, skills, commands, or scripts for delivery gates.
- Treat the `test` team point as a team review binding, not as a new artifact in the spec-driven schema.
- Any regression-suite failure found during a change's own regression check MUST be fixed within that change before archiving — never recorded as "pre-existing"/"out-of-scope" and left open.
- An unrelated failure still blocks archiving unless the user explicitly waives it with a recorded reason in the change's own artifacts — never self-waive.
