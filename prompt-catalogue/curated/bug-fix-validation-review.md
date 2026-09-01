---
title: Bug Fix Validation Review
trigger: openspec/ directory exists at the repo root
---
- For a bug/crash-fix OpenSpec change, run an independent empty-context review once tasks.md is complete — before apply starts, not before archive.
- The review agent must be genuinely fresh, never a context-inheriting fork; it checks the fix against real evidence, not the design's own narrative.
- Score exactly four things: does it solve the reported problem, any collateral regressions, similar unaddressed occurrences elsewhere, and is the fix provable.
- Apply may not start while a finding is open; fix and re-review, or have a human explicitly waive it with a reason — never self-waive.
- Re-run the review once more after implementation, before archive, as a regression check against what was actually built.
