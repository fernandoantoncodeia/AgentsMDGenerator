# Design: `/generate-agents` Workflow

Status: implementation target for change `generate-agents-md`.

## Context

The repo ships a bundle of OpenSpec workflows. Each workflow exposes a Claude command (`.claude/commands/opsx-*.md`) and a Claude skill (`.claude/skills/openspec-*/SKILL.md`). User feedback drives the need for a parallel workflow whose purpose is to generate and maintain an AGENTS.md in a consumer project. The workflow must be re-runnable on existing repos to optimize content as the project evolves.

Two design considerations drive most decisions:

1. **Reference source strategy** — the workflow needs high-quality best-practice guidance. Running a live web search on every invocation is slow and non-deterministic. Embedding curated guidance plus reference links is reliable and fast; an optional live-refresh path covers the case where embedded guidance goes stale.
2. **Mandated vs. optional content** — only one section ("be a colleague") is mandated in every output. The other items from the maintainer's usual checklist are best practices to apply only when their trigger fires in the target project. This avoids bloating AGENTS.md in non-relevant repos.

## Goals / Non-Goals

**Goals:**
- New Claude command `/generate-agents` invokable at project start or any time.
- New Claude skill `generate-agents-md` carrying the workflow logic, embedded checklist, reference sources, mandated baseline, and conditional catalog.
- Reliable and deterministic generation that does not depend on live network access by default.
- Update mode that trims verbose or non-imperative content instead of just appending.
- Workflow reports what it did so the user can trust the result.

**Non-Goals:**
- Multi-platform distribution (Factory / Codex / other agents) in this iteration. Claude only, matching user request. The pattern is easy to port later.
- Automatic CLAUDE.md mirroring. The workflow MAY offer to mirror but SHALL NOT do it unprompted.
- Authoring application code in the consumer project. The workflow writes only AGENTS.md (and optionally a CLAUDE.md mirror).
- Live web refresh on every run; only when explicitly requested or staleness is detected.

## Decisions

### D1: Two-deliverable layout (Claude command + Claude skill)
Two files, mirroring the existing bundle layout for OpenSpec workflows:
- `.claude/commands/generate-agents.md` — entry point (frontmatter + brief behavior pointer to the skill).
- `.claude/skills/generate-agents-md/SKILL.md` — full body (workflow, embedded guidance).

**Why:** consistent with the existing repo pattern; lets Claude resolve the skill independently of the command.
**Alternatives considered:** single combined file (rejected: breaks the bundle pattern and reduces portability).

### D2: Embedded best-practices checklist, optional live refresh
The skill ships with a curated best-practices checklist and a small set of public reference URLs (agents.md open standard, builder.io guide, morphllm AGENTS.md vs CLAUDE.md, asdlc.io spec, blakecrosley patterns, betterclaw). Live web search runs only when the user asks (`--refresh`) or when the workflow suspects staleness.

**Why:** deterministic by default; live path available for currency.
**Alternatives considered:** always live (rejected: slow, flaky, non-reproducible); never live (rejected: ignores currency).

### D3: Single mandated section, conditional catalog
Mandated in every output: the "be a colleague" baseline. Everything else from the maintainer's checklist is in a conditional catalog whose triggers fire only when relevant.

**Why:** keeps AGENTS.md short and high-signal across diverse projects, while letting the workflow apply mature guidance where it fits.
**Alternatives considered:** include every section always (rejected: bloats files for unrelated projects and contradicts best-practice guidance of "concise, imperative").

### D4: Create vs. update mode branched at detection
The workflow inspects the target path at run time. Missing file → create mode (build from scratch). Existing file → update mode (read, evaluate against checklist, trim, preserve project-specific rules, apply trigger-fired catalog sections, write in place).

**Why:** a single invokable workflow covers both "bootstrapping" and "drift repair" without burdening the user to choose.
**Alternatives considered:** separate commands for create vs. update (rejected: doubles surface area for a tiny choice the workflow can make itself).

### D5: Update mode performs a trim pass after write
After updating AGENTS.md, the workflow re-reads the entire file and removes verbose, redundant, or non-actionable content. This honors the user's stated principle that AGENTS.md is for AI agents and must stay imperative.

**Why:** matches the maintainer's mandated-as-default content rule ("cut anything verbose, redundant, non-actionable after every edit").
**Alternatives considered:** trim only at write time (rejected: misses content emitted by the catalog application step that may, in combination, become redundant).

### D6: Faithful completion reporting
The workflow reports: create-or-update, sections added, sections preserved verbatim, sections trimmed, whether a refresh was performed, and any side effect suggestions (e.g. CLAUDE.md mirror).

**Why:** mirrors the "be a colleague" stance the workflow itself encodes — users benefit from accurate reporting.
**Alternatives considered:** terse single-line confirmation (rejected: leaves the user guessing about what changed).

## Risks / Trade-offs

- **[Risk]** Embedded reference links rot or become outdated. → **Mitigation:** the optional live refresh path; staleness heuristic; the listed sources are stable URLs (agents.md site, GitHub canonical).
- **[Risk]** The conditional catalog stays useful as the maintainer's checklist evolves. → **Mitigation:** catalog lives inside the skill; updating it is a small skill edit. Future changes go through OpenSpec to keep spec and skill in sync.
- **[Risk]** Update mode rewrites correctly-written content into something weaker. → **Mitigation:** the spec encodes "MUST NOT silently rewrite correct content into something false or weaker"; the trim pass should preserve strong imperative rules verbatim.
- **[Risk]** A consumer project with no AGENTS.md never gets the workflow installed, so it never runs. → **Mitigation:** out of scope for this iteration; the workflow itself is the seed once `/generate-agents` is invoked.

## Migration Plan

This change introduces new files only. No existing files are modified. On archive:
- `openspec/changes/archive/generate-agents-md/` receives a snapshot.
- `openspec/specs/agents-md-generation/spec.md` is created from the delta spec.

No rollback concerns beyond `git revert`-equivalent removal of the two `.claude/*` files if needed; the archived change can always be replayed.

## Open Questions

None at implementation time. The mandated-section phrasing will be drawn from the user's requirements verbatim/lightly adapted; comments in the skill will mark adaptations vs. verbatim quotes.
