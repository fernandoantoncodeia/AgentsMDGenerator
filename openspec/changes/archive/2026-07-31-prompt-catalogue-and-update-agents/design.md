# Design: Prompt Catalogue + Two-Flow Architecture

## Context

The workflow's `/generate-agents` SKILL.md today embeds the conditional catalog (C1-C9) inline. Each catalog entry is a small block of prose the workflow reads at runtime to decide which sections to splice into the consumer's AGENTS.md. Today there is no operator-curated pipeline: editing the catalog means editing the skill, which is a workflow behavior change and must run through the OpenSpec lifecycle. Operators have no place to draft a candidate prompt, no diff surface, no promote/demote discipline, and no quick browse of "what's currently active vs. what's pending review."

`/generate-agents-refresh` (archived under `agents-md-refresh` capability) currently re-fetches the six-source authority set and proposes updates to the Sourced Principles list (workflow-internal). That surface — keeping the workflow's own meta-guidance current against live URLs — is unrelated to the project-level prompt catalogue but visually adjacent, hence the user's clarification that the two lifecycles must not be conflated.

The user has explicitly cleared the architecture in three messages: (a) prompts MUST live in a catalogue and MUST NOT live in the skills (requirement #7); (b) `browsecontent` does the work that `/generate-agents-refresh` did today, but results in `addcontent` calls into `proposed/` rather than OpenSpec-staged changes; (c) catalogue changes do NOT go through OpenSpec but DO go through proposed/curated operator review. Two flows collapse the existing pair: `/update-agents` (consumer project facing) and `/refresh-agents-content` (catalogue operator facing).

## Goals / Non-Goals

**Goals:**

- Two artefacts: `prompt-catalogue/{curated,proposed}/<category>.md`. Browsable in the filesystem by humans; the folder name is invariant.
- Two slash commands: `/update-agents` and `/refresh-agents-content`. The existing `/generate-agents` and `/generate-agents-refresh` are deleted; their skills `generate-agents-md/SKILL.md` and `agents-md-refresh/SKILL.md` are deleted; their capabilities `agents-md-generation` and `agents-md-refresh` are MODIFIED, not archived.
- Five actions under `/refresh-agents-content`: `addcontent`, `curatecontent`, `browsecontent`, `addcategory`, `curatecategory`. Each is a documented verb with clear pre/post state and clear write target (`proposed/` for everything except `curatecontent` and `curatecategory`, which move entries to `curated/`).
- `/update-agents` first invocation creates AGENTS.md; subsequent invocations refresh and detect applicable-but-not-yet-inserted categories. When a trigger-equivalent matches the scan but no curated category covers it, the workflow auto-emits `/refresh-agents-content addcategory --name <derived> --trigger "<evidence>" --body "<starter>"` so a placeholder lands in `prompt-catalogue/proposed/<derived>.md`. The curated set is unchanged at the moment of the `/update-agents` invocation; the operator curates via `curatecategory` later.
- Hard isolation: `/update-agents` MUST NOT read `prompt-catalogue/proposed/`. The contract is documented in the workflow and enforced by review of the skill body, not at the OS level (a hard file-system ACL would break ordinary browsing).
- The existing C1-C9 catalog content ships as initial `prompt-catalogue/curated/<category>.md` files (one markdown per category), so a fresh consumer install has a working default.
- Catalogue files adopt the same length discipline the workflow's own Sourced Principles cite: concise (target 30-50 lines, soft cap 150, hard cap 32 KiB), imperative voice, command-first where commands exist.
- The skill files kept under `.claude/skills/{update-agents,refresh-agents-content}/SKILL.md` contain operational content only — never consumer-facing prompt bodies (requirement #7).

**Non-Goals:**

- A pull-request style diff viewer or interactive merge tool. `curatecontent` merge-and-simplify is the operator's text editor plus their judgment.
- Cross-consumer catalogue sharing. Each consumer keeps its own `prompt-catalogue/`. Vendoring fresh content from upstream is operator-driven (and the skill suggests `browsecontent` as the way to surface suggestions from the live source set).
- A registry service that resolves `category:` IDs to content. Categories are local file names; resolution is by directory read.
- A web UI. Operators browse by filesystem; the change is meant to keep the surface easily browsable.
- Lifecycle integration between the consumer's `prompt-catalogue/` and the tool's `prompt-catalogue/`. Each consumer's catalogue is its own; the tool's bundled seeded `prompt-catalogue/` is what new installs receive.
- Auto-merging of `proposed/` items into the consumer's AGENTS.md. Proposed items MUST be curated first.

## Decisions

### D1: Two-folder catalogue layout

The catalogue lives at repo root: `prompt-catalogue/{curated,proposed}/<category>.md`. Categories are kebab-case; one markdown file per category, named after the category itself. The same `<category>.md` filename can exist in both `curated/` and `proposed/` simultaneously — that signals an item is awaiting curation while a related curated item is already in use.

**Why:** a flat folder of markdown files is the most universally browsable form — `ls`, a file tree, or any markdown-aware editor enumerates content. Two folders preserve the lifecycle gate without imposing any schema beyond a file per category.

Alternatives considered: a single folder with a YAML frontmatter `status:` field per file (rejected: harder to grep, harder to enforce isolation in tooling, hides state behind format); a SQLite index (rejected: operators do not want a database in the workflow).

### D2: Category file format

Each `<category>.md` file has the structure:

```markdown
---
title: <one-line title shown in AGENTS.md when spliced>
trigger: <the detection rule, e.g. "project contains *.py files">
---

<body content — concise, imperative, follow the workflow's sourced principles>
```

YAML frontmatter carries the minimum metadata the workflow needs to (a) name the section when splicing into AGENTS.md and (b) decide whether to splice it. Body content is the actual prompt.

**Why:** frontmatter is a stable machine-readable contract; body is free-form prose the workflow passes through verbatim. This matches patterns the workflow itself cites (SKILL.md frontmatter schema documented by MorphLLM).

Alternatives considered: splitting trigger into a separate `triggers/<category>.yaml` (rejected: splits the artifact in two, harder to keep in sync); embedding trigger logic in body prose (rejected: tooling has to parse prose).

### D3: Hard isolation contract, documented not enforced

`update-agents/SKILL.md` explicitly states "MUST NOT read `prompt-catalogue/proposed/`." The rule is repeated at the top of the skill, in the guardrails section, and in the completion-summary block.

**Why:** filesystem ACL-based isolation would break ordinary browsing and add operational overhead. Documented isolation + the discipline of an operator reviewing skill changes via the standard OpenSpec lifecycle is the right level of rigor in this design.

Alternatives considered: a build-time check that the skill never references `proposed/` (rejected: brittle, would need a custom linter; the rule is small enough to read in code review).

### D4: Catalogue does not pass through OpenSpec

Updating the catalogue contents is a content change to a project-level artefact. Per the user's clarification, the lifecycle for catalogue changes is:

1. Operator (or `/refresh-agents-content browsecontent`) writes new content into `prompt-catalogue/proposed/<category>.md` via `addcontent`.
2. Operator reviews via filesystem read.
3. Operator runs `curatecontent` to promote the entry, with merge-and-simplify against extant curated content.
4. `/update-agents` reads the curated set next invocation.

There is no `openspec archive` step. The OpenSpec lifecycle continues to govern *workflow* changes (this current change included).

**Why:** workflow behaviour lives inside this repo's CI discipline; catalogue content is operator-curated and lives alongside consumer projects. Mixing the two lifecycles confuses both.

Alternatives considered: routing catalogue writes through openspec (rejected: per user explicit "do not need to go through openspec"); routing openspec changes through the catalogue (rejected: openspec is the change tracker for workflow files specifically).

### D5: Five actions, each with a clear write-target contract

| Action | Reads | Writes | Operator gate |
|--------|-------|--------|---------------|
| `addcontent <text> --category <cat>` | existing curated + proposed for category | appends to `proposed/<cat>.md` | implicit (operator creates with intent to curate later) |
| `curatecontent <ref>` | curated/ + proposed/ for category | replaces curated entry with merge-and-simplified version; removes from proposed/ | required (this IS the curate gate) |
| `browsecontent` | six-source authority set + `prompt-catalogue/curated/<cat>/*.md` | emits `addcontent` calls (operator decides which to invoke) | implicit (browse-only by default; only writes via operator-confirmed `addcontent`) |
| `addcategory <name> <trigger>` | none | creates `proposed/<category>.md` with the proposed trigger; nothing yet in curated/ | required (a new category enters as proposed and must be curated before it splices) |
| `curatecategory <name>` | proposed entry for category | creates `curated/<category>.md` with the trigger; remaps entries that match by name/keyword to use it | required + operator validates each remap |

**Why:** each action has a single, narrow contract. Operators know exactly which write-path is touched. Skill bodies stay short because there's no overlapping semantics.

Alternatives considered: three actions (curate single/bulk/auto) (rejected: more action surface for marginal gain); one mega-action "manage" (rejected: operators want narrow, composable verbs).

### D6: /update-agents reads categories by trigger, never by content shape

`/update-agents` enumerates `prompt-catalogue/curated/*.md` and reads each file's `trigger:` frontmatter field. Decision: splice into AGENTS.md if the trigger matches the consumer project's scan; otherwise skip. The body content is concatenated verbatim into AGENTS.md, with the heading from `title:`.

Triggers are evaluated against a deterministic scan of the consumer project:
- presence of files (Python: `*.py`, etc.)
- presence of directories (`openspec/`, `docs/`, etc.)
- presence of manifests (`pyproject.toml`, etc.)

A trigger that needs more than these (e.g. "looks like FastAPI") is documented as a heuristic and treated as a soft signal — operators mark such categories with `trigger-confidence: heuristic` so the workflow reports rather than auto-splices.

**Why:** every category entry needs to be inspectable. Triggers in YAML frontmatter are deterministic; triggers that aren't deterministic are flagged so the operator can recognize them in the diff.

Alternatives considered: triggers as regex over filenames (rejected: paths differ across projects); triggers as runtime code invocations (rejected: catalogue would become a programmatic API, against the "browseable" goal).

### D7: C1-C9 → curated category seed

The existing C1-C9 content moves out of the SKILL.md into nine markdown files at `prompt-catalogue/curated/`:

- `build-error-feedback-loop.md`
- `short-and-imperative.md`
- `python-project.md`
- `windows-com.md`
- `self-documentation.md`
- `openspec-driven.md`
- `tool-erratic.md`
- `openspec-cli.md`
- `shell-tooling.md`

Each file's `trigger:` field encodes the rule currently listed in the SKILL.md. Each file's `title:` field is the section heading. Each file's body is the prose body of the current entry, lightly trimmed per the workflow's own principles.

**Why:** zero-day loss of capability: a fresh consumer install still gets all nine categories. The migration is a content move, not a rewrite.

Alternatives considered: rewriting the entries during the move (rejected: this is a structure change, not a content change; mixing the two risks silent drift).

### D8: Missing-applicable-category auto-add into `proposed/`

When `/update-agents` detects a trigger that matches the consumer project's scan but no curated category covers it, the workflow MUST auto-emit a `/refresh-agents-content addcategory` call that creates a placeholder entry in `prompt-catalogue/proposed/<derived>.md`. The auto-add carries:
- `--name <derived>` — pulled from the trigger evidence (e.g. `go-language` for Go files).
- `--trigger "<observed-evidence>"` — the exact evidence observed in the scan.
- `--body "<suggested>"` — a minimal starter body so the operator has something to refine, not a placeholder; the operator replaces it during `curatecategory`.

The auto-add lands ONLY in `proposed/`. The curated set is unchanged at the moment of `/update-agents` invocation. The completion summary lists each auto-add transparently:

```
Auto-added to proposed catalogue:
- go-language (matched by: *.go files present) -> /refresh-agents-content addcategory --name go-language --trigger "*.go files present" --body "<starter>"
```

**Why:** the catalogue's curation discipline protects the curated set because every operator-gated decision still happens at `curatecontent` / `curatecategory`. Auto-adding to `proposed/` is safe and keeps `/update-agents` advanceable without manual first-touch.

Alternatives considered:
- Auto-promote to curated — rejected: would breach the proposed/curated gate and silently inject unverified content into the next consumer's AGENTS.md.
- Report-only without writing — rejected: the user clarified detection must drive auto-add, since "categories themselves have a curation flow" — leaving the entry un-added gives the operator nothing to curate.
- Inline `proposed/<cat>.md` body content without using `addcategory` — rejected: bypasses the action gate; future action contracts would have to chase the same write path.

### D9: Existing `agents-md-refresh` capability survives with new semantics

The capability `agents-md-refresh` is MODIFIED rather than archived. Its previous semantics (refresh the workflow's embedded Sourced Principles against live URLs) are now performed by `/refresh-agents-content browsecontent`, but the workflow-embedded Sourced Principles still needs to stay current. The MODIFIED requirement narrows the capability's scope to: keep the workflow's Sourced Principles list inside `.claude/skills/generate-agents-md/SKILL.md` (now carried in `.claude/skills/update-agents/SKILL.md`) current against the live six-source authority set, and propose updates through OpenSpec like before.

**Why:** keeps the workflow's own meta-guidance in the same governance discipline (OpenSpec), distinct from the catalogue's Lifecyle.

Alternatives considered: archiving the capability (rejected: would have no governance for the workflow's own embedded principles); folding Sourced Principles into the catalogue (rejected: they describe how the workflow operates, not what to put in AGENTS.md — a category-level mismatch with catalogue scope).

### D10: Slash command file deletion is required

The superseded artefacts `.claude/commands/{generate-agents,generate-agents-refresh}.md` and the folders `.claude/skills/{generate-agents-md,agents-md-refresh}/` are deleted, not renamed. Renaming would leave collapsed content in the tree. The orphaned archived openspec changes stay in `openspec/changes/archive/` for history.

**Why:** collapsing into the two new flows, per the user's explicit ask. Operators aren't meant to find two commands doing the same thing.

Alternatives considered: keeping old as deprecated aliases that forward to new (rejected: the user said "dissapear and collapse" — explicit).

## Risks / Trade-offs

- **[Risk]** Operator makes a category too long, breaching the 150-line soft cap that the workflow's own Sourced Principles cite. → **Mitigation**: the workflow's own trim pass rule applies — when `/refresh-agents-content curatecontent` runs with merge-and-simplify, it actively shortens any entry over the cap and references the rule inline. Catalog files ship under the cap as a default; drift is visible during curation.
- **[Risk]** Two proposed entries are semantically equivalent but worded differently; merge-and-simplify produces a Frankenstein entry. → **Mitigation**: the operator curates `curatecontent`, so they are in the loop. The skill surfaces a noted "merged 2 entries" message so the operator knows.
- **[Risk]** Operator deletes a `curated/<category>.md` file out of band. Next `/update-agents` invocation just doesn't splice it. No alert. → **Mitigation**: documentation in the skill notes that deletions are silent; operators wanting in-band removal use `curatecontent` with empty body or move to `proposed/` first.
- **[Risk]** A trigger's regex is too greedy. → **Mitigation**: triggers live in YAML frontmatter under operator control; tests via `browsecontent` ("would this trigger fire on a sample project?") before curation.
- **[Risk]** `/refresh-agents-content browsecontent` floods `proposed/`. → **Mitigation**: `browsecontent` is read-only by default; only operator-confirmed follow-up `addcontent` calls write to `proposed/`. The default behaviour avoids overflow.
- **[Risk]** Operator confusion: catalogue vs. openspec lifecycles. → **Mitigation**: the skill is explicit at the top: "Catalogue updates are NOT openspec; they go through the proposed → curated gate." AGENTS.md in this repo is updated to surface the distinction.
- **[Risk]** Migration finds the C1-C9 content was hand-edited in prior changes. → **Mitigation**: the content is moved from the existing SKILL.md verbatim per the prior apply phase; any prior edits are preserved by reading current state first. If the SKILL.md was edited between change-archives and now, that drift is captured in the migration checklist.
- **[Risk]** Two skills both reference the same authority set (six sources). Drift between them. → **Mitigation**: `/refresh-agents-content browsecontent`'s source list is the canonical reference; `/update-agents` does not fetch sources at all (only reads catalogue), so it doesn't need its own source list. Single source of authority.

## Migration Plan

This change is structural. Migration has three phases:

1. **Pre-implementation read.** Read the current `.claude/skills/generate-agents-md/SKILL.md` and extract the C1-C9 content into nine markdown files matching D7 exactly. No edits.
2. **Apply phase.** Per the implementation tasks: create `prompt-catalogue/curated/`, populate with the seeded content from step 1, create `prompt-catalogue/proposed/` with a `.gitkeep`. Create new slash commands and skills. Delete the superseded files. Update the synced specs.
3. **Post-archive.** No data migration is required for consumer projects; the next time a consumer installs the new workflow, they pick up the seeded catalogue.

Rollback strategy: archived openspec changes are immutable. The two old archived changes (`generate-agents-md`, `refresh-agents-md-workflow`) stay as history. Reverting only means: ship a follow-up change restoring the deleted files. No `state` recovery needed.

## Open Questions

- Whether `addcategory`'s auto-addition (D8) should also re-suggest the same category on subsequent `/update-agents` invocations before the operator curates, or only on the first detection per trigger. Default: only first detection; subsequent invocations see the auto-suggestion as a no-op.
- Whether the body supplied to a `curatecategory` call (or pre-populated by `addcategory`) MUST match the `<category>`-named entry's body shape, or is freely draftable. Default: freely draftable and re-formable until curated.
- How to handle the case where the operator's `addcategory --body` content from `/update-agents`'s auto-add is empty or trivial. Default: the workflow should refuse to emit an `addcategory` call with empty body; it should report the trigger evidence and ask the operator for a starter body inline before the next invocation.
