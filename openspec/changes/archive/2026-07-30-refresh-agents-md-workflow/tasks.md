## 1. Refresh command scaffold

- [x] 1.1 Create `.claude/commands/generate-agents-refresh.md` with frontmatter matching `.claude/commands/opsx/*.md` style
- [x] 1.2 Body points to the `agents-md-refresh` skill, an input line, and a one-line behavior summary

## 2. Refresh skill body

- [x] 2.1 Create `.claude/skills/agents-md-refresh/SKILL.md` with YAML frontmatter matching the bundle pattern
- [x] 2.2 Encode the read-only default: fetch → diff → report → user decision → apply
- [x] 2.3 Encode the closed source set of six URLs and the rule that adding a source requires its own OpenSpec change
- [x] 2.4 Encode the diff format: numbered additions, refinements, deprecations — no patches
- [x] 2.5 Encode the apply path: stage an OpenSpec change under `openspec/changes/refresh-agents-md-content-<date>/`

## 3. Sync existing SKILL.md

- [x] 3.1 Verified `.claude/skills/generate-agents-md/SKILL.md` already has the 16-principle Sourced Principles list with inline source citations (this happened during the discovery sync before this change was opened)

## 4. Validation + archive

- [x] 4.1 Run `openspec validate refresh-agents-md-workflow --strict`
- [x] 4.2 Run `openspec archive refresh-agents-md-workflow -y` to sync MODIFIED requirements into `openspec/specs/agents-md-generation/spec.md` and the new capability into `openspec/specs/agents-md-refresh/spec.md`, then archive the change
