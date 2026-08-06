## 1. Specs

- [x] 1.1 pcm: ADD configurable-caps requirement; MODIFY self-discipline rules + scan to the configured per-category cap (default 32)
- [x] 1.2 operator-cli: MODIFY status; ADD caps command
- [x] 1.3 gen: MODIFY Sourced Principles (512) + self-discipline scan finding text
- [x] 1.4 `openspec validate adjust-line-caps-and-make-configurable --strict`

## 2. Code

- [x] 2.1 Add `agentsmd/config.py`: `Caps` + `resolve_caps()` (env > caps.json > defaults 32/512/32768; malformed/non-positive raises)
- [x] 2.2 Route `catalogue.py` caps through `resolve_caps().category_max_lines` (checks, suggestions, scan)
- [x] 2.3 Add `catalogue://config` MCP resource and `agentsmd caps` CLI command

## 3. Assets

- [x] 3.1 Update both `update-agents/SKILL.md`: AGENTS.md cap from `catalogue://config` (default 512 / 32 KiB); per-category default 32
- [x] 3.2 One-off approved edit: `short-and-imperative.md` bullet 150 -> 512
- [x] 3.3 Add `prompt-catalogue/caps.json.example` and document precedence in INSTALL.md

## 4. Verify

- [x] 4.1 `agentsmd caps` prints resolved caps + source; `agentsmd status` clean at cap 32
- [x] 4.2 caps.json override and env-var override both take effect (env wins); malformed caps.json raises
- [x] 4.3 `catalogue://config` resource returns resolved caps

## 5. Archive

- [x] 5.1 `openspec archive adjust-line-caps-and-make-configurable -y`
