---
title: Tiered Regression Coverage
trigger: openspec/ directory exists at the repo root
---
- Maintain a tiered regression suite: a fast minimum tier run on every change, and a comprehensive tier run before release cuts.
- Never let the everyday tier grow so heavy that it stops being run; push slow or full-matrix coverage to the release-only tier.
- Map every spec requirement to its covering tests and classify it Covered, Partial, or Not covered, with an aggregate coverage percentage.
- Treat coverage gaps as backlog items to close via a change proposal, not as informal notes.
