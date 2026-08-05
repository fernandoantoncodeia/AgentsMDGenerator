"""Filesystem operations for the prompt catalogue."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from .trim import MAX_BULLET_LEN, dedupe, levenshtein, pre_trim, scan_bullets

MAX_CATEGORY_LINES = 100

_ROOT_OVERRIDE: Path | None = None


class CatalogueError(Exception):
    """Raised for catalogue-level errors."""


class RefusalError(CatalogueError):
    """Raised when a curation action is refused."""


@dataclass(frozen=True)
class CategoryMeta:
    name: str
    title: str
    trigger: str | None
    heuristic: bool


def set_catalogue_root(path: str | Path | None) -> None:
    """Set an explicit catalogue-root override (highest precedence)."""
    global _ROOT_OVERRIDE
    _ROOT_OVERRIDE = Path(path).expanduser() if path else None


def _bundled_catalogue_dir() -> Path | None:
    base = Path(__file__).parent / "_assets" / "prompt-catalogue"
    return base if (base / "curated").is_dir() else None


def _normalize(candidate: Path) -> Path | None:
    if (candidate / "curated").is_dir():
        return candidate
    if (candidate / "prompt-catalogue" / "curated").is_dir():
        return candidate / "prompt-catalogue"
    return None


def resolve_catalogue_dir() -> Path:
    """Resolve the prompt-catalogue directory or raise CatalogueError.

    Precedence: explicit override > AGENTSMD_CATALOGUE_ROOT > ./prompt-catalogue
    > read-only bundled snapshot shipped in the installed package.
    """
    candidates: list[Path] = []
    if _ROOT_OVERRIDE is not None:
        candidates.append(_ROOT_OVERRIDE)
    env = os.environ.get("AGENTSMD_CATALOGUE_ROOT")
    if env:
        candidates.append(Path(env).expanduser())
    candidates.append(Path("prompt-catalogue"))
    for candidate in candidates:
        norm = _normalize(candidate)
        if norm is not None:
            return norm
    bundled = _bundled_catalogue_dir()
    if bundled is not None:
        return bundled
    raise CatalogueError(
        "catalogue not found; provide it via --catalogue-root, the "
        "AGENTSMD_CATALOGUE_ROOT environment variable, a prompt-catalogue/ "
        "directory in the current directory, or the package's bundled snapshot"
    )


def catalogue_is_read_only() -> bool:
    """Return True when the resolved catalogue is the bundled read-only snapshot."""
    bundled = _bundled_catalogue_dir()
    if bundled is None:
        return False
    try:
        return resolve_catalogue_dir().resolve() == bundled.resolve()
    except CatalogueError:
        return False


def curated_dir() -> Path:
    return resolve_catalogue_dir() / "curated"


def proposed_dir() -> Path:
    return resolve_catalogue_dir() / "proposed"


def _ensure_catalogue_root() -> None:
    resolve_catalogue_dir()


def _require_writable() -> None:
    if catalogue_is_read_only():
        raise RefusalError(
            "resolved catalogue is the read-only bundled snapshot; set a writable "
            "root via --catalogue-root or AGENTSMD_CATALOGUE_ROOT to make changes"
        )


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and return (data, body)."""
    if text.startswith("---"):
        match = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
        if match:
            try:
                data = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError as e:
                raise CatalogueError(f"Invalid YAML frontmatter: {e}") from e
            return data, match.group(2).strip()
    return {}, text.strip()


def _render_frontmatter(data: dict) -> str:
    """Render a dict as YAML frontmatter."""
    yaml_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{yaml_text}\n---\n"


def _read_category(path: Path) -> tuple[dict, str]:
    if not path.exists():
        raise FileNotFoundError(path)
    return _parse_frontmatter(path.read_text(encoding="utf-8"))


def _write_category(path: Path, data: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = _render_frontmatter(data) + body.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def _extract_bullets(body: str) -> list[str]:
    """Extract bullet lines from a body. Non-bullet lines are kept as-is."""
    bullets: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]\s+", stripped):
            if current:
                bullets.append("\n".join(current).strip())
                current = []
            bullets.append(re.sub(r"^[-*]\s+", "", stripped))
        elif current and (stripped == "" or line.startswith(" ")):
            current.append(line)
        else:
            if current:
                bullets.append("\n".join(current).strip())
                current = []
            if stripped:
                bullets.append(stripped)
    if current:
        bullets.append("\n".join(current).strip())
    return bullets


def _render_bullets(bullets: list[str]) -> str:
    """Render bullets as markdown list."""
    lines: list[str] = []
    for bullet in bullets:
        for i, line in enumerate(bullet.splitlines()):
            if i == 0:
                lines.append(f"- {line}")
            else:
                lines.append(f"  {line}")
    return "\n".join(lines)


def _default_title(category: str) -> str:
    return category.replace("-", " ").replace("_", " ").title()


def list_curated() -> list[CategoryMeta]:
    """Return metadata for all curated categories."""
    _ensure_catalogue_root()
    result: list[CategoryMeta] = []
    curated = curated_dir()
    if not curated.exists():
        return result
    for path in sorted(curated.glob("*.md")):
        try:
            data, _ = _read_category(path)
        except FileNotFoundError:
            continue
        result.append(
            CategoryMeta(
                name=path.stem,
                title=data.get("title", _default_title(path.stem)),
                trigger=data.get("trigger"),
                heuristic=data.get("trigger-confidence") == "heuristic",
            )
        )
    return result


def list_proposed() -> list[str]:
    """Return the names of all proposed categories."""
    _ensure_catalogue_root()
    proposed = proposed_dir()
    if not proposed.exists():
        return []
    return sorted(p.stem for p in proposed.glob("*.md"))


def read_body(name: str, proposed: bool = False) -> str | None:
    """Return the body of a category, or None if absent."""
    _ensure_catalogue_root()
    directory = proposed_dir() if proposed else curated_dir()
    path = directory / f"{name}.md"
    if not path.exists():
        return None
    _, body = _read_category(path)
    return body


def read_frontmatter(name: str, proposed: bool = False) -> dict:
    """Return the frontmatter of a category, or {} if absent."""
    _ensure_catalogue_root()
    directory = proposed_dir() if proposed else curated_dir()
    path = directory / f"{name}.md"
    if not path.exists():
        return {}
    data, _ = _read_category(path)
    return data


def _add_bullets(
    category: str,
    bullets: list[str],
    proposed: bool = True,
    title: str | None = None,
    no_trim_tails: bool = False,
) -> tuple[Path, list[str]]:
    """Append bullets to a category file, applying the pre-trim pass."""
    _ensure_catalogue_root()
    _require_writable()
    directory = proposed_dir() if proposed else curated_dir()
    if not proposed:
        raise CatalogueError("direct writes to curated/ are not allowed")

    path = directory / f"{category}.md"
    existing_curated = _extract_bullets(read_body(category, proposed=False) or "")
    existing_proposed: list[str] = []
    if path.exists():
        existing_proposed = _extract_bullets(_read_category(path)[1])

    trimmed, logs = pre_trim(
        bullets,
        existing_curated=existing_curated,
        existing_proposed=existing_proposed,
        trim_tails=not no_trim_tails,
    )

    overlong = scan_bullets(trimmed)
    if overlong:
        raise RefusalError(
            "refused — bullet too long (≥200 chars after split): "
            + "; ".join(overlong)
        )

    if path.exists():
        data, body = _read_category(path)
        existing_bullets = _extract_bullets(body)
        combined = existing_bullets + trimmed
        new_body = _render_bullets(combined)
    else:
        data = {
            "title": title or _default_title(category),
            "trigger": "",
        }
        new_body = _render_bullets(trimmed)

    _write_category(path, data, new_body)
    return path, logs


def addcontent(
    category: str,
    body: str,
    title: str | None = None,
    no_trim_tails: bool = False,
) -> tuple[Path, list[str]]:
    """Append a body as one or more bullets to a proposed category."""
    bullets = _extract_bullets(body) if body.strip() else [body.strip()]
    if not bullets or not any(b.strip() for b in bullets):
        raise RefusalError("body is empty")
    return _add_bullets(
        category, bullets, proposed=True, title=title, no_trim_tails=no_trim_tails
    )


def addcategory(
    name: str,
    trigger: str,
    body: str,
    title: str | None = None,
) -> tuple[Path, list[str]]:
    """Create a proposed category file with a starter body."""
    _ensure_catalogue_root()
    _require_writable()
    if (curated_dir() / f"{name}.md").exists():
        raise RefusalError(
            f"category already in curated; use curatecontent to refine the existing curated entry"
        )
    if (proposed_dir() / f"{name}.md").exists():
        raise RefusalError(
            f"category already in proposed; use addcontent to append to it"
        )
    if not body or not body.strip():
        raise RefusalError(
            "body is required (D8 + spec). Re-run with at least a one-sentence starter body."
        )

    bullets = _extract_bullets(body)
    trimmed, logs = pre_trim(
        bullets,
        existing_curated=[],
        existing_proposed=[],
    )
    overlong = scan_bullets(trimmed)
    if overlong:
        raise RefusalError(
            "refused — bullet too long (≥200 chars after split): "
            + "; ".join(overlong)
        )

    data = {
        "title": title or _default_title(name),
        "trigger": trigger,
    }
    path = proposed_dir() / f"{name}.md"
    _write_category(path, data, _render_bullets(trimmed))
    return path, logs


def _check_caps(data: dict, body: str) -> list[str]:
    """Return a list of cap violations for a curated file."""
    findings: list[str] = []
    lines = body.splitlines()
    if len(lines) > MAX_CATEGORY_LINES:
        findings.append(
            f"merged would be {len(lines)} lines (cap {MAX_CATEGORY_LINES})"
        )
    bullets = _extract_bullets(body)
    for i, bullet in enumerate(bullets, 1):
        if len(bullet) > MAX_BULLET_LEN:
            findings.append(f"bullet {i} exceeds 200 chars ({len(bullet)} chars)")
    if not data.get("trigger"):
        findings.append("missing trigger: field is non-overridable")
    return findings


def _suggest_fix(body: str) -> list[str]:
    """Return suggested fixes for cap violations."""
    suggestions: list[str] = []
    lines = body.splitlines()
    if len(lines) > MAX_CATEGORY_LINES:
        overflow = len(lines) - MAX_CATEGORY_LINES
        suggestions.append(f"drop {overflow} bullets to reach {MAX_CATEGORY_LINES} lines")
    bullets = _extract_bullets(body)
    for i, bullet in enumerate(bullets, 1):
        if len(bullet) > MAX_BULLET_LEN:
            match = re.search(r"(?<=[.!?])\s+", bullet)
            if match:
                first = bullet[: match.end()].strip()
                second = bullet[match.end() :].strip()
                suggestions.append(
                    f"bullet {i}: split into \"{first}\" and \"{second}\""
                )
            else:
                suggestions.append(f"bullet {i}: shorten manually")
    return suggestions


def curatecontent(category: str, force: bool = False) -> Path:
    """Merge a proposed category into the curated category."""
    _ensure_catalogue_root()
    _require_writable()
    proposed_path = proposed_dir() / f"{category}.md"
    curated_path = curated_dir() / f"{category}.md"

    if not proposed_path.exists():
        raise RefusalError(f"no proposed entry for {category}")

    proposed_data, proposed_body = _read_category(proposed_path)
    proposed_bullets = _extract_bullets(proposed_body)

    if curated_path.exists():
        curated_data, curated_body = _read_category(curated_path)
        curated_bullets = _extract_bullets(curated_body)
        # Prefer non-empty proposed frontmatter values, but never let an empty
        # proposed value (e.g. a blank trigger from addcontent) clobber a real
        # curated one.
        merged_data = dict(curated_data)
        for key, value in proposed_data.items():
            if value not in (None, ""):
                merged_data[key] = value
        merged_bullets = curated_bullets + proposed_bullets
    else:
        curated_bullets = []
        merged_data = proposed_data.copy()
        merged_bullets = proposed_bullets

    # Deduplicate merged bullets against themselves and curated ones
    deduped, dropped = dedupe(merged_bullets, [])
    if dropped:
        deduped, _ = dedupe(deduped, curated_bullets)

    new_body = _render_bullets(deduped)
    violations = _check_caps(merged_data, new_body)

    if violations and not force:
        suggestions = _suggest_fix(new_body)
        raise RefusalError(
            "curatecontent: refused — " + "; ".join(violations) + "\n"
            "Suggested fix: " + "; ".join(suggestions)
        )

    if not merged_data.get("title"):
        merged_data["title"] = _default_title(category)
    if not merged_data.get("trigger"):
        raise RefusalError(
            "curatecontent: refused — missing trigger: field is non-overridable; --force cannot resolve it"
        )

    _write_category(curated_path, merged_data, new_body)
    proposed_path.unlink()
    return curated_path


def curatecategory(name: str, force: bool = False) -> Path:
    """Promote a proposed category to curated."""
    _ensure_catalogue_root()
    _require_writable()
    proposed_path = proposed_dir() / f"{name}.md"
    curated_path = curated_dir() / f"{name}.md"

    if not proposed_path.exists():
        raise RefusalError(f"no proposed entry for {name}")
    if curated_path.exists():
        raise RefusalError(
            f"category {name} already exists in curated; use curatecontent to merge"
        )

    data, body = _read_category(proposed_path)
    violations = _check_caps(data, body)
    if violations and not force:
        suggestions = _suggest_fix(body)
        raise RefusalError(
            "curatecategory: refused — " + "; ".join(violations) + "\n"
            "Suggested fix: " + "; ".join(suggestions)
        )

    if not data.get("trigger"):
        raise RefusalError(
            "curatecategory: refused — missing trigger: field is non-overridable; --force cannot resolve it"
        )

    _write_category(curated_path, data, body)
    proposed_path.unlink()
    return curated_path


def self_discipline_scan() -> list[tuple[str, list[str]]]:
    """Scan all curated categories and return findings per file."""
    _ensure_catalogue_root()
    results: list[tuple[str, list[str]]] = []
    for path in sorted(curated_dir().glob("*.md")):
        data, body = _read_category(path)
        findings: list[str] = []
        lines = body.splitlines()
        if len(lines) > MAX_CATEGORY_LINES:
            findings.append(f"{len(lines)} lines (cap {MAX_CATEGORY_LINES})")
        if not data.get("trigger"):
            findings.append("missing trigger:")
        bullets = _extract_bullets(body)
        for i, bullet in enumerate(bullets, 1):
            if len(bullet) > MAX_BULLET_LEN:
                findings.append(f"bullet {i} exceeds 200 chars ({len(bullet)} chars)")
        # near-duplicate detection within the file
        for i, a in enumerate(bullets):
            for j, b in enumerate(bullets):
                if i < j:
                    dist = levenshtein(a, b)
                    if dist <= 30:
                        findings.append(
                            f"near-duplicate vs bullet {j + 1} (edit distance {dist})"
                        )
        if not findings:
            findings.append("ok")
        results.append((path.stem, findings))
    return results


def fetch_sources(urls: Iterable[str]) -> list[dict]:
    """Fetch URLs and return raw bodies with status and last-modified."""
    import requests

    results: list[dict] = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=30)
            results.append(
                {
                    "url": url,
                    "status": resp.status_code,
                    "body": resp.text,
                    "last_modified": resp.headers.get("Last-Modified"),
                }
            )
        except Exception as e:
            results.append(
                {
                    "url": url,
                    "status": 0,
                    "body": "",
                    "last_modified": None,
                    "error": str(e),
                }
            )
    return results
