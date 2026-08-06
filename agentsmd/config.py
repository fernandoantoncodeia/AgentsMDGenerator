"""Configurable line caps.

Each cap resolves per-key with precedence:
environment variable > ``<catalogue-root>/caps.json`` > built-in default.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CATEGORY_MAX_LINES = 32
DEFAULT_AGENTS_MD_MAX_LINES = 512
DEFAULT_AGENTS_MD_MAX_BYTES = 32768  # 32 KiB

CAPS_FILENAME = "caps.json"

# (attribute, caps.json key / env-derived key, environment variable, default)
_SPECS: list[tuple[str, str, int]] = [
    ("category_max_lines", "AGENTSMD_CATEGORY_MAX_LINES", DEFAULT_CATEGORY_MAX_LINES),
    ("agents_md_max_lines", "AGENTSMD_AGENTS_MD_MAX_LINES", DEFAULT_AGENTS_MD_MAX_LINES),
    ("agents_md_max_bytes", "AGENTSMD_AGENTS_MD_MAX_BYTES", DEFAULT_AGENTS_MD_MAX_BYTES),
]


class ConfigError(Exception):
    """Raised for malformed caps configuration."""


@dataclass(frozen=True)
class Caps:
    category_max_lines: int
    agents_md_max_lines: int
    agents_md_max_bytes: int
    sources: dict[str, str]  # key -> "env" | "caps.json" | "default"


def _coerce_positive_int(value: object, origin: str, key: str) -> int:
    if isinstance(value, bool):
        raise ConfigError(f"{origin}: {key} must be a positive integer, got {value!r}")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.strip().lstrip("+").isdigit():
        result = int(value.strip())
    else:
        raise ConfigError(f"{origin}: {key} must be a positive integer, got {value!r}")
    if result <= 0:
        raise ConfigError(f"{origin}: {key} must be a positive integer, got {value!r}")
    return result


def _load_file(catalogue_root: str | Path | None) -> dict:
    if catalogue_root is None:
        return {}
    path = Path(catalogue_root) / CAPS_FILENAME
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise ConfigError(f"{path}: invalid JSON ({e})") from e
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: top-level JSON must be an object")
    return data


def resolve_caps(catalogue_root: str | Path | None = None) -> Caps:
    """Resolve all caps against env, caps.json in the catalogue root, and defaults."""
    file_data = _load_file(catalogue_root)
    values: dict[str, int] = {}
    sources: dict[str, str] = {}
    for key, env, default in _SPECS:
        env_val = os.environ.get(env)
        if env_val is not None:
            values[key] = _coerce_positive_int(env_val, f"env {env}", key)
            sources[key] = "env"
        elif key in file_data:
            values[key] = _coerce_positive_int(file_data[key], CAPS_FILENAME, key)
            sources[key] = "caps.json"
        else:
            values[key] = default
            sources[key] = "default"
    return Caps(
        category_max_lines=values["category_max_lines"],
        agents_md_max_lines=values["agents_md_max_lines"],
        agents_md_max_bytes=values["agents_md_max_bytes"],
        sources=sources,
    )
