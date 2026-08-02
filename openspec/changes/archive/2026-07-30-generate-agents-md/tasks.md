## 1. Command scaffold

- [x] 1.1 Create `.claude/commands/generate-agents.md` with the frontmatter (`description`, `argument-hint`) matching the bundle layout used by `.claude/commands/opsx/*.md`
- [x] 1.2 Keep the command body short: pointer to the skill, an input line, and a one-line summary of behavior

## 2. Skill body (workflow logic)

- [x] 2.1 Create `.claude/skills/generate-agents-md/SKILL.md` with the YAML frontmatter (`name`, `description`, `allowed-tools`, `license`, `compatibility`, `metadata`) matching the bundle pattern
- [x] 2.2 Encode the create-vs-update detection: read `AGENTS.md` at the resolved project path or the supplied path argument
- [x] 2.3 Encode update-mode evaluation: read existing file, score against the embedded checklist, preserve project-specific rules, apply conditional catalog, write in place
- [x] 2.4 Encode create-mode generation: scan repo, fire trigger checks, build output from mandated section plus only the trigger-fired catalog sections, write file

## 3. Mandated baseline content

- [x] 3.1 Embed the "be a colleague" baseline section text in the skill so the workflow can splice it into every output
- [x] 3.2 Cover the three sub-points it must convey: collaborator stance (not just executor), faithful reporting (no manufactured green results), and user-facing prose rules (complete sentences, no unexplained jargon)

## 4. Conditional catalog and triggers

- [x] 4.1 Encode the catalog as a numbered list of section templates with detection triggers (Python, Windows COM, OpenSpec, self-documentation, build/error feedback loop, tool erratic behaviour, OpenSpec CLI, shell tooling)
- [x] 4.2 Encode the trigger rules so a section is included in the output only when its trigger fires
- [x] 4.3 Mark optional sections that apply only when the user's request or repo makes them valuable

## 5. Best-practices checklist and references

- [x] 5.1 Embed a curated checklist of best-practice principles (imperative tone, group by concern, exact commands over prose, concise length, no contradictions, real examples, trim after edit)
- [x] 5.2 Embed a short list of public reference URLs (agents.md open standard and github mirror, builder.io, morphllm, asdlc.io, blakecrosley, betterclaw)

## 6. Optional live refresh

- [x] 6.1 Add a `--refresh` input convention that triggers a live web search against the embedded references before generating
- [x] 6.2 Add a staleness-detection note for the case where the workflow suspects embedded guidance is out of date

## 7. Reporting

- [x] 7.1 Encode a completion summary listing create-vs-update, sections added, sections preserved verbatim, sections trimmed, and any side-effect suggestions (CLAUDE.md mirror)
- [x] 7.2 Encode a failure summary that reports the exact cause and does not claim success

## 8. Validation and archive

- [x] 8.1 Run `openspec validate generate-agents-md --strict`
- [x] 8.2 Run `openspec archive generate-agents-md -y` to sync the delta spec into `openspec/specs/agents-md-generation/spec.md` and archive the change
