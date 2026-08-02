---
title: Build Error Feedback Loop
trigger: default-on
---

When the user reports a build error you caused, or a mistake you could repeat, first decide whether the rule is generic or project-specific, then route it to the correct surface.

## Generic rules (go to the central catalogue)

Generic rules apply to many projects. Reuse the most-relevant existing curated category (e.g. python-project, openspec-driven, short-and-imperative) before creating a new one.

- From a project skill, call the MCP tool `catalogue_addcontent(category="<cat>", body="<rule>")`; it writes to `prompt-catalogue/proposed/<cat>.md` in the master repo.
- From the master repo as operator, run `agentsmd addcontent <cat> --body "<rule>"`.
- If no category fits, call `catalogue_addcategory(name="<derived>", trigger="<rule>", body="<starter>")` or run `agentsmd addcategory <derived> --trigger "<rule>" --body "<starter>"`.
- Tell the user what you staged and the path. Do NOT splice the rule into the consumer's AGENTS.md, into `prompt-catalogue/curated/`, or into any sibling skill file.
- The operator later curates it with `agentsmd curatecontent <cat>` or `agentsmd curatecategory <derived>` in the master repo.
- The curated file then feeds the next consumer `/update-agents` invocation.

## Project-specific rules (stay in the project's AGENTS.md)

- Project-specific rules apply only to the current consumer project (a build error unique to this repo, a convention that makes sense only here).
- Do NOT send them to the central catalogue.
- Instead, surface the rule text so the user can paste it into the project's own AGENTS.md under a project-specific section.
- Then re-run `/update-agents` to keep the file consistent.
- Example rule: "Always run `make validate` before `make test` in this repo."

## Never list

- **Never** hand-write a generic rule into `<agent-root>/AGENTS.md` outside `/update-agents`; that file is regenerated output, not a scratchpad.
- **Never** edit `prompt-catalogue/curated/*.md` directly; go through `agentsmd curatecontent` / `agentsmd curatecategory` so the operator review gate runs.
- **Never** embed consumer-facing prompt bodies in `.claude/skills/<name>/SKILL.md`; skills stay operational and prompt bodies live only in the catalogue.
