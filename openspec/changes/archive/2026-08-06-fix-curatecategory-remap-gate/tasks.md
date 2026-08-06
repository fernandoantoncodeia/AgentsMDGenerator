## 1. Specs

- [x] 1.1 Modify `agentsmd-operator-cli` `curatecategory` requirement: genuine trigger overlap + `--no-remap`
- [x] 1.2 `openspec validate fix-curatecategory-remap-gate --strict`

## 2. Code

- [x] 2.1 Add a stopword-filtered trigger-token helper and compute genuine overlap in `curatecategory`
- [x] 2.2 Add the `--no-remap` flag; promote when no genuine candidate or when `--no-remap` is passed
- [x] 2.3 Keep listing genuine candidates (and not promoting) when they exist and `--no-remap` is absent

## 3. Verify

- [x] 3.1 Confirm the four unrelated live proposals no longer trigger the remap gate
- [x] 3.2 Confirm `--no-remap` promotes when a genuine overlap is simulated

## 4. Archive

- [x] 4.1 `openspec archive fix-curatecategory-remap-gate -y`
