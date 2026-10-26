---
title: Skills Factory Project
trigger: project contains .persona-factory/manifest.json, .claude/teams/*/TEAM.md,
  .claude/skills/team-run/SKILL.md, workflows/software-project.yaml
---
- Call the factory through the CLIs your `.mcp.json` and hooks use (generation-suffixed, e.g. `factory-workflow-v2`); never mix generations. If anything misbehaves run `factory-setup-v2 doctor`.
- Never hand-edit factory state: the registry (`projects.json`), credentials, `.persona-factory/manifest.json`, or the factory entries in `.mcp.json` and hook settings. Re-run `init`/`update`.
- Never write gate records (`hazard-review-*.json`, `architecture-docs-gate-review.json`) or `deferred-findings-*.json`; the harness writes and signs them (`factory-workflow-v2 tool review.* --sign`).
- Never read, print or copy anything under the registry home (`~/.factory-*`): it holds the signing credential and the control-plane token.
- Drive every change through the `software-project` workflow or the OpenSpec skills. Never bypass the preflight or archive hooks; fix what the gate reports.
- Review loops: only critical and high findings iterate; any other finding gets one fix loop, then goes to the review backlog. Never self-waive: a waiver is a recorded human decision with a reason.
- At the start of every change run `factory-workflow-v2 backlog` and include the open items without asking. Name each `[backlog:<id>]` in a task, ticked when done, or drop it with `dropped: <reason>`.
- Keep `research/*-hazard-files.txt` current: add a file the moment a hazard shape appears. An empty list makes the hazard gates pass without checking anything.
- Keep the four architecture documents current through the architecture-docs-gate skill: reference documents describe the present, history documents hold the dated decisions.
- Vendored skills and personas under `.claude/` evolve through `/refine-skill` and `/refine-persona`; local edits are traced as drift on `update`, so promote them instead of forking silently.
- Use the memory tools: `recall` before deciding, `remember` tradeoffs after proposal, specs and design. `.persona-factory/memory` digests are committed; the derived index is not.
- Do not start a real `software-project` run (it spends agent tokens) unless the user asks; use `factory-setup-v2 smoke` to check an install.
- A rule about using the factory itself belongs in this category: add it with `catalogue_addcontent(category="skills-factory-project", body=...)`.
