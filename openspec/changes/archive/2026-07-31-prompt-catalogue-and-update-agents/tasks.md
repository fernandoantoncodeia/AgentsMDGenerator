## 1. Catalogue scaffolding

- [x] 1.1 Create `prompt-catalogue/` directory at the repo root
- [x] 1.2 Create `prompt-catalogue/curated/` subfolder
- [x] 1.3 Create `prompt-catalogue/proposed/` subfolder with a `.gitkeep` (the folder ships empty; operator queue)

## 2. Migrate the existing C1-C9 catalog into 9 curated category files

- [ ] 2.1 Extract the C1 Build Error Feedback Loop block from `.claude/skills/generate-agents-md/SKILL.md` into `prompt-catalogue/curated/build-error-feedback-loop.md` with YAML frontmatter (`title: Build Error Feedback Loop`, `trigger: default-on`)
- [ ] 2.2 Extract C2 into `prompt-catalogue/curated/short-and-imperative.md` (`title: Short and Imperative`, `trigger: default-on`)
- [ ] 2.3 Extract C3 into `prompt-catalogue/curated/python-project.md` (`title: Python Project Hints`, `trigger: project contains Python sources (pyproject.toml, requirements*.txt, setup.py, *.py)`)
- [ ] 2.4 Extract C4 into `prompt-catalogue/curated/windows-com.md` (`title: Windows COM`, `trigger: project imports Windows COM automation (pywin32, comtypes, win32com, winrt, pythonnet, *.tlb)`)
- [ ] 2.5 Extract C5 into `prompt-catalogue/curated/self-documentation.md` (`title: Self-Documentation`, `trigger: project has docs/ OR ADR directory OR OpenAPI/Swagger OR docs-site config OR an openspec/ directory`)
- [ ] 2.6 Extract C6 into `prompt-catalogue/curated/openspec-driven.md` (`title: OpenSpec Driven Changes`, `trigger: openspec/ exists at the repo root`)
- [ ] 2.7 Extract C7 into `prompt-catalogue/curated/tool-erratic.md` (`title: Tool Erratic Behaviour`, `trigger: default-on`)
- [ ] 2.8 Extract C8 into `prompt-catalogue/curated/openspec-cli.md` (`title: OpenSpec CLI Conventions`, `trigger: openspec/ exists AND the project runs openspec commands`)
- [ ] 2.9 Extract C9 into `prompt-catalogue/curated/shell-tooling.md` (`title: Shell Tooling`, `trigger: project mixes Windows (PowerShell) and Unix (bash / zsh) workstations OR runs shell probes in CI`)
- [ ] 2.10 Confirm each curated file is ≤100 lines (D11); trim during the C-extraction if any is over

## 3. Author the new `/update-agents` slash command + skill

- [x] 3.1 Create `.claude/commands/update-agents.md` with YAML frontmatter matching the bundle pattern (description, argument-hint) and a short body that points to the new skill
- [x] 3.2 Create `.claude/skills/update-agents/SKILL.md` with YAML frontmatter (name, description, allowed-tools, license, compatibility, metadata)
- [x] 3.3 SKILL.md first-line guardrail: explicitly declare "this workflow reads only `prompt-catalogue/curated/`; it MUST NOT read `prompt-catalogue/proposed/`" (per isolation contract)
- [x] 3.4 Encode mode detection (`/update-agents [path?]`) and the first-call-create vs subsequent-refresh branching
- [x] 3.5 Encode the trigger-scan logic that walks `prompt-catalogue/curated/*.md` and evaluates each `trigger:` against a deterministic scan of the target repo
- [x] 3.6 Encode the auto-add-to-proposed behavior (D8 + matching spec scenario): when a trigger-equivalent matches but no curated entry covers it, emit a `/refresh-agents-content addcategory --name <derived> --trigger "<evidence>" --body "<starter>"` invocation and write the placeholder into `prompt-catalogue/proposed/<derived>.md`. Do NOT splice the proposed entry.
- [x] 3.7 Encode the CLAUDE.md mirror step (already shipped via `add-claude-md-mirror`)
- [x] 3.8 Encode the trim-pass: respect the AGENTS.md 150-line soft cap and the per-category 100-line cap (D11)
- [x] 3.9 Encode the completion summary: include the Auto-added-to-proposed listing alongside sections spliced, mirror outcome, and any "applicable-but-not-curated" entries
- [x] 3.10 Encode the guardrails: hard isolation against `proposed/`, no auto-splice of proposed content, auto-routed self-additions
- [x] 3.11 Trim the SKILL.md: only operational content lives here; no consumer-facing prompt bodies (requirement #7)

## 4. Author the new `/refresh-agents-content` slash command + skill

- [x] 4.1 Create `.claude/commands/refresh-agents-content.md` with YAML frontmatter (description, argument-hint listing the five actions)
- [x] 4.2 Create `.claude/skills/refresh-agents-content/SKILL.md` with YAML frontmatter matching the bundle pattern
- [x] 4.3 Encode the action dispatch: `/refresh-agents-content <action> [...]`. The five actions are `addcontent`, `curatecontent`, `browsecontent`, `addcategory`, `curatecategory`.
- [x] 4.4 Encode `addcontent --category <cat> --body <text> [--title <text>]` (added optional title override during authoring; required --body checks remain)
- [x] 4.5 Encode `curatecontent <ref>`: merge-and-simplify the proposed entry into `prompt-catalogue/curated/<cat>.md`; remove the proposed entry after success; apply length-discipline trim if needed
- [x] 4.6 Encode `browsecontent [--source <url>...] [--apply]`: fetch the six canonical URLs (plus repeatable ad-hoc --source URLs); diff against `prompt-catalogue/curated/` AND embedded Sourced Principles; emit a numbered diff labelled by target surface ([catalogue:<cat>] or [principles:<index>]); --apply is opt-in
- [x] 4.7 Encode `addcategory --name <cat> --trigger <rule> --body <text>`: refuse if `--body` is absent/empty; create `prompt-catalogue/proposed/<cat>.md` with frontmatter and the supplied body; refuse collision with existing curated name
- [x] 4.8 Encode `curatecategory --name <cat>`: promote proposed entry to `prompt-catalogue/curated/<cat>.md`; surface remap candidates for operator confirmation; do NOT auto-remap
- [x] 4.9 Encode the catalogue-bypasses-OpenSpec rule: write targets are `prompt-catalogue/` ONLY; no `openspec/new change` for catalogue updates (only for Sourced Principles refresh)
- [x] 4.10 Encode the Sourced Principles bridge inside browsecontent: when the diff targets Sourced Principles, propose an OpenSpec change under `openspec/changes/refresh-agents-md-content-<date>/` and wait for the operator's `openspec archive`; do NOT auto-archive
- [x] 4.11 Trim the SKILL.md; no consumer prompt bodies here either (requirement #7)

## 5. Delete the superseded files

- [x] 5.1 Delete `.claude/commands/generate-agents.md`
- [x] 5.2 Delete `.claude/commands/generate-agents-refresh.md`
- [x] 5.3 Delete the entire `.claude/skills/generate-agents-md/` folder
- [x] 5.4 Delete the entire `.claude/skills/agents-md-refresh/` folder

## 6. Update this repo's own AGENTS.md

- [x] 6.1 Re-run `/update-agents` against this repo (or hand-update its AGENTS.md) so the file references the new skill names and the catalogue's role (note: `update-agents` is the new command; in this transition the file is hand-edited until a fresh consumer-style invocation confirms behavior)
- [x] 6.2 Confirm AGENTS.md still fits the 150-line soft cap

## 7. Smoke verification

- [x] 7.1 Run `/update-agents` against an empty temp repo at `/tmp/smoke-empty-prompt-cat` and confirm: AGENTS.md created with mandated baseline + zero curated category splices (no triggers fire), CLAUDE.md mirror created, completion summary reports empty curated splice list
- [x] 7.2 Run `/update-agents` against a temp repo with `prompt-catalogue/curated/python-project.md` AND a Python source file; confirm AGENTS.md splices the python-project section
- [x] 7.3 Run `/update-agents` against a temp repo with Go sources but no curated Go category; confirm auto-add to `proposed/go-language.md` and the completion summary's "Auto-added to proposed catalogue" line
- [x] 7.4 Run `/refresh-agents-content addcategory --name shell-tooling --trigger "*.sh files present" --body "<starter>"` against the same temp repo and confirm `prompt-catalogue/proposed/shell-tooling.md` is created with frontmatter
- [x] 7.5 Run `/refresh-agents-content addcategory --name shell-tooling --trigger "*.sh files present"` (no body) and confirm rejection: `error: --body is required`
- [x] 7.6 Run `/refresh-agents-content browsecontent --source https://example.com/extra-guide` and confirm the diff summary lists numbered items with the source URL tagged as ad-hoc

## 8. Validate + archive

- [x] 8.1 Run `openspec validate prompt-catalogue-and-update-agents --strict`
- [x] 8.2 Run `openspec archive prompt-catalogue-and-update-agents -y` to sync the three modified/added capability deltas into `openspec/specs/`, and archive the change as `2026-07-30-prompt-catalogue-and-update-agents` (or the current date)
