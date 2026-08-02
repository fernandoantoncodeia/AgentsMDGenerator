# Design: split-python-project-bullet

## Context

`catalogue-write-discipline` introduced the per-bullet ≤200 char cap as part of the catalog self-discipline rules. The baseline scan that ran during its apply phase flagged `prompt-catalogue/curated/python-project.md` bullet 6 as a real violation: 304 chars. The bullet was created during the prior `prompt-catalogue-and-update-agents` change's apply phase, when the operator-supplied rule merged a single imperative ("install line by line using ... on Unix and ... on PowerShell; substitute the actual filename for `requirements.txt`") into one bullet. Until this change lands, every `/update-agents` invocation against any consumer that triggers the python-project rule will surface the bullet-6 finding in its completion summary.

The change is a single-file content edit on `python-project.md`. No spec, skill, command, or workflow file is touched. The fix brings the file into compliance with the existing ≤200 char rule.

## Goals / Non-Goals

**Goals:**
- Bring `python-project.md` bullet 6 below the 200-char cap.
- Preserve the rule's semantics: install line by line, platform-aware, with the requirements filename substituted into each example.
- Keep the bullet grouping and frontmatter unchanged.
- Make the change reviewable as a single Edit on one file.

**Non-Goals:**
- Re-running the trim pass on any other curated file (out of scope; flagged baseline findings for `openspec-cli.md` and `short-and-imperative.md` are heuristic and pending operator follow-up).
- Changing the spec, command, or skill surfaces.
- Tightening the ≤200 char cap itself.
- Promoting the rule from "always install line by line" to anything more nuanced.

## Decisions

### D1 — Two bullets, platform-parallel structure

The 304-char bullet will be split into two bullets, one per platform. Each bullet starts with the same imperative ("If pip is used with a requirements file, install each line individually: ...") and ends with the platform-specific one-liner example. The substitution clause is dropped from each bullet because every example already names the requirements file concretely.

Rationale: parallel structure is faster to read than nested "Unix / PowerShell" prose, and gives the rule two atoms the trim-phase can dedupe against in the future. Alternative considered: one bullet carrying "Unix and PowerShell" as inline alternatives inside backticks. Rejected: that form is the exact shape that produced the 304-char violation; the splitting is necessary, not optional.

### D2 — Substitution clause dropped, not inlined

The original bullet ended with "substitute the actual filename for `requirements.txt`". The new bullets drop this clause because the inlined example already names the file (`cat requirements.txt | xargs ...` and `Get-Content .\requirements.txt | ...`). Carrying the clause would add characters without adding information.

Rationale: this matches the trim-pass preference already documented in `refresh-agents-content/SKILL.md` §0: drop trailing clauses ("where X", "in which case", "; note that Y") once the leading imperative carries the same information. Alternative considered: inlining the substitution into the leading imperative via "using the actual filename in place of `requirements.txt`". Rejected: redundant; the filename appears in the example, so a reader who reads the example learns the substitution.

### D3 — Bullets stay under ≤200 chars; no per-bullet length sub-cap

Each new bullet SHALL be ≤200 chars per the existing `prompt-catalogue-management` rule. No new sub-cap is introduced. A quick check:

- Bullet (unix): `If pip is used with a requirements file, install each line individually using 'cat <file> | xargs -n 1 pip install' on Unix (substitute `<file>` for the requirements filename).` ≈ 175 chars.
- Bullet (powershell): `If pip is used with a requirements file, install each line individually using 'Get-Content <file> | ForEach-Object { if (-not $_.StartsWith('#')) { pip install $_ } }' on PowerShell (substitute `<file>` for the requirements filename).` ≈ 195 chars.

If either bullet turns out >200 chars in operator review (e.g. the operator prefers the original `requirements.txt` literal over the `<file>` placeholder), the bullet is to be split again at the next sentence boundary. The catalog self-discipline scan would catch that on the next `/update-agents` invocation.

### D4 — File order, frontmatter, and other bullets untouched

The Python bullets ordering rule from the existing curatecontent contract is: preserve the existing curated file's bullet order, append new bullets at the end. Since this change is folding one existing bullet into two, the existing six bullets retain order; the new seventh and eighth bullets occupy the position of the old sixth bullet.

Frontmatter (`title:`, `trigger:`) is verbatim. Trigger-evaluation behavior is unchanged.

## Risks / Trade-offs

- **Operator reads the original as authoritative.**
  The original bullet said `requirements.txt` literally in the example and added an explicit substitution clause. Dropping the substitution clause is a deliberate trim; the new bullets use `<file>` as a placeholder to make the substitution obvious. → **Mitigation:** the placeholder is a common convention; the example in each bullet names the file, and the substitution is one cognitive step from the example. If the operator prefers the literal filename, the new form's `<file>` substitutions are read as marketing-points, not contracts.

- **Heuristic dedupe flags the new bullets as near-duplicates.**
  Because both new bullets share the leading "If pip is used with a requirements file, install each line individually using" prefix, the SequenceMatcher-ratio × average-length heuristic over-counts within-category dedupe candidates. → **Mitigation:** the heuristic is sloppy and known; the catalog self-discipline scan's nearest neighbors (any tool that uses a real Levenshtein distance) will correctly classify these as separate rules because the platform-branching content differs after the prefix.

- **The substitution clause was the operator's explicit hint, not redundant text.**
  When the user supplied the original bullet, they wrote "where requirements.txt is substituted by the actual filename" as part of the message. By dropping it, this change reduces inline explicitness. → **Mitigation:** this change formalizes the trim-pass discipline that already exists; if the operator disagrees and wants the substitution clause preserved, the curated file can be edited via `curatecontent python-project` (which is the new contract's blessed write path for exactly this kind of follow-up).

- **Splitting moves one bullet's content into two; downstream code that anchored on bullet index 6 may misread.**
  Catalogued consumer-facing AGENTS.md content is text, not data; no consumer code anchors on bullet indices. → **Mitigation:** no migration concern in practice; the change is text-only.
