## 1. CLAUDE.md resolve helper

- [x] 1.1 Add a describe-claude-md(resolved_root) helper section in `.claude/skills/generate-agents-md/SKILL.md` documenting the four resolve cases (missing / symlink / already-valid / exists-with-other-content) and the empty-or-whitespace edge case
- [x] 1.2 Document the non-root skip case (AGENTS.md target is outside the consumer repo root) and the failure-abort case, with exact causes each reports

## 2. Create-mode mirror step

- [x] 2.1 In the "Create mode (no existing AGENTS.md)" numbered list of `.claude/skills/generate-agents-md/SKILL.md`, add a step that writes CLAUDE.md at the consumer root using the describe-claude-md resolver, placed after the AGENTS.md write and before the trim pass
- [x] 2.2 The step advances through the four cases and the empty-or-whitespace case per the spec scenarios

## 3. Update-mode mirror step

- [x] 3.1 In the "Update mode (AGENTS.md exists)" numbered list, add a step that resolves CLAUDE.md at the consumer root and writes the prepend-or-create result, placed after the existing-file read and before applying updates to AGENTS.md (per design D5)
- [x] 3.2 The step uses the same resolver logic as create mode but reads the existing CLAUDE.md first

## 4. Completion summary row

- [x] 4.1 In the "Completion summary (always)" block of `.claude/skills/generate-agents-md/SKILL.md`, replace the existing `Suggestion: whether to mirror the file to CLAUDE.md (the workflow SHOULD NOT auto-mirror; it MAY suggest)` bullet with a `Mirror: created at CLAUDE.md / refreshed CLAUDE.md (preserved N existing lines) / already-valid at CLAUDE.md / already-valid symlink at CLAUDE.md / mirror skipped <reason>` row
- [x] 4.2 Add a separate failure-mode row noting partial state when AGENTS.md succeeded but the mirror step failed

## 5. Guardrail revocation

- [x] 5.1 In the "Guardrails" section of `.claude/skills/generate-agents-md/SKILL.md`, replace the existing `Do NOT auto-mirror to CLAUDE.md; offer only.` line with `The workflow MUST ensure a CLAUDE.md mirror at the consumer root in both modes; do NOT silently skip it`
- [x] 5.2 Remove the `Do NOT use this workflow for non-AGENTS.md documentation` clash by clarifying that CLAUDE.md (the mirror) is in scope; the existing rule about non-AGENTS.md documentation still applies otherwise

## 6. Trim pass + reuse existing trim logic

- [x] 6.1 Apply the existing trim pass to the updated SKILL.md: re-read the whole file, verify it stays under the 150-line soft cap the workflow's own Sourced Principles cite (this file gets longer by ~15-25 lines from mirror logic; verify it stays compact)

## 7. Smoke verification + archive

- [x] 7.1 Run `/generate-agents` against an empty temp repo and confirm: AGENTS.md created, CLAUDE.md created with `@AGENTS.md\n`, completion summary lists Mirror row as `created at CLAUDE.md`
- [x] 7.2 Run `/generate-agents` against a temp repo with a pre-existing CLAUDE.md containing unrelated content and confirm: AGENTS.md updated, CLAUDE.md refreshed with `@AGENTS.md\n\n` prepended, original content preserved, completion summary lists Mirror row as `refreshed CLAUDE.md (preserved N existing lines)`
- [x] 7.3 Run `openspec validate add-claude-md-mirror --strict`
- [x] 7.4 Run `openspec archive add-claude-md-mirror -y` to sync MODIFIED + ADDED requirements into `openspec/specs/agents-md-generation/spec.md`
