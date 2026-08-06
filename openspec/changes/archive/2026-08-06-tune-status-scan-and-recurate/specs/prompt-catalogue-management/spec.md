## MODIFIED Requirements

### Requirement: Catalogue self-discipline rules and pre-trim contract
The catalogue's mechanical hygiene is governed by four rules. Every `catalogue_addcontent`, `catalogue_addcategory`, `agentsmd addcontent`, and `agentsmd addcategory` write action SHALL honour these rules. Operators cannot opt out of dedupe or bullet-length caps; the trim-tails phase is opt-out per call on the CLI (and surfaced as a flag for the MCP tools).

- Per-category file budget: ≤100 lines (D11).
- Per-bullet length cap: ≤200 chars; over-length bullets split at the first sentence boundary, halves stay separate unless folded by dedupe.
- Dedupe: two bullets in the same category are near-duplicates when their Levenshtein edit distance is ≤30 chars AND ≤40% of the shorter bullet's length; a new bullet that is a near-duplicate of an existing curated or proposed bullet is dropped. The length-relative factor prevents short, similarly-worded but distinct bullets (such as one-line command references) from being treated as duplicates.
- Frontmatter: every curated entry MUST carry `title:` AND `trigger:`; absence is a non-overridable contract violation; `--force` cannot resolve it.

#### Scenario: Dedupe drops near-duplicate bullets
- **WHEN** a caller supplies a bullet that is a near-duplicate (edit distance ≤30 chars and ≤40% of the shorter bullet's length) of an existing curated bullet in the same category
- **THEN** the surface drops the duplicate and reports `addcontent: dedupe <n> bullets vs curated` (or the analogous `curatecontent`/`addcategory` log line)

#### Scenario: Split-at-sentence for over-length bullets
- **WHEN** a caller supplies a bullet >200 chars
- **THEN** the surface splits at the first sentence boundary. Either half >200 chars fails the action with `bullet too long (≥200 chars after split)`.

#### Scenario: Opt-out flag documented
- **WHEN** the operator passes `--no-trim-tails` to `agentsmd addcontent` or `agentsmd addcategory` (or the equivalent MCP tool flag)
- **THEN** the trim-tails phase is skipped and the supplied body is written verbatim (subject to dedupe and length caps). The result records `addcontent: --no-trim-tails applied`.

### Requirement: Catalog self-discipline scan at /update-agents time
Every invocation of `/update-agents` (whose capability is `agents-md-generation`) SHALL read the central catalogue via the MCP server after the splice pass and emit a `Catalog self-discipline check:` section in the consumer's completion summary. The scan is read-only; it does NOT refuse the `/update-agents` invocation. The scan SHALL consider only real markdown list items (lines beginning with `-` or `*`); prose paragraphs and headings are not treated as bullets. Near-duplicate findings SHALL use the length-relative rule (edit distance ≤30 chars AND ≤40% of the shorter bullet's length). Findings per file:

- `ok` — all four rules pass.
- `<n> lines (cap 100)` — over the per-category cap (file over 100 lines).
- `bullet <i> exceeds 200 chars (n chars)` — over-length list item.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category near-duplicate list item.
- `missing trigger:` — HARD finding, named in the summary as a contract violation.

#### Scenario: Self-discipline check surfaces findings
- **WHEN** a curated file exceeds 100 lines or contains an over-length list item
- **THEN** the `/update-agents` completion summary has a `Catalog self-discipline check:` section listing each curated file with its findings. The summary still reports the splice outcome; the scan is non-blocking.

#### Scenario: Self-discipline check flags missing trigger field
- **WHEN** a curated file lacks the `trigger:` field
- **THEN** the file is flagged in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is named in the summary; the operator is expected to invoke `agentsmd curatecontent <category>` in the master repo to repair the file.
