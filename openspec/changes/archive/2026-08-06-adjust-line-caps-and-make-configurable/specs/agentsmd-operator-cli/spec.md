## ADDED Requirements

### Requirement: CLI provides caps command
The `agentsmd caps` command SHALL print the resolved line caps — the per-category curated cap, the AGENTS.md line cap, and the AGENTS.md byte cap — and, for each, the source that won resolution (`env`, `caps.json`, or `default`). It is read-only and performs no file writes.

#### Scenario: Operator inspects resolved caps
- **WHEN** the operator runs `agentsmd caps`
- **THEN** the CLI prints each cap with its resolved value and source, using the precedence environment variable > `caps.json` > default

## MODIFIED Requirements

### Requirement: CLI provides status command
The `agentsmd status` command SHALL run the catalog self-discipline scan against every curated file and print the findings. The scan SHALL consider only real markdown list items (lines beginning with `-` or `*`); prose paragraphs and headings are not treated as bullets. Near-duplicate findings SHALL use the length-relative rule (edit distance ≤30 chars AND ≤40% of the shorter bullet's length). The per-category line cap is the configured value (default 32; see the configurable-caps requirement). It is read-only.

#### Scenario: Operator checks catalogue hygiene
- **WHEN** the operator runs `agentsmd status`
- **THEN** the CLI prints one line per curated file: `ok`, `<n> lines (cap <configured>)`, `bullet N exceeds 200 chars`, `near-duplicate vs bullet N`, or `missing trigger:`, without modifying any file
