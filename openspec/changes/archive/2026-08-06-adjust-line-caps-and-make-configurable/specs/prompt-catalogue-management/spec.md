## ADDED Requirements

### Requirement: Configurable line caps via caps.json and environment
The catalogue SHALL support two configurable line caps: the per-category curated file cap and the total generated AGENTS.md cap. Each value SHALL resolve per-key with the precedence **environment variable > `<catalogue-root>/caps.json` > built-in default**:

- Per-category curated cap: default **32** lines. Env `AGENTSMD_CATEGORY_MAX_LINES`; `caps.json` key `category_max_lines`.
- AGENTS.md line cap: default **512** lines. Env `AGENTSMD_AGENTS_MD_MAX_LINES`; `caps.json` key `agents_md_max_lines`.
- AGENTS.md byte cap: default **32768** (32 KiB). Env `AGENTSMD_AGENTS_MD_MAX_BYTES`; `caps.json` key `agents_md_max_bytes`.

These defaults supersede any literal "100-line" per-category figure or "150-line" AGENTS.md figure quoted in other requirements. `caps.json` is OPTIONAL: a missing file uses the defaults; a malformed file or a non-positive-integer value SHALL raise a `CatalogueError`. Unknown keys are ignored. The per-category cap governs the `curatecontent`, `curatecategory`, and `recurate` refusals plus the self-discipline scan; the AGENTS.md caps govern the `/update-agents` trim pass. The MCP server SHALL expose the resolved caps as the read-only resource `catalogue://config`, and the operator CLI SHALL expose them via `agentsmd caps`.

#### Scenario: Defaults apply when unconfigured
- **WHEN** no `caps.json` exists in the catalogue root and no cap environment variable is set
- **THEN** the per-category cap is 32 lines, the AGENTS.md cap is 512 lines, and the AGENTS.md byte cap is 32768

#### Scenario: caps.json overrides a default
- **WHEN** `<catalogue-root>/caps.json` sets `{"category_max_lines": 50}` and no matching env var is set
- **THEN** the resolved per-category cap is 50 and the other caps keep their defaults

#### Scenario: Environment variable overrides caps.json
- **WHEN** `caps.json` sets `category_max_lines` to 50 and `AGENTSMD_CATEGORY_MAX_LINES` is set to 20
- **THEN** the resolved per-category cap is 20

#### Scenario: Malformed configuration is rejected
- **WHEN** `caps.json` is not valid JSON, or a cap value is not a positive integer
- **THEN** the surface raises a `CatalogueError` naming the offending key or file rather than silently using a default

#### Scenario: Resolved caps are exposed
- **WHEN** a client reads `catalogue://config` or the operator runs `agentsmd caps`
- **THEN** the resolved per-category, AGENTS.md line, and AGENTS.md byte caps are returned

## MODIFIED Requirements

### Requirement: Catalogue self-discipline rules and pre-trim contract
The catalogue's mechanical hygiene is governed by four rules. Every `catalogue_addcontent`, `catalogue_addcategory`, `agentsmd addcontent`, and `agentsmd addcategory` write action SHALL honour these rules. Operators cannot opt out of dedupe or bullet-length caps; the trim-tails phase is opt-out per call on the CLI (and surfaced as a flag for the MCP tools).

- Per-category file budget: ≤ the configured per-category cap (default 32 lines; see the configurable-caps requirement).
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
Every invocation of `/update-agents` (whose capability is `agents-md-generation`) SHALL read the central catalogue via the MCP server after the splice pass and emit a `Catalog self-discipline check:` section in the consumer's completion summary. The scan is read-only; it does NOT refuse the `/update-agents` invocation. The scan SHALL consider only real markdown list items (lines beginning with `-` or `*`); prose paragraphs and headings are not treated as bullets. Near-duplicate findings SHALL use the length-relative rule (edit distance ≤30 chars AND ≤40% of the shorter bullet's length). The per-category line cap is the configured value (default 32; see the configurable-caps requirement). Findings per file:

- `ok` — all four rules pass.
- `<n> lines (cap <configured>)` — over the per-category cap.
- `bullet <i> exceeds 200 chars (n chars)` — over-length list item.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category near-duplicate list item.
- `missing trigger:` — HARD finding, named in the summary as a contract violation.

#### Scenario: Self-discipline check surfaces findings
- **WHEN** a curated file exceeds the configured per-category cap or contains an over-length list item
- **THEN** the `/update-agents` completion summary has a `Catalog self-discipline check:` section listing each curated file with its findings. The summary still reports the splice outcome; the scan is non-blocking.

#### Scenario: Self-discipline check flags missing trigger field
- **WHEN** a curated file lacks the `trigger:` field
- **THEN** the file is flagged in the `Catalog self-discipline check:` section as `missing trigger:` (HARD). The workflow still splices the body but the file is named in the summary; the operator is expected to invoke `agentsmd curatecontent <category>` in the master repo to repair the file.
