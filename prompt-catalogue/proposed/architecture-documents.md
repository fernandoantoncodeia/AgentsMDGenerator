---
title: Architecture Documents
trigger: project contains architecture/functional-architecture.md or architecture/technical-architecture.md
---
- Keep four documents under `architecture/`: references `functional-architecture.md` and `technical-architecture.md`, and append-only histories `*-history.md`.
- Write references in present tense, by theme, as the architecture is now. Never put dated entries (`### YYYY-MM-DD — …`) in a reference.
- Put every dated decision in the matching history document, append-only. Never rewrite or reorder past entries.
- Read both references before authoring any proposal, spec or design: they are the canonical input.
- After design and before tasks, reconcile specs and design against the references: append each decision to history, then interpret it into the reference.
- Interpret by adding a theme, amending in place, replacing or removing a stale statement, or "none" with a reason. Never append a log item to a reference.
- Before archive, re-check the references against what was built. Archive only on a passed record or a recorded human waiver; never self-waive.
- Keep one mermaid diagram per reference (functional: logical pieces and dependencies; technical: physical pieces and links). Update both on every change.
- If a reference is log-shaped, migrate it once: entries verbatim into history, then rewrite the reference by theme.
- Never edit installed or upstream OpenSpec files to add these rules; use project-owned scripts, skills or team points.
