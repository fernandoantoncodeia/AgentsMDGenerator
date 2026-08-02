---
title: Shell Tooling
trigger: project mixes Windows (PowerShell 5.1) and Unix (bash / zsh) workstations, OR an OpenSpec install that will run shell probes, OR the consumer's CI runs on either platform
---

- Detect the host platform before any shell command (system prompt OS/shell metadata first; cheap `python -c "import sys, platform; print(sys.platform, platform.system())"` probe if ambiguous).
- Path separators MUST match the host. Use `pathlib.Path` in scripts instead of string concatenation.
- Heredocs and any stdin-fed multi-line program are PERMANENTLY BANNED on every host.
- Multi-line or piped `python -c "..."` is the same class as a heredoc ban — write a `scripts/_<purpose>.py` instead.
- Working directory goes through the runner's `Cwd` parameter; never chain `cd <path>; <cmd>` into the command line.
- Destructive ops require operator approval. After two failed shell attempts, switch to a file-backed Python script; after two cancellations of the same conceptual operation, stop and ask.
- Prefer forward-slash relative paths in commit messages and docs even on Windows.
