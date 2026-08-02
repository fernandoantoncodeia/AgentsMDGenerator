# Design: catalogue-write-discipline

## Context

`prompt-catalogue/` is the single blessed write surface for consumer prompts (requirement #7). Operators land there via `/refresh-agents-content` actions, every one of which currently ships operator-supplied text into `proposed/` with no shape verification and merges into `curated/` with a trim note that the operator is expected to honour. Two real-world findings:

1. A curated entry returned from `curatecontent` recently contained a redundant trailer (`where requirements.txt is substituted by the actual filename`) that the operator had to revise in a follow-up pass. The trim discipline is operator-driven and therefore fragile.
2. `build-error-feedback-loop` (a default-on rule, currently the most-spliced curated entry) tells the operator to "add a short imperative rule to AGENTS.md under the most relevant section", which is precisely the anti-pattern `/update-agents` §10 forbids. Concretely, an operator reading build-error-feedback-loop would hand-edit AGENTS.md, bypassing the catalogue pipeline entirely.

Both pathologies route through the same operator surface: `/refresh-agents-content`. Closing the loop is the only place to fix them.

## Goals

- Make `/refresh-agents-content` mechanically enforce trim mechanics so operator judgment is the last-mile polish, not the safety net.
- Make the failure mode for "I made a mistake" point at the catalogue flow by name.
- Make catalogue hygiene visible at every consumer invocation, even when no changes are happening.

## Non-Goals

- Not changing the per-category 100-line cap or the 150-line AGENTS.md cap; this change tightens the trip wires, not the ceilings.
- Not introducing a new action verb; everything maps to existing `addcontent` / `curatecontent` / `addcategory` / `curatecategory`.
- Not automating `curatecontent`'s pre-merge rewrite. The hard-refusal is the right behaviour: refuse on the violation, surface the diff, let the operator pick `--force` only after review.

## Decisions

### D1 — Pre-trim at `addcontent` and `addcategory`

`addcontent --category <cat> --body <text>` and `addcategory --name <cat> --trigger <rule> --body <text>` SHALL pre-trim `<body>` BEFORE writing to `proposed/`:

- Drop duplicates: any bullet whose edit distance against existing bullets (curated *and* proposed, in the same category) is ≤30 chars folds into the existing bullet. Existing bullets survive; the new bullets are dropped. Recorded as `addcontent: dedupe <n> bullets vs curated`.
- Trim verbose tails: any bullet whose trailing `where X`, `in which case`, or `; note that Y` clause carries semantic content that's already in the bullet's leading commands gets flagged `addcontent: trim tail on <bullet index>` and the trailing clause is dropped. Operator can override with `--no-trim-tails` per call.
- Per-bullet length: any bullet >200 chars is split at the first sentence boundary and the split half becomes a new bullet. If still >200 chars in either half, refuse and surface `addcontent: bullet too long (≥200 chars after split)` — operator decides.

The trim pass is logged in the addcontent / addcategory completion summary so operators see exactly what was cut.

### D2 — Hard refusal at `curatecontent` and `curatecategory`

`curatecontent <ref>` SHALL refuse the merge and surface a trim diff if:

- merged output >100 lines (D11 cap)
- any bullet in the merged output >200 chars
- merge would create a near-duplicate rule (≤30 char edit distance) with an existing bullet that survives the merge

The refusal message is the same shape as `addcategory` rejection: list each violation with a `Suggested fix:` line. The operator can override with `--force`, but `--force` only applies to a curated cap violation (file >100 lines or bullet >200 chars), NEVER to a missing-`trigger:` field failure (that's a hard contract violation).

`curatecategory --name <cat>` enforces the same caps on the resulting curated file.

### D3 — Catalog self-discipline scan at `/update-agents`

`/update-agents` walks every `prompt-catalogue/curated/*.md` after the splice pass and reports a `Catalog self-discipline check:` section in the completion summary with one line per curated file. Per file:

- `curated/<cat>: ok` — passes all rules
- `curated/<cat>: 234 lines (cap 100)` — over the cap (does NOT block the splice; reports only)
- `curated/<cat>: bullet 3 exceeds 200 chars` — flagged
- `curated/<cat>: near-duplicate vs bullet 1 (edit distance 18)` — flagged
- `curated/<cat>: missing trigger field` — HARD case, splice still completes but the file is named in the summary as a contract violation

The scan is read-only; it does NOT refuse the `/update-agents` invocation. Operators see hygiene drift in the consumer's report.

### D4 — Rewriting `build-error-feedback-loop`

The curated entry is rewritten to direct mistakes through `/refresh-agents-content` and to forbid direct-write to AGENTS.md or `curated/`. New body:

```
## Build Error Feedback Loop

When the user reports a build error caused by something the agent did, or any mistake pattern the agent could repeat, route the rule through the catalogue flow rather than editing AGENTS.md directly:

1. Pick the most-relevant existing curated category (e.g. python-project, openspec-driven). Prefer reuse over creation.
2. Invoke `/refresh-agents-content addcontent --category <cat> --body "<one-or-two-sentence rule>"` to stage the proposed rule in `prompt-catalogue/proposed/<cat>.md`.
3. If no existing category fits, invoke `/refresh-agents-content addcategory --name <derived> --trigger "<evidence-derived rule>" --body "<starter>"` to propose a new category.
4. Tell the user what you staged and the absolute path. Do NOT splice the rule into AGENTS.md, into `prompt-catalogue/curated/`, or into any sibling skill file.
5. Operator reviews via `curatecontent` / `curatecategory` later.

**Never** hand-write to `<agent-root>/AGENTS.md` outside the `/update-agents` workflow.
**Never** hand-write to `prompt-catalogue/curated/*.md` outside `/refresh-agents-content curatecontent` / `curatecategory`.
**Never** embed consumer-facing prompt bodies in `.claude/skills/<name>/SKILL.md`.
```

Default-on trigger stays unchanged.

### D5 — `browsecontent` self-discipline tagging

When `browsecontent` inspects a curated file, it tags the diff with `self-discipline violation: <category>` if the curated file fails the catalog self-discipline check (D3). The tag is appended to the existing `[catalogue:<cat>]` tag. Operator-visible; the tag does not block the diff report.

### D6 — Catalogue self-discipline rules are documented in the operator entry point

`/refresh-agents-content/SKILL.md` opens with a "Catalogue self-discipline" section listing the four rules this change introduces (per-bullet length ≤200 chars, dedupe ≤30 char edit distance, mandatory file size ≤100 lines, mandatory `trigger:` field). The section is short (≤15 lines) so it stays operational, not behavioural — this aligns with requirement #7.

## Risks / Trade-offs

- **Operator friction.** A hard refusal at `curatecontent` is faster for the system than for the operator. The `--force` opt-in is the safety valve but increases the chance of post-hoc reasoning. Mitigation: the trim diff is the same shape as the proposed entry diff, so operators can compare before forcing.
- **Per-bullet length is heuristic.** A rule longer than 200 chars might be genuinely required. Split-at-first-sentence keeps the imperative anchor and lets the second sentence stand alone, but the split introduces a near-duplicate risk by definition (the bullet's first sentence is now a bullet, and the second sentence is too). The dedupe rule (≤30 char edit distance) folds the split halves back together unless they diverge enough; if they don't diverge, the split is suppressed.
- **Self-discipline check at `/update-agents` is informational, not blocking.** A curated entry that exceeds the cap will still splice. Operators will see the warning; the actual fix is `curatecontent --category <cat>`. We chose informational because blocking `/update-agents` on a catalogue hygiene problem would leave a consumer's repo without a regenerated AGENTS.md, a worse outcome than a flagged-but-still-emitted file.

## Migration Plan

1. Implement the SKILL and catalogue updates under `openspec/changes/catalogue-write-discipline/`.
2. Re-run the catalog self-discipline scan against the existing 9 curated files to record a baseline. Any existing file that fails the check is named in the change's completion summary; the operator decides whether to fix forward or accept the report.
3. Smoke verify against `/tmp/smoke-catalogue-discipline/` for: `addcontent` dedupe; `addcontent` long-bullet split; `curatecontent` refusal at >100 lines; `curatecontent --force` override; `curatecontent` refusal at missing-`trigger:` (no `--force` override accepted); `/update-agents` consumer invocation with completion summary listing `Catalog self-discipline check:`.
4. Validate + archive.

## Open Questions

- Should the catalog self-discipline scan also walk `proposed/`? My current draft scopes it to `curated/` only because consumers only read `curated/`. If operator experience shows `proposed/` hygiene matters too, a follow-up extension can scan both.
- Is the 200-char bullet cap too tight for compound imperative rules (e.g. a rule that lists three commands)? The trim pass splits at sentence boundaries; a triple-imperative bullet becomes three single-imperative bullets after the split. The operator can stitch them back via `curatecontent` if the operationally correct form really is one bullet.
