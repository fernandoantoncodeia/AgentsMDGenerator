# Change: split-python-project-bullet

## Why

The catalog self-discipline scan added in `catalogue-write-discipline` runs at every `/update-agents` invocation and surfaces per-curated-file findings in the completion summary. The baseline scan against the existing 9 curated files flagged `prompt-catalogue/curated/python-project.md` bullet 6 as a real violation: 304 chars, exceeding the 200-char per-bullet cap. Until this change lands, every consumer-facing `/update-agents` run will surface `catalog/E-python-project.md — bullet 6 exceeds 200 chars (304 chars)` in its report — a known weakness shipped into the harness.

Splitting bullet 6 into two imperatives brings the file back into compliance with the existing contract and clears the baseline finding.

## What Changes

- **Modify** `prompt-catalogue/curated/python-project.md` — split the existing 304-char "If pip is used with a requirements file, install line by line using ... on Unix and ... on PowerShell; substitute the actual filename for `requirements.txt`." bullet into two separate imperatives, each ≤200 chars. The split target is the platform branch: (1) Unix one-liner becomes one bullet; (2) PowerShell one-liner becomes another bullet; (3) the substitution clause is folded into the leading imperative or dropped because it's information already carried by each example.

No requirements changes. This change is content-only, brought into conformance with the per-bullet ≤200 char rule that already exists in the `prompt-catalogue-management` capability (introduced by `catalogue-write-discipline`).

## Capabilities

- **Modified Capabilities**: none. No requirement changes; this is a content edit bringing one curated file into compliance.
- **New Capabilities**: none.

## Impact

- Future `/update-agents` invocations against any consumer project that splices `python-project.md` will no longer log the bullet-6 finding in the `Catalog self-discipline check:` section.
- AGENTS.md content for affected consumers changes: the 6th bullet in the spliced `## Python Project Hints` section now has two bullets where there was one. Order of bullets preserved; no semantic shift.
- The two new bullets together still convey the same installation rule (install line by line, platform-aware, substituting the filename).
- No spec, skill, command, or OpenSpec change touched outside this curated entry's body.
