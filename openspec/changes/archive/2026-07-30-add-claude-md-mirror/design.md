# Design: Auto-Write the CLAUDE.md Mirror

## Context

Claude Code does not read `AGENTS.md` natively. It picks up the content only when the consumer repo has a `CLAUDE.md` whose first line is `@AGENTS.md` (Claude Code's `@imports` syntax — first hop picks up the file). Today `/generate-agents` only *suggests* this mirror in its completion summary; consumers forget, so most generated AGENTS.md files stay invisible to Claude Code. The user explicitly asked for the mirror to be present "in all cases" so this change moves the mirror from a soft suggestion into a hard artifact of the workflow.

The proposal already establishes the why. This design covers the how: how the workflow detects and writes the mirror, what it does when the file already exists, and what the new completion-summary row looks like.

## Goals / Non-Goals

**Goals:**

- `CLAUDE.md` exists next to `AGENTS.md` after every `/generate-agents` invocation, in both create and update modes.
- The file starts with `@AGENTS.md` (Claude Code's import syntax).
- The default text-import pattern is preferred over a symlink: more portable across Windows + macOS + Linux, no broken-symlink failure modes.
- Pre-existing `CLAUDE.md` content (anything else the consumer wrote there) is preserved.
- The completion summary lists the mirror as a written/refreshed/already-valid row, not a "suggestion."
- The previous "Do NOT auto-mirror" guardrail is revoked; this is the new behavior.

**Non-Goals:**

- A `--no-claude-md` opt-out flag. The user's directive was "in all cases"; adding an opt-out introduces complexity without a request.
- Editing every consumer file that imports `AGENTS.md` differently (e.g. `.cursorrules` symlinks). Those are related but out of scope.
- A `CLAUDE.local.md` (Claude Code's user-scope override). The mirror is project-scope only; consumers can add their own `CLAUDE.local.md` independently.
- Touching the workflow's own `/generate-agents` skill or any file outside the consumer repo's two files. The mirror logic lives only in the consumer-repo step.
- Bumping any prior generation. The mirror logic only takes effect on the next invocation. Existing AGENTS.md consumers do not get retroactive CLAUDE.md.

## Decisions

### D1: Text-import mirror, not symlink

The mirror file is a regular text file containing the literal line `@AGENTS.md` (followed by a trailing newline). It is NOT a symlink.

**Why:** text works on every host (Windows, macOS, Linux). Symlinks fail on Windows without elevation or developer-mode, and produce cryptic errors in CI. Claude Code's `@imports` is the documented cross-tool option (per the morphllm AGENTS.md vs CLAUDE.md comparison and the agents.md open standard).

Alternatives considered: a symlink (`CLAUDE.md → AGENTS.md`) — rejected for portability and discoverability; a copy of AGENTS.md contents — rejected because it duplicates the source of truth and would drift.

### D2: Resolve CLAUDE.md with four deterministic cases

When the workflow reaches the mirror step, it inspects the consumer repo root and applies one of four branches:

| Case | Detection | Action |
|------|-----------|--------|
| `CLAUDE.md` does not exist | `not path.exists()` | Create with content `@AGENTS.md\n` |
| `CLAUDE.md` is a symlink | `path.is_symlink()` | Leave untouched, mark "already-valid (symlink)" |
| `CLAUDE.md` first line trims to `@AGENTS.md` | `read_text().splitlines()[0].strip() == "@AGENTS.md"` | Leave untouched, mark "already-valid" |
| `CLAUDE.md` exists with other content | any of the above failing | **Prepend** `@AGENTS.md\n\n` and write the original content below, mark "refreshed" |

**Why prepending instead of replacing:** the consumer may already use `CLAUDE.md` for project-specific Claude instructions. Replacing would silently destroy that work, violating the workflow's own rule against silently rewriting correct content.

Alternatives considered: replace (`@AGENTS.md\n` only) — rejected, destructive; refuse + report — rejected, the user's directive is "in all cases."

### D3: Empty or whitespace-only CLAUDE.md is treated as missing

If the file exists but reads empty or only whitespace, the workflow treats it as not-present and creates it fresh with `@AGENTS.md\n`. Report as `created` in that case.

**Why:** an empty marker file conveys no intent; creating a clean one is consistent with the missing-file case.

### D4: Reporting row replaces the prior "Suggestion" line

The completion summary's `Suggestion` row is replaced by a first-class `Mirror` row with one of four values:

- `created at CLAUDE.md` — file did not exist before, now contains `@AGENTS.md`.
- `refreshed CLAUDE.md (preserved N existing lines)` — prepended to existing content.
- `already-valid at CLAUDE.md` — first line is `@AGENTS.md`, no change.
- `already-valid symlink at CLAUDE.md` — symlink to AGENTS.md or another path. Symlink target is read with `os.readlink` and surface as a parenthetical, not required to match AGENTS.md.

**Why:** the prior "SHOULD NOT auto-mirror; MAY suggest" guardrail was the root cause of the discovery most consumers had no CLAUDE.md. Reporting the mirror as an actual write makes the workflow's behavior visible without requiring the user to act on a suggestion.

### D5: Mirror happens after AGENTS.md, before the trim pass

In create mode, the order is: write AGENTS.md → mirror CLAUDE.md → trim pass on AGENTS.md. In update mode: read existing AGENTS.md → score against checklist → mirror CLAUDE.md → apply updates to AGENTS.md → trim pass.

**Why:** the mirror step must happen after we've decided AGENTS.md will exist at the resolved path. Mirroring before AGENTS.md would create a dangling `@AGENTS.md` import pointed at a non-existent file.

### D6: Mirror failure aborts the workflow with a precise cause

If the mirror step fails (permission error, read-only filesystem, missing parent dir for the resolved path), the workflow aborts and reports the failure. AGENTS.md may already have been written; the completion summary makes it explicit which step succeeded and which did not.

**Why:** partial state ("AGENTS.md is there but the mirror is not") is the failure mode the migration was supposed to eliminate. Reporting it precisely is consistent with the workflow's mandate ("be a colleague — report outcomes faithfully").

### D7: Mirror respects an opt-out only at the consumer's own hand

The workflow does not read any "no mirror" config from the consumer repo. If the consumer wants to opt out, they can set the CLAUDE.md first line to something other than `@AGENTS.md` and then run `/generate-agents` once more — D2 will treat that as the "exists with other content" case and prepend `@AGENTS.md`, which re-enables the mirror.

**Why:** this trade-off — a workflow that always wins over a consumer's hand edit — is consistent with the user's "in all cases" directive. If they want a softer behavior later, it's a future OpenSpec change.

## Risks / Trade-offs

- **[Risk]** A consumer's existing CLAUDE.md has content Claude Code interprets as instructions. Prepending `@AGENTS.md` keeps that content but makes the file longer. → **Mitigation:** Claude Code's `@imports` follow a documented hop limit; prepending does not change semantics for the existing content. We do prepend carefully (`@AGENTS.md\n\n`, two newlines) so the existing content reads naturally.

- **[Risk]** Symlink consumers may have broken targets (e.g., `CLAUDE.md → AGENTS.md` when AGENTS.md lives at a different path). → **Mitigation:** we do not chase or repair symlinks. The workflow reports the symlink target as a parenthetical and exits. The consumer decides whether to keep or replace the symlink on their next review.

- **[Risk]** File-permission failures (read-only CLAUDE.md, permission denied on the parent dir). → **Mitigation:** mirror failure aborts the workflow with the exact cause; the completion summary is honest about the partial state.

- **[Risk]** Consumer runs `/generate-agents` from a subdirectory with `--path docs/team/AGENTS.md`. The mirror would write CLAUDE.md to the CWD, which may not be where the consumer expects. → **Mitigation:** the mirror step writes `CLAUDE.md` at the SAME resolved root where AGENTS.md is written. If the user passed an explicit path that is NOT the consumer root, the mirror is skipped and the completion summary reports "skipped mirror — AGENTS.md not at consumer root." Future enhancement: a `--mirror-root <path>` flag. Out of scope now.

- **[Risk]** Edge case where resolve-target is a special filesystem (e.g., a non-writable repo in CI). → **Mitigation:** mirror-failure abort path applies; the workflow's reporting busts the partial state.

## Migration Plan

This change adds behavior to `/generate-agents`; it does not migrate any existing AGENTS.md consumers' CLAUDE.md files.

- After archive, the next `/generate-agents` invocation against any consumer repo will create or refresh CLAUDE.md alongside AGENTS.md.
- Existing consumers with no CLAUDE.md: next invocation creates one.
- Existing consumers with content CLAUDE.md: next invocation prepends `@AGENTS.md`.
- Existing consumers with a symlink: next invocation leaves it alone, reports "already-valid symlink."

Rollback is the standard "revert the OpenSpec change and re-archive `agents-md-generation`" path. No data migration to undo.

## Open Questions

- Should there be a future "always write AGENTS.md to consumer root even when --path is supplied" companion flag, so the mirror can always run? Deferred until a concrete need surfaces.
- Is `AGENTS.override.md` (Codex-specific, mentioned in blakecrosley's patterns post) worth a parallel mirror at `CLAUDE.local.md`? Deferred — the consumer can author that themselves when they need it.
