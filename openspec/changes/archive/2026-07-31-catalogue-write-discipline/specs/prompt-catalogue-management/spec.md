# prompt-catalogue-management delta spec

## MODIFIED Requirements

### Requirement: addcontent appends a proposed entry to the catalogue
The `/refresh-agents-content addcontent` action SHALL append a new entry to `prompt-catalogue/proposed/<category>.md`. The action SHALL pre-trim the supplied body BEFORE writing: drop duplicates against existing curated and proposed bullets in the same category (≤30 char edit distance), drop verbose trailing clauses (`where X`, `in which case`, `; note that Y` once the leading commands are present), and split any bullet longer than 200 chars at its first sentence boundary into two bullets. If a resulting bullet is still >200 chars, refuse the call rather than write. Operators can opt out of the trim pass with `--no-trim-tails` per invocation; the dedupe and length caps are mandatory (no opt-out flag). The pre-trim pass is reported in the action's completion summary.

#### Scenario: addcontent dedupes near-duplicates in same category
- **WHEN** the operator invokes `/refresh-agents-content addcontent --category python-project --body "..."` with a bullet that has ≤30 char edit distance against an existing curated bullet in the same category
- **THEN** the action drops the duplicate bullet, writes only new content, and reports `addcontent: dedupe <n> bullets vs curated` in its completion summary

#### Scenario: addcontent splits an over-long bullet
- **WHEN** the operator supplies a bullet >200 chars
- **THEN** the action splits at the first sentence boundary and writes two bullets. If either half is still >200 chars, the action refuses with `addcontent: bullet too long (≥200 chars after split)` and writes nothing.

#### Scenario: addcontent drops a redundant trailer
- **WHEN** the operator supplies a bullet ending with `where requirements.txt is substituted by the actual filename` and the leading imperative already covers the substitution
- **THEN** the action drops the trailer and reports `addcontent: trim tail on bullet 1 (dropped "<trailer text>")`. Operator can disable with `--no-trim-tails`.

#### Scenario: addcontent to a new proposed file
- **WHEN** the operator invokes `/refresh-agents-content addcontent --category shell-tooling --body "..."`
- **AND** `prompt-catalogue/proposed/shell-tooling.md` does not exist
- **THEN** the action creates the file with the supplied body (after pre-trim) and writes a YAML frontmatter header with the operator-supplied title (or a default generated from the category name)

#### Scenario: addcontent to an existing proposed file
- **WHEN** `prompt-catalogue/proposed/shell-tooling.md` already exists
- **AND** the operator invokes `/refresh-agents-content addcontent --category shell-tooling --body "..."`
- **THEN** the action appends the new entry (after pre-trim) with separator (e.g. `---` between entries) so multiple proposed items can coexist in one file

#### Scenario: addcontent rejects missing category
- **WHEN** the operator invokes `/refresh-agents-content addcontent` without `--category`
- **THEN** the action reports `error: --category is required` and writes nothing

### Requirement: curatecontent promotes one proposed entry to curated, merge-and-simplify
The `/refresh-agents-content curatecontent` action SHALL move one specific proposed entry to `prompt-catalogue/curated/<category>.md`. The action SHALL perform a merge against any existing curated entry: identify overlap with the proposed entry, deduplicate (≤30 char edit distance), apply the workflow's own length-discipline rule (per-category ≤100 lines, per-bullet ≤200 chars). The proposed entry MUST be removed from `proposed/<category>.md` after successful curation. **`--force` override.** If the merged file would exceed 100 lines OR any bullet would exceed 200 chars, the action SHALL refuse with a trim diff (one line per violation) and write nothing. The operator can pass `--force` to override size or bullet-length refusals; `--force` MAY NOT override a missing-`trigger:` field failure.

#### Scenario: curatecontent promotes a fresh proposal
- **WHEN** the operator invokes `/refresh-agents-content curatecontent` and selects an entry from `prompt-catalogue/proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` does not exist
- **THEN** the action creates the curated file with the proposed entry as the body and removes the entry from the proposed file

#### Scenario: curatecontent merges with existing curated content
- **WHEN** the operator invokes `/refresh-agents-content curatecontent` and selects an entry from `proposed/<category>.md`
- **AND** `prompt-catalogue/curated/<category>.md` already exists
- **THEN** the action reads both files, identifies semantically overlapping rules, deduplicates (≤30 char edit distance), applies the workflow's length-discipline trim rule, and writes the merged result to the curated file. The proposed entry is removed from the proposed file. The action reports `merged 2 entries` (or the actual count) in its completion summary.

#### Scenario: curatecontent refuses merged file over the per-category cap
- **WHEN** the merged curated file would exceed the 100-line per-category cap
- **THEN** the action refuses with `curatecontent: refused — merged would be <line-count> lines (cap 100)` followed by a `Suggested fix:` line listing which bullets to drop. The proposed file is unchanged.

#### Scenario: curatecontent refuses bullet-length violation
- **WHEN** the merged curated file would contain a bullet >200 chars
- **THEN** the action refuses with `curatecontent: refused — bullet <n> exceeds 200 chars in merged output` and a `Suggested fix:` line showing how the bullet would split at the first sentence boundary. The proposed file is unchanged.

#### Scenario: curatecontent --force override
- **WHEN** the operator has read the trim diff and chooses to accept the size violation
- **AND** invokes `/refresh-agents-content curatecontent --force`
- **THEN** the action proceeds with the merge despite the violation and records `curatecontent: --force applied, accepted <violation>` in the completion summary. The proposed file is removed.

#### Scenario: curatecontent cannot --force past missing trigger
- **WHEN** the merged file's YAML frontmatter is missing `trigger:`
- **AND** the operator invokes `/refresh-agents-content curatecontent --force`
- **THEN** the action still refuses with `curatecontent: refused — missing trigger: field is non-overridable; --force cannot resolve it` and writes nothing.

#### Scenario: curatecontent enforces length discipline on merge
- **WHEN** the merged result would exceed the 100-line per-category cap
- **THEN** the action refuses with `curatecontent: refused — merged would be <line-count> lines (cap 100)` followed by a `Suggested fix:` line. Operator passes `--force` to override and accept the over-cap merge. This supersedes the previous soft-trim behaviour; soft-trim is no longer performed.

### Requirement: addcategory proposes a new category with a starter body
The `/refresh-agents-content addcategory` action SHALL create `prompt-catalogue/proposed/<new-category>.md` with a setup consisting of: a YAML frontmatter block (built from the operator-supplied `--name` and `--trigger`), and the operator-supplied `--body` content as the starting body, after the same pre-trim pass that `addcontent` runs (dedupe against proposed files ONLY — there is no curated file yet — trim verbose trailers, split bullets >200 chars at sentence boundary). `--body` is REQUIRED; empty/whitespace-only `--body` is rejected. The action MUST NOT create anything in `prompt-catalogue/curated/`. The action reports the suggested file path and trigger rule plus any trim-pass log in its completion summary.

#### Scenario: addcategory creates a proposed entry with body
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name new-language --trigger "*.go files present" --body "<starter content>"`
- **THEN** `prompt-catalogue/proposed/new-language.md` is created with title derived from the first sentence of `--body`, trigger matching Go files, and the supplied body as the seed content after pre-trim. The completion summary reports the new proposed file path, trigger rule, and any trim-pass log.

#### Scenario: addcategory rejects missing body
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name new-language --trigger "*.go files present"`
- **AND** `--body` is absent or empty
- **THEN** the action refuses with `error: --body is required (D8 + spec). Re-run with at least a one-sentence starter body so the operator has something to refine.` and writes nothing

#### Scenario: addcategory refuses collision with existing curated category
- **WHEN** the operator invokes `/refresh-agents-content addcategory --name python-project` and `prompt-catalogue/curated/python-project.md` already exists
- **THEN** the action refuses with `error: category already in curated; use curatecontent to refine the existing curated entry`

### Requirement: curatecategory accepts a proposed category into curated with remap
The `/refresh-agents-content curatecategory` action SHALL promote a `prompt-catalogue/proposed/<category>.md` entry to `prompt-catalogue/curated/<category>.md`. After promotion, the resulting curated file is checked against the same contract as `curatecontent`: ≤100 lines per file, ≤200 chars per bullet, mandatory `trigger:` field. **Refusal profile.** If any cap is violated, the action refuses with a trim diff and writes nothing; the operator passes `--force` to override size violations only. The remap-candidates behaviour from before is preserved.

#### Scenario: curatecategory promotes a new category with no remap candidates
- **WHEN** the operator invokes `/refresh-agents-content curatecategory` selecting a proposed entry
- **AND** no other proposed entries share the trigger-evidence
- **THEN** the action creates `prompt-catalogue/curated/<category>.md` with the proposed content after cap verification and clears the proposed entry

#### Scenario: curatecategory surfaces remap candidates for operator validation
- **WHEN** the proposed entry creates a category that other proposed entries could be remapped to
- **THEN** the action lists them as `remap candidates: <other-category-1>, <other-category-2>` and waits for the operator to confirm each remap explicitly

#### Scenario: curatecategory refuses over-cap result
- **WHEN** after promotion the curated file would exceed 100 lines or any bullet would exceed 200 chars
- **THEN** the action refuses with the same shape as `curatecontent`'s refusal (trim diff with `Suggested fix:` lines), and writes nothing. Operator passes `--force` to override size and bullet-length; `--force` cannot override a missing-`trigger:` field.

## ADDED Requirements

### Requirement: build-error-feedback-loop content must direct through catalogue flow
The `prompt-catalogue/curated/build-error-feedback-loop.md` entry's body MUST direct the operator through `/refresh-agents-content addcontent` / `addcategory` / `curatecontent` / `curatecategory` for any new consumer-facing rule, and MUST include an explicit Never list forbidding direct edits to `AGENTS.md`, `prompt-catalogue/curated/`, and any skill file's body. Specifying what to put in AGENTS.md, the curated folder, or the SKILL.md is forbidden; the entry routes through catalogue flow only.

#### Scenario: build-error-feedback-loop redirects mistakes through addcontent
- **WHEN** a maintainer reads `prompt-catalogue/curated/build-error-feedback-loop.md`
- **THEN** the entry's first imperative line is to invoke `/refresh-agents-content addcontent --category <cat> --body "<rule>"` (existing category) or `/refresh-agents-content addcategory --name <derived> --trigger "<rule>" --body "<starter>"` (new category). The entry does NOT instruct the operator to edit `AGENTS.md`, `curated/`, or any skill file directly.

#### Scenario: build-error-feedback-loop carries an explicit Never list
- **WHEN** a maintainer reads `prompt-catalogue/curated/build-error-feedback-loop.md`
- **THEN** the entry contains explicit Never statements covering: hand-edit `AGENTS.md` outside `/update-agents`; hand-edit `prompt-catalogue/curated/*.md` outside `/refresh-agents-content curatecontent`/`curatecategory`; embed consumer-facing prompt bodies in `.claude/skills/<name>/SKILL.md`.


### Requirement: Catalogue self-discipline rules and pre-trim contract
The catalogue's mechanical hygiene is governed by four rules. Every `/refresh-agents-content` write action SHALL honour these rules. Operators cannot opt out of dedupe or bullet-length caps; the trim-tails phase is opt-out per call.

- Per-category file budget: ≤100 lines (D11).
- Per-bullet length cap: ≤200 chars; over-length bullets split at the first sentence boundary, halves stay separate unless folded by dedupe.
- Dedupe: any new bullet whose edit distance against an existing curated or proposed bullet in the same category is ≤30 chars is dropped as a duplicate.
- Frontmatter: every curated entry MUST carry `title:` AND `trigger:`; absence is a non-overridable contract violation; `--force` cannot resolve it.

#### Scenario: Dedupe drops near-duplicate bullets
- **WHEN** the operator supplies a bullet whose edit-distance against an existing curated bullet in the same category is ≤30 chars
- **THEN** the action drops the duplicate and reports `addcontent: dedupe <n> bullets vs curated` (or the analogous `curatecontent`/`addcategory` log line)

#### Scenario: Split-at-sentence for over-length bullets
- **WHEN** the operator supplies a bullet >200 chars
- **THEN** the action splits at the first sentence boundary. Either half >200 chars fails the action with `bullet too long (≥200 chars after split)`.

#### Scenario: Opt-out flag documented
- **WHEN** the operator passes `--no-trim-tails` to `addcontent` or `addcategory`
- **THEN** the trim-tails phase is skipped and the supplied body is written verbatim (subject to dedupe and length caps). The completion summary records `addcontent: --no-trim-tails applied`.

### Requirement: Catalog self-discipline scan at /update-agents time
Every invocation of `/update-agents` (whose capability is `agents-md-generation`) SHALL walk `prompt-catalogue/curated/*.md` after the splice pass and emit a `Catalog self-discipline check:` section in the consumer's completion summary. The scan is read-only; it does NOT refuse the `/update-agents` invocation. Findings per file:

- `ok` — all four rules pass.
- `<n> lines (cap 100)` — over the per-category cap (file over 100 lines).
- `bullet <i> exceeds 200 chars (n chars)` — over-length bullet.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category dedupe candidate.
- `missing trigger:` — HARD finding, named in the summary as a contract violation.

#### Scenario: Self-discipline check surfaces findings
- **WHEN** a curated file exceeds 100 lines or contains an over-length bullet
- **THEN** the `/update-agents` completion summary has a `Catalog self-discipline check:` section listing each curated file with its findings. The summary still reports the splice outcome; the scan is non-blocking.

#### Scenario: Self-discipline check flags missing trigger field
- **WHEN** a curated file lacks the `trigger:` field
- **THEN** the file is flagged in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is named in the summary; the operator is expected to invoke `curatecontent` on the file to repair the frontmatter.
