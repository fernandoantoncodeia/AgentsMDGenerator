---
title: Python Project Hints
trigger: project contains Python sources (pyproject.toml, requirements*.txt, setup.py, setup.cfg, pyrightconfig.json, ruff.toml, *.py, Pipfile, uv.lock, or a python/ or src/ package layout)
---

- Pick one dependency manager; do not mix pip, uv, poetry, and pip-tools in the same repo.
- Type-check with pyright or mypy, run with --strict on first pass; loosen per-module only with a justifying comment.
- Format and lint with ruff (rules in ruff.toml, not AGENTS.md). Black conventions are fine but ruff is the source of truth.
- Tests with pytest. Prefer per-file invocations: `pytest path/to/test_file.py -v` over full scans.
- Always activate a virtualenv before running Python; never touch the system interpreter.
- Pin Python in `pyproject.toml` (e.g. `requires-python = ">=3.11"`); do not pin every dependency to a fixed version.
- If pip is used with a requirements file, install each line individually using `cat <file> | xargs -n 1 pip install` on Unix.
- If pip is used with a requirements file, install each line individually using `Get-Content <file> | ForEach-Object { if ($_ -and $_ -notmatch '^\s*#') { pip install $_ } }` on PowerShell.
