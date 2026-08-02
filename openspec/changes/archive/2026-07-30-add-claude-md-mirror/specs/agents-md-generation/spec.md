# agents-md-generation delta spec

## MODIFIED Requirements

### Requirement: Workflow reports what changed and why
When the workflow writes or updates AGENTS.md, it SHALL report a short summary of:
- Whether it created a new file or updated an existing one.
- Which mandated and conditional catalog sections ended up in the output.
- Which existing rules were trimmed, rewritten, or preserved verbatim.
- Whether a live refresh was performed and against which sources.
- The CLAUDE.md mirror state and outcome (created, refreshed with N preserved lines, already-valid, or already-valid symlink).

#### Scenario: Successful generation report
- **WHEN** the workflow completes successfully
- **THEN** it produces a summary that lists the sections present in the file, the changes applied to existing content, and any side effects (CLAUDE.md mirror outcome, refresh invocation)

#### Scenario: Failure report
- **WHEN** the workflow cannot write the file (e.g. permission error, invalid path)
- **THEN** it reports the failure with the exact cause and does not claim success

#### Scenario: Mirror failure makes partial state explicit
- **WHEN** AGENTS.md was written successfully but the CLAUDE.md mirror step failed
- **THEN** the completion summary names both outcomes: which file succeeded, which failed, and the exact cause of the mirror failure

## ADDED Requirements

### Requirement: One-line CLAUDE.md mirror is always present at the consumer root
The workflow SHALL guarantee that a `CLAUDE.md` file exists at the consumer repo root alongside AGENTS.md after every invocation, in both create and update modes. The mirror SHALL be a regular (non-symlink) text file whose first line, after trimming whitespace, is exactly the literal string `@AGENTS.md` (Claude Code's `@imports` syntax). The mirror SHALL be written at the same resolved consumer root where AGENTS.md is written; if AGENTS.md is written to a non-root path supplied via a `--path`-style argument, the mirror SHALL be skipped and the completion summary SHALL report the skip with the exact reason.

#### Scenario: Mirror created when CLAUDE.md does not exist
- **WHEN** the workflow reaches the mirror step and `CLAUDE.md` does not exist at the consumer root
- **THEN** the workflow creates `CLAUDE.md` whose content is exactly `@AGENTS.md\n` and reports `created at CLAUDE.md`

#### Scenario: Mirror leaves existing valid CLAUDE.md untouched
- **WHEN** `CLAUDE.md` exists at the consumer root and its first line, after trimming whitespace, equals `@AGENTS.md`
- **THEN** the workflow does not modify the file and reports `already-valid at CLAUDE.md`

#### Scenario: Mirror leaves symlink CLAUDE.md untouched
- **WHEN** `CLAUDE.md` at the consumer root is a symbolic link
- **THEN** the workflow does not modify the link, does not chase its target, and reports `already-valid symlink at CLAUDE.md` with the link target in parentheses

#### Scenario: Mirror preserves pre-existing content by prepending
- **WHEN** `CLAUDE.md` exists at the consumer root, is not a symlink, and its first line, after trimming whitespace, is not `@AGENTS.md`
- **THEN** the workflow prepends `@AGENTS.md\n\n` followed by the original file content (preserving every byte), writes the result, and reports `refreshed CLAUDE.md (preserved N existing lines)` where N is the count of non-empty original lines

#### Scenario: Empty or whitespace-only CLAUDE.md is treated as missing
- **WHEN** `CLAUDE.md` exists at the consumer root, is not a symlink, and reads as empty or only whitespace
- **THEN** the workflow replaces its content with `@AGENTS.md\n` and reports `created at CLAUDE.md` (not `refreshed`)

#### Scenario: Mirror skipped when AGENTS.md target is not the consumer root
- **WHEN** the user invokes `/generate-agents` with a path argument that resolves outside the consumer repo root (e.g. `docs/team/AGENTS.md`)
- **THEN** the workflow skips the mirror step and the completion summary reports `mirror skipped — AGENTS.md target <resolved path> is not the consumer root`

#### Scenario: Mirror failure aborts the workflow
- **WHEN** the mirror step raises an exception (permission denied, read-only filesystem, missing parent directory)
- **THEN** the workflow does NOT claim success, the completion summary reports the failure with the exact cause, and any partial state (AGENTS.md written successfully, mirror not written) is named explicitly
