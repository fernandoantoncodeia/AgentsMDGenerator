# Change: catalogue-write-discipline

## Why

The `prompt-catalogue/` flow governs every consumer-facing prompt in this repo, but real-world operator usage has revealed two contract weaknesses:

1. **Trim discipline is operator-judgment only.** `addcontent` writes the operator-supplied body verbatim into `proposed/` and `curatecontent` notes "applying the workflow's own short and imperative trim" but never enforces it. Operators have shipped curated bullets with redundant trailers (`... where X is substituted by the actual filename`), near-duplicates of existing bullets, and rule fragments that exceed sane per-bullet length. The hand-fix loop is operator fatigue: a missed trim lands in `curated/`, then has to be undone with another `curatecontent` call.
2. **`build-error-feedback-loop` directs mistakes straight to AGENTS.md.** The default-on category entry reads *"add a short imperative rule to AGENTS.md under the most relevant section"*. This contradicts requirement #7 (consumers prompts live only in the catalogue; never splice directly into AGENTS.md) and is the same pattern we explicitly banned for `/update-agents` self-additions.

This change makes the catalogue flow self-correcting: `addcontent` pre-trims before `proposed/` sees the bytes, `curatecontent` hard-refuses on size or duplication violations, `/update-agents` scans every curated entry at consumer invocation and surfaces findings in its completion summary, and `build-error-feedback-loop` is rewritten to explicitly route through `/refresh-agents-content`.

## What Changes

- `prompt-catalogue/curated/build-error-feedback-loop.md` is REWRITTEN to direct mistakes through `/refresh-agents-content addcontent` / `addcategory` / `curatecontent` / `curatecategory` and to carry an explicit Never list forbidding direct edits to AGENTS.md or `prompt-catalogue/curated/`.
- `agents-md-generation` capability is MODIFIED: a new requirement adds a catalog self-discipline scan that walks every `prompt-catalogue/curated/*.md` at `/update-agents` invocation time and surfaces findings (oversize file, >200-char bullet, near-duplicate rule, missing `trigger:` field) in the consumer's completion summary.
- `prompt-catalogue-management` capability is MODIFIED: `addcontent` SHALL pre-trim the supplied body before writing to `proposed/`; `curatecontent` SHALL refuse the merge if the result exceeds 100 lines, any bullet exceeds 200 chars, or the merge would create a near-duplicate rule (≤30 char edit distance); `addcategory` SHALL pre-trim the body the same way; `curatecategory` SHALL enforce the same caps on the resulting curated file; `build-error-feedback-loop`'s content contract is explicitly "must direct through catalogue flow".
- `agents-md-refresh` capability is MODIFIED: `browsecontent` SHALL report, for each curated file it inspects, whether the file passes the catalog self-discipline check (the new requirement from `prompt-catalogue-management`); a curated file that fails the self-discipline check SHALL be tagged in the diff summary as `self-discipline violation: <category>`.

## Capabilities

- MODIFIED `agents-md-generation` — adds the catalog self-discipline scan at consumer invocation time.
- MODIFIED `prompt-catalogue-management` — adds the pre-trim and hard-refusal contracts; pins down the build-error-feedback-loop content contract.
- MODIFIED `agents-md-refresh` — extends the browsecontent diff summary with `self-discipline violation:` tags.

## Impact

### Files to add
- none beyond the spec deltas inside this change's directory

### Files to modify
- `prompt-catalogue/curated/build-error-feedback-loop.md` (full rewrite — a 13-line curated entry; trim-controlled)
- `.claude/skills/refresh-agents-content/SKILL.md` (pre-trim, hard-refusal, build-error-feedback-loop contract)
- `.claude/skills/update-agents/SKILL.md` (catalog self-discipline scan §X)

### Files to delete
- none
