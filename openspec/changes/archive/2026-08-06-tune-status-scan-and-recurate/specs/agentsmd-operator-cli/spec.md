## MODIFIED Requirements

### Requirement: CLI provides status command
The `agentsmd status` command SHALL run the catalog self-discipline scan against every curated file and print the findings. The scan SHALL consider only real markdown list items (lines beginning with `-` or `*`); prose paragraphs and headings are not treated as bullets. Near-duplicate findings SHALL use the length-relative rule (edit distance ≤30 chars AND ≤40% of the shorter bullet's length). It is read-only.

#### Scenario: Operator checks catalogue hygiene
- **WHEN** the operator runs `agentsmd status`
- **THEN** the CLI prints one line per curated file: `ok`, `>100 lines`, `bullet N exceeds 200 chars`, `near-duplicate vs bullet N`, or `missing trigger:`, without modifying any file

## ADDED Requirements

### Requirement: CLI provides recurate command
The `agentsmd recurate <name>` command SHALL re-sweep an existing curated category in place. It SHALL re-run the trailer trim and drop near-duplicate list items (keeping the first occurrence) using the same length-relative near-duplicate rule as the scan, while preserving non-bullet content (prose and headings) and the frontmatter. It SHALL require an existing `prompt-catalogue/curated/<name>.md` and SHALL NOT read or modify `proposed/`. It applies the same cap checks and refusal profile as `curatecontent`: `--force` overrides size and bullet-length caps only, and a missing `trigger:` is non-overridable. `--no-trim-tails` skips the trailer-trim phase.

#### Scenario: Operator re-sweeps a curated category
- **WHEN** the operator runs `agentsmd recurate <name>` on a curated file that contains a genuine near-duplicate list item
- **THEN** the CLI drops the later duplicate, preserves all other content and the frontmatter, rewrites the curated file, and reports the dropped bullet

#### Scenario: recurate refuses without a curated entry
- **WHEN** the operator runs `agentsmd recurate <name>` and `prompt-catalogue/curated/<name>.md` does not exist
- **THEN** the CLI refuses with an error and writes nothing

#### Scenario: recurate leaves distinct short bullets intact
- **WHEN** a curated file has short, similarly-worded but distinct list items (such as one-line command references)
- **THEN** the length-relative rule does not treat them as duplicates and recurate keeps them all
