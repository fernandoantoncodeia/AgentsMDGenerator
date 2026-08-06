## Why

`agentsmd status` reports near-duplicate findings that are false positives. The near-duplicate rule uses a fixed Levenshtein distance of 30 regardless of bullet length, so short, similarly-worded but distinct list items (e.g. one-line command references in `openspec-cli`) are flagged. The scan also treats prose paragraphs and headings as bullets, widening the comparison set. There is also no sanctioned way to clean a genuine duplicate out of a curated file, since `curated/` must not be hand-edited and `curatecontent` only merges a `proposed/` entry.

## What Changes

- **A. Length-relative near-duplicate rule.** Two bullets are near-duplicates only when their Levenshtein distance is ≤30 chars AND ≤40% of the shorter bullet's length. This single rule is used by the write-path dedupe, the status scan, and recurate, so short distinct bullets stop being flagged or dropped.
- **B. Scan only real list items.** The self-discipline scan considers only markdown list items (lines starting with `-`/`*`); prose paragraphs and headings are no longer compared.
- **C. New `agentsmd recurate <name>` command.** Re-sweeps an existing curated category in place: re-trims trailers and drops genuine near-duplicate list items (first occurrence kept), preserving non-bullet content and frontmatter, applying the same cap checks and `--force` profile as `curatecontent`. It never touches `proposed/`.

## Capabilities

### Modified Capabilities
- `prompt-catalogue-management`: length-relative near-duplicate definition; scan restricted to real list items.
- `agentsmd-operator-cli`: `status` scans only list items with the length-relative rule; new `recurate` command.

## Impact

- Code: `agentsmd/trim.py` (near-dup rule), `agentsmd/catalogue.py` (scan + recurate), `agentsmd/cli.py` (recurate command).
- Clears the current false-positive `status` findings and gives operators a safe way to clean genuine duplicates without hand-editing `curated/`.
- Backward compatible: write-path dedupe becomes slightly less aggressive on short bullets; caps and the operator gate are unchanged.
