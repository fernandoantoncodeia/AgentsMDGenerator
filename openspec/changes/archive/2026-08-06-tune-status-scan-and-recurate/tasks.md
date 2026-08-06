## 1. Specs

- [x] 1.1 Modify `prompt-catalogue-management`: length-relative dedupe + scan-only-list-items
- [x] 1.2 Modify `agentsmd-operator-cli` status; add `recurate` command requirement
- [x] 1.3 `openspec validate tune-status-scan-and-recurate --strict`

## 2. Code

- [x] 2.1 A: add `is_near_duplicate` (≤30 AND ≤40% of shorter length) in trim.py; route `dedupe` through it
- [x] 2.2 B: add `_segment_body`/`_extract_list_items` and use them in `self_discipline_scan`; use `is_near_duplicate`
- [x] 2.3 C: add `catalogue.recurate` (preserve prose/headings/frontmatter) and the `agentsmd recurate` CLI command

## 3. Verify

- [x] 3.1 `agentsmd status` is clean on the live curated set (openspec-cli / short-and-imperative no longer flagged)
- [x] 3.2 recurate drops a simulated genuine duplicate but keeps distinct openspec-cli bullets

## 4. Archive

- [x] 4.1 `openspec archive tune-status-scan-and-recurate -y`
