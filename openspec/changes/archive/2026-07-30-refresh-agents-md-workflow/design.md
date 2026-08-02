# Design: Sourced Principles + Refresh Workflow

## Context

`/generate-agents` (archived change `generate-agents-md`) ships with an embedded best-practices checklist and a reference-source list. The embedded content was generic ("imperative voice", "prefer real examples") rather than concrete or attributed. Two risks:

1. The workflow can't defend its guidance; if a user asks "why this rule?", there is no traceable answer.
2. As the public ecosystem evolves (new research, new practitioner consensus, deprecated patterns), the embedded guidance will drift without a runnable way to detect and apply updates.

This change addresses both. The first by citing sources inline; the second by shipping a separate `/generate-agents-refresh` skill that re-discovers and proposes updates through the project's OpenSpec change lifecycle.

## Goals / Non-Goals

**Goals:**

- Replace the embedded best-practices checklist with 16 source-attributed principles.
- Add a writing-order list backed by blakecrosley's synthesis and the GitHub Engineering team's analysis of 2,500+ repositories.
- Ship a manual refresh workflow `/generate-agents-refresh` that re-fetches the canonical + practitioner page set, diffs live principles against embedded ones, and proposes updates through OpenSpec.
- Keep the refresh workflow read-only by default: it diffs and reports. It only writes when the user explicitly accepts the proposed update.
- Honor the project's "every behavior change goes through openspec" rule even for refreshes.

**Non-Goals:**

- Scheduled automation. The user defers cadence.
- Auto-merging of refresh results.
- Refreshing the consumer project's AGENTS.md from inside the refresh workflow (that is the job of `/generate-agents` in update mode).
- New public sources beyond the six already chosen; the source set is the authority. Adding a new source is its own OpenSpec change.

## Decisions

### D1: Six sources is the authority set

The refresh workflow fetches exactly these six sources:

1. agents.md open standard — `https://agents.md/` and `https://github.com/agentsmd/agents.md`.
2. Builder.io — `https://www.builder.io/blog/agents-md`.
3. MorphLLM — `https://www.morphllm.com/agents-md-guide`.
4. blakecrosley — `https://blakecrosley.com/blog/agents-md-patterns`.
5. ASDLC.io — `https://asdlc.io/practices/agents-md-spec/`.
6. BetterClaw — `https://www.betterclaw.io/blog/agents-md-best-practices`.

Supporting context (Gloaguen et al. 2026, Princeton study, GitHub Engineering 2,500-repo analysis) is referenced via the practitioner pages; the refresh does not fetch them directly because they're cited through those pages.

**Why:** a fixed source set is auditable and reproduces the same diff every time. Adding a source is a behavior change.

### D2: Refresh writes through OpenSpec

When the user accepts a proposed principle diff, the refresh workflow stages an OpenSpec change under `openspec/changes/refresh-agents-md-content-<date>/`, with a delta spec that MODIFIES the `agents-md-generation` capability, then `openspec archive`s it. SKILL.md updates happen inside that change's apply step.

**Why:** consistent with the repo's "every behavior change goes through openspec" rule, and gives the user the standard OpenSpec review surface (show / validate / archive).

### D3: Refresh is read-only by default

The skill runs fetch + diff + report in step 1. Step 2 (propose) is gated on an explicit user decision in the conversational summary. Step 3 (write) only runs inside an OpenSpec change.

**Why:** auto-applying refreshes would silently mutate `/generate-agents`'s behavior, which violates the workflow's own "do not silently rewrite correct content" rule.

### D4: Source update is itself an OpenSpec change; refresh is just the trigger

The refresh workflow proposes; the project's `openspec` workflow applies. The refresh workflow never edits `openspec/specs/` directly (the repo's rule: only `openspec archive` writes there). It can create new change directories under `openspec/changes/`.

**Why:** keeps the rule "Never hand-edit openspec/specs/" intact and the standard review surface uniform.

### D5: Diff language is plain text, not a complex diff tool

The skill presents the diff as numbered additions ("3 new principles"), numbered refinements ("principle #7 wording tightened"), and numbered removals ("betterclaw's #10 superseded by asdlc's #8, recommend drop"). No patch output.

**Why:** keeps the user's decision space readable; a unified diff on prose is harder to evaluate than a numbered summary.

## Risks / Trade-offs

- **[Risk]** Source URL shapes change, breaking fetches. → **Mitigation**: the workflow records last-fetched timestamps; on hard 4xx / 5xx it reports the failure per the spec and stops with no proposed update.
- **[Risk]** Refresh proposes a change that weakens the mandated baseline or collapses the conditional catalog. → **Mitigation**: refresh is only allowed to update the "Sourced principles" + "Writing order" + "Reference sources" sections inside SKILL.md. The mandated baseline and conditional catalog are out of scope for any refresh; they require manual edits through their own OpenSpec change.
- **[Risk]** Refresh fetches drift away from principles due to author rewrites. → **Mitigation**: each principle's source URL is cited inline; if the user disagrees with a principle's current wording, they accept the diff or don't.
- **[Risk]** Future practitioner sources contain conflicting advice. → **Mitigation**: the current set already has known conflicts (betterclaw's hand-written emphasis vs. ASDLC's LLM-as-draft emphasis); refresh presents conflicts explicitly in the diff summary, not silently picking a side.

## Migration Plan

This change adds files and updates one existing skill. No data migration.

- Existing `/generate-agents` invocations continue to work; the upgraded sourced-principles checklist is a richer scoring rubric, not a behavior change visible to the user.
- New `/generate-agents-refresh` is opt-in; nothing in `/generate-agents` triggers it automatically.

Rollback is `git revert`-equivalent removal of the two `.claude/agents-md-refresh/*` files plus a re-archive of the prior `agents-md-generation` spec. The archived `refresh-agents-md-workflow` change can be replayed anytime.

## Open Questions

- Cadence (daily / weekly / monthly / on-demand). Deferred to the user.
- Notification path for "principle drift detected". Probably a logged refresh proposal the user can scan next session. Out of scope here.
- Whether to support a `--source <url>` flag for ad-hoc source inclusion. Resourceful agents might want this; deferred until a concrete need surfaces.
