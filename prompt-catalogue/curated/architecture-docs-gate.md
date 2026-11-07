---
title: Architecture Docs Gate
trigger: openspec/ directory exists at the repo root, OR an architecture/ directory
  exists with functional-architecture.md or technical-architecture.md
---
- Keep four documents under `architecture/`: two references (`functional-architecture.md`, `technical-architecture.md`) and two append-only histories (`*-history.md`).
- Write references in present tense, organized by theme, describing the architecture as it is now. Never put dated decision entries (`### YYYY-MM-DD — …`) in a reference.
- Put every dated decision in the matching history document, append-only; never rewrite or reorder past entries.
- Treat the references as the live, canonical input to every proposal, spec and design session. Read them before authoring any of those artifacts.
- Pre-gate: before authoring a proposal, specs or design, confirm all four documents exist and are valid.
- If a reference is log-shaped, migrate it once: move entries verbatim into history, then rewrite the reference as a thematic description.
- Design-alignment gate: after design and before tasks, reconcile specs and design against the references. Append each decision to history, then interpret it into the reference.
- Interpret by adding a theme, amending in place, replacing or removing a stale statement, or "none" with a reason. Never append a log item to a reference.
- Post-apply gate: before archiving, re-run the reconciliation against what was actually implemented. Archive only on `outcome: "passed"` or a non-empty recorded waiver.
- Record each gate outcome in a per-change file with the stage, the history entries, and one interpretation per entry. Never self-waive.
- Keep one mermaid diagram in each reference: functional shows logical pieces and their dependencies; technical shows physical pieces and their links. Update both on every change.
- Enforce the gates mechanically with a checker script wired into a pre-archive hook. If the runtime has no confirmed hook, run the checker manually before each stage.
- Never modify installed or upstream OpenSpec files to add these gates; use project-owned scripts, skills or team thinking-points.
