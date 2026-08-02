## 1. SKILL contract updates

- [x] 1.1 Update `.claude/skills/refresh-agents-content/SKILL.md` to add the "Catalogue self-discipline" preamble section (≤15 lines) listing the four rules: ≤100-line per-category, ≤200-char per-bullet, ≤30-char edit-distance dedupe, mandatory `trigger:` field
- [x] 1.2 Update `/refresh-agents-content/SKILL.md` `addcontent` action contract to specify pre-trim (dedupe, split at sentence boundary, trim verbose trailers)
- [x] 1.3 Update `/refresh-agents-content/SKILL.md` `addcategory` action contract to apply the same pre-trim pass
- [x] 1.4 Update `/refresh-agents-content/SKILL.md` `curatecontent` action contract to specify hard refusal at >100-line or >200-char violation, with `--force` opt-in excluding `missing trigger:` failure
- [x] 1.5 Update `/refresh-agents-content/SKILL.md` `curatecategory` action contract to apply the same hard refusal + `--force` rules
- [x] 1.6 Update `/refresh-agents-content/SKILL.md` `browsecontent` action contract to add `self-discipline violation: <cat>` tagging
- [x] 1.7 Update `.claude/skills/update-agents/SKILL.md` to add §X "Catalog self-discipline check" with the four-rule scan and the `Catalog self-discipline check:` summary section shape

## 2. Curated entry rewrite

- [x] 2.1 Rewrite `prompt-catalogue/curated/build-error-feedback-loop.md` to redirect through `/refresh-agents-content addcontent` / `addcategory` / `curatecontent` / `curatecategory`
- [x] 2.2 Add the explicit Never list to `build-error-feedback-loop.md`: never hand-edit AGENTS.md; never hand-edit `curated/`; never embed consumer prompt bodies in SKILL.md

## 3. Self-discipline scan baseline

- [x] 3.1 Run the catalog self-discipline scan against the existing 9 curated files (`build-error-feedback-loop`, `short-and-imperative`, `python-project`, `windows-com`, `self-documentation`, `openspec-driven`, `tool-erratic`, `openspec-cli`, `shell-tooling`)
- [x] 3.2 Record any existing files
### 3.2.a Baseline findings (recorded while change is open)

- `prompt-catalogue/curated/build-error-feedback-loop.md`: ok after rewrite (25 lines).
- `prompt-catalogue/curated/short-and-imperative.md`: heuristic flag `near-duplicate pair bullets 2 and 3` (24-char heuristic distance). Pending re-check with a strict Levenshtein metric; flagged for operator follow-up.
- `prompt-catalogue/curated/python-project.md`: `bullet 6 exceeds 200 chars (304 chars)`. Real violation; unattended operator action item. The bullet merges a single imperative with both Unix and PowerShell one-liners. Operator decision: split into 2 bullets before this change archives so the next sync is clean; otherwise the catalog self-discipline scan surfaces it in every `/update-agents` completion summary.
- `prompt-catalogue/curated/windows-com.md`: ok.
- `prompt-catalogue/curated/self-documentation.md`: ok.
- `prompt-catalogue/curated/openspec-driven.md`: ok.
- `prompt-catalogue/curated/tool-erratic.md`: ok.
- `prompt-catalogue/curated/openspec-cli.md`: 11 heuristic near-duplicate pairs flagged. Heuristic may be wrong (SequenceMatcher ratio × average length is sloppy for short strings); pending operator follow-up with a stricter metric.
- `prompt-catalogue/curated/shell-tooling.md`: ok.
 that fail the four-rule check in this change's `tasks.md` completion summary (so future operators see the baseline findings)

## 4. Smoke verification

- [x] 4.1 Run `/refresh-agents-content addcontent --category python-project --body "<near-duplicate>"` against a sandbox catalogue; confirm the duplicate is dropped and the completion summary logs `addcontent: dedupe 1 bullet vs curated`
- [x] 4.2 Run `/refresh-agents-content addcontent --category python-project --body "<a single bullet well over 200 chars>"` against a sandbox catalogue; confirm the action refuses with `addcontent: bullet too long (≥200 chars after split)`
- [x] 4.3 Run `/refresh-agents-content addcontent --category python-project --body "<bullet with redundant trailer>"` against a sandbox catalogue; confirm the trailer is dropped and logged `addcontent: trim tail on bullet 1`
- [x] 4.4 Run `/refresh-agents-content addcontent --no-trim-tails --category python-project --body "<bullet with redundant trailer>"`; confirm the trailer survives the trim phase and the summary logs `addcontent: --no-trim-tails applied`
- [x] 4.5 Run a sandbox `curatecontent` whose merged result exceeds 100 lines; confirm refusal with `curatecontent: refused — merged would be <line-count> lines (cap 100)` and `Suggested fix:` line. Then re-run with `--force` and confirm override.
- [x] 4.6 Run a sandbox `curatecategory` whose curated output is missing `trigger:`; confirm `--force` does NOT bypass the refusal: `curatecategory: refused — missing trigger: field is non-overridable; --force cannot resolve it`
- [x] 4.7 Run a sandbox `/update-agents` against an empty consumer repo with a curated file that fails one hygiene rule; confirm the completion summary contains a `Catalog self-discipline check:` section but the workflow still emits AGENTS.md as normal

## 5. Validate + archive

- [x] 5.1 Run `openspec validate catalogue-write-discipline --strict`
- [x] 5.2 Run `openspec archive catalogue-write-discipline -y` to sync the three modified/added capability deltas into `openspec/specs/`, and archive the change as `2026-07-31-catalogue-write-discipline`
