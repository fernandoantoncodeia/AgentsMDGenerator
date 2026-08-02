## 1. Edit python-project.md

- [x] 1.1 Read `prompt-catalogue/curated/python-project.md` to capture the existing bullet 6 text verbatim
- [x] 1.2 Edit the file: replace bullet 6 with two parallel bullets (Unix, PowerShell), each ≤200 chars
- [x] 1.3 Verify the resulting file is still ≤100 lines per the per-category cap (D11)
- [x] 1.4 Verify frontmatter (`title:`, `trigger:`) is unchanged

## 2. Verify self-discipline compliance

- [x] 2.1 Re-run the catalog self-discipline scan against the updated `python-project.md`
- [x] 2.2 Confirm zero findings for `python-project.md`: file ≤100 lines, every bullet ≤200 chars, no missing `trigger:` field, no false-positive near-duplicate flagging that requires operator review
- [x] 2.3 Confirm the eight other curated files' baseline findings are unchanged (no incidental regression)

## 3. Validate + archive

- [x] 3.1 Run `openspec validate split-python-project-bullet --strict`
- [x] 3.2 Run `openspec archive split-python-project-bullet -y` so the change lifecycle closes
