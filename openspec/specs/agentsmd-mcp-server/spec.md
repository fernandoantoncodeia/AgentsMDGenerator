# agentsmd-mcp-server Specification

## Purpose
TBD - created by archiving change mcp-catalogue-rearchitecture. Update Purpose after archive.
## Requirements
### Requirement: Server exposes curated category metadata as a resource
The server SHALL expose `catalogue://categories` as an MCP resource. The response SHALL be a list of every curated category with `name`, `title`, and `trigger` fields. The response SHALL NOT include the body of any category.

#### Scenario: Project reads category metadata
- **WHEN** a project skill requests `catalogue://categories`
- **THEN** the server returns a JSON array of `{name, title, trigger}` objects, one per file in `prompt-catalogue/curated/`, parsed from each file's YAML frontmatter

#### Scenario: Metadata resource excludes bodies
- **WHEN** a project skill requests `catalogue://categories`
- **THEN** the response contains no `body` field and no category content beyond title and trigger metadata

### Requirement: Server exposes curated category bodies as resources
The server SHALL expose `catalogue://curated/<category>` as an MCP resource. The resource path maps to the category filename without the `.md` extension. The resource SHALL return the body of the category, excluding the YAML frontmatter.

#### Scenario: Project reads a specific curated category
- **WHEN** a project skill requests `catalogue://curated/python-project`
- **THEN** the server returns the body of `prompt-catalogue/curated/python-project.md`, stripped of its frontmatter

#### Scenario: Unknown curated category returns 404
- **WHEN** a project skill requests `catalogue://curated/nonexistent-category`
- **THEN** the server returns a not-found error and an empty body

### Requirement: Server exposes proposed category resources for monitoring
The server SHALL expose `catalogue://proposed-list` and `catalogue://proposed/<category>` resources. `proposed-list` returns the names of all categories in `prompt-catalogue/proposed/`. `proposed/<category>` returns the body of the proposed entry, excluding frontmatter.

#### Scenario: Operator reads proposed list
- **WHEN** an operator requests `catalogue://proposed-list`
- **THEN** the server returns the list of basenames of files in `prompt-catalogue/proposed/`

#### Scenario: Operator reads a proposed entry
- **WHEN** an operator requests `catalogue://proposed/python-project`
- **THEN** the server returns the body of `prompt-catalogue/proposed/python-project.md` if it exists, otherwise a not-found error

### Requirement: Server provides project-facing write tools
The server SHALL expose `catalogue_addcontent(category, body)` and `catalogue_addcategory(name, trigger, body)` tools. Both tools write only to `prompt-catalogue/proposed/`. They apply the same pre-trim rules (dedupe ≤30 char edit distance, trim verbose trailers, split bullets >200 chars at sentence boundary) as the previous `refresh-agents-content` actions.

#### Scenario: Project proposes a new bullet
- **WHEN** a project skill calls `catalogue_addcontent` with category `python-project` and a body string
- **THEN** the server appends the trimmed body to `prompt-catalogue/proposed/python-project.md` or creates the file if absent, and reports any trim-pass log in the tool result

#### Scenario: Project proposes a new category
- **WHEN** a project skill calls `catalogue_addcategory` with name `go-project`, trigger `*.go files present`, and a non-empty body
- **THEN** the server creates `prompt-catalogue/proposed/go-project.md` with the supplied frontmatter and trimmed body, and returns the file path

#### Scenario: Write tools refuse to write to curated
- **WHEN** a caller invokes `catalogue_addcontent` or `catalogue_addcategory` with a target that would overwrite `prompt-catalogue/curated/<category>.md`
- **THEN** the server refuses and returns an error stating that writes to `curated/` require a curation tool

### Requirement: Server provides operator-facing curation tools
The server SHALL expose `catalogue_curatecontent(category)` and `catalogue_curatecategory(name)` tools. These tools move content from `prompt-catalogue/proposed/` to `prompt-catalogue/curated/`, applying the same merge, dedupe, and self-discipline refusal rules as the previous `curatecontent` and `curatecategory` actions. They are the only tools that write to `curated/`.

#### Scenario: Operator curates proposed content
- **WHEN** an operator calls `catalogue_curatecontent` with category `python-project`
- **THEN** the server merges `prompt-catalogue/proposed/python-project.md` into `prompt-catalogue/curated/python-project.md`, removes the proposed entry after success, and returns the merged file path

#### Scenario: Operator curates a new category
- **WHEN** an operator calls `catalogue_curatecategory` with name `go-project`
- **THEN** the server promotes `prompt-catalogue/proposed/go-project.md` to `prompt-catalogue/curated/go-project.md`, enforces the 100-line and 200-char caps, and returns the curated file path

### Requirement: Server provides a source fetch tool for discovery
The server SHALL expose `catalogue_fetch_sources(urls[])` as a read-only tool. The tool fetches each URL and returns the raw HTTP body plus the `Last-Modified` timestamp if available. It does not diff, summarize, or invoke any LLM.

#### Scenario: Operator skill fetches canonical sources
- **WHEN** an operator skill calls `catalogue_fetch_sources` with the six canonical URLs
- **THEN** the server returns a list of `{url, body, last_modified, status}` entries, one per URL, with per-source HTTP status codes

#### Scenario: Fetch failure does not abort the batch
- **WHEN** one URL in the list returns 4xx or 5xx
- **THEN** the server records the failure for that URL and continues fetching the rest

### Requirement: Server runs no LLM and does not scan projects
The server SHALL NOT contain any LLM invocation, prompt template, embedding model, or model inference code. It SHALL NOT read files outside the catalogue directory (`prompt-catalogue/`). It SHALL NOT scan, list, or inspect consumer project files.

#### Scenario: Server code inspection shows no LLM
- **WHEN** a maintainer inspects the server source code
- **THEN** there is no dependency on an LLM SDK, no inference call, and no prompt-as-string construction

#### Scenario: Server rejects project-scan requests
- **WHEN** a client asks the server to evaluate a trigger against a project path
- **THEN** the server refuses and returns an error stating that trigger evaluation is the project skill's responsibility

### Requirement: Server supports both stdio and SSE transports
The server SHALL support `--transport stdio` and `--transport sse` startup modes. The default transport is `stdio`. The `--port` option is used when `--transport sse` is selected.

#### Scenario: Local stdio transport
- **WHEN** the server is started with `--transport stdio`
- **THEN** it reads MCP messages from stdin and writes responses to stdout, suitable for Claude Desktop / Claude Code local configuration

#### Scenario: Docker SSE transport
- **WHEN** the server is started with `--transport sse --port 3000`
- **THEN** it binds an HTTP server on port 3000 and exposes the MCP SSE endpoint, suitable for Docker or shared local services

