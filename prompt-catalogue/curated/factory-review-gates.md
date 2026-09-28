---
title: Factory Review Gates
trigger: project has .persona-factory
---
- Bug Fix Validation Review: for a bug/crash-fix OpenSpec change, run an independent empty-context review once tasks.md is complete — before apply starts, not before archive.
- The review agent must be genuinely fresh and tool-restricted per Subagent Containment — never a context-inheriting fork, never full-access.
- Score exactly four things: solves the reported problem, any collateral regressions, similar unaddressed occurrences elsewhere, is the fix provable.
- Apply may not start while a finding is open; fix and re-review, or have a human explicitly waive it with a reason — never self-waive.
- Re-run the review once more after implementation, before archive, as a regression check against what was actually built.
- Hazard Guardrail Review: maintain an explicit, curated hazard file list per domain (e.g. concurrency-reentrancy, security-sensitive-surface).
- Any diff touching a listed file requires an independent review focused on that hazard, run by a fresh, tool-restricted agent per Subagent Containment.
- Keep each domain's hazard list current: add a file the moment a new hazard shape is found; do not let it go stale.
- Record the review's outcome explicitly (e.g. a per-change review-record file); never let an open finding ship silently or be self-waived.
- Run hazard review before considering the change done, even when it is not itself a bug fix.
