"""Filesystem operations for the prompt catalogue."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from .trim import (
    MAX_BULLET_LEN,
    dedupe,
    is_near_duplicate,
    levenshtein,
    pre_trim,
    scan_bullets,
    trim_tail,
)

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


def _normalize(candidate: Path) -> Path | None:
    if (candidate / "curated").is_dir():
        return candidate
    if (candidate / "prompt-catalogue" / "curated").is_dir():
        return candidate / "prompt-catalogue"
    return None


def resolve_catalogue_dir() -> Path:
    """Resolve the prompt-catalogue directory or raise CatalogueError.

    Precedence: explicit override > AGENTSMD_CATALOGUE_ROOT > ./prompt-catalogue.
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
    raise CatalogueError(
        "catalogue not found; provide it via --catalogue-root, the "
        "AGENTSMD_CATALOGUE_ROOT environment variable, or a prompt-catalogue/ "
        "directory in the current directory"
    )


def curated_dir() -> Path:
    return resolve_catalogue_dir() / "curated"


def proposed_dir() -> Path:
    return resolve_catalogue_dir() / "proposed"


def _ensure_catalogue_root() -> None:
    resolve_catalogue_dir()


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


_BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")


def _segment_body(body: str) -> list[tuple[str, str | None, list[str]]]:
    """Split a body into ordered segments.

    Each segment is ("bullet", canonical_text, raw_lines) for a real markdown
    list item (with its indented continuation lines folded into the text), or
    ("other", None, raw_lines) for any prose, heading, or blank line. This
    preserves non-bullet content so a rewrite never mangles it.
    """
    lines = body.splitlines()
    segments: list[tuple[str, str | None, list[str]]] = []
    i = 0
    while i < len(lines):
        match = _BULLET_RE.match(lines[i])
        if match:
            raw = [lines[i]]
            text = match.group(2).strip()
            j = i + 1
            while (
                j < len(lines)
                and lines[j].startswith((" ", "\t"))
                and lines[j].strip()
                and not _BULLET_RE.match(lines[j])
            ):
                raw.append(lines[j])
                text += " " + lines[j].strip()
                j += 1
            segments.append(("bullet", text, raw))
            i = j
        else:
            segments.append(("other", None, [lines[i]]))
            i += 1
    return segments


def _extract_list_items(body: str) -> list[str]:
    """Return only real markdown list items (prose and headings excluded)."""
    return [text for kind, text, _ in _segment_body(body) if kind == "bullet" and text]


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


def recurate(
    name: str, force: bool = False, trim_tails: bool = True
) -> tuple[Path, list[str]]:
    """Re-sweep an existing curated category in place.

    Re-runs the trailer trim and drops near-duplicate list items (first
    occurrence kept), preserving non-bullet content and the frontmatter. Never
    reads or writes proposed/. Applies the same caps/refusal profile as
    curatecontent.
    """
    _ensure_catalogue_root()
    curated_path = curated_dir() / f"{name}.md"
    if not curated_path.exists():
        raise RefusalError(f"no curated entry for {name}")

    data, body = _read_category(curated_path)
    kept_texts: list[str] = []
    out_lines: list[str] = []
    logs: list[str] = []
    dropped = 0

    for kind, text, raw in _segment_body(body):
        if kind != "bullet" or text is None:
            out_lines.extend(raw)
            continue
        new_text = text
        if trim_tails:
            trimmed, trailer = trim_tail(text)
            if trailer:
                new_text = trimmed
                logs.append(f'trimmed tail (dropped "{trailer}")')
        if any(is_near_duplicate(new_text, kept) for kept in kept_texts):
            dropped += 1
            preview = new_text if len(new_text) <= 60 else new_text[:57] + "..."
            logs.append(f'dropped near-duplicate bullet: "{preview}"')
            continue
        kept_texts.append(new_text)
        if new_text != text:
            out_lines.append(f"- {new_text}")
        else:
            out_lines.extend(raw)

    if dropped:
        logs.append(f"dropped {dropped} near-duplicate bullets")
    new_body = "\n".join(out_lines).strip()

    violations = _check_caps(data, new_body)
    if violations and not force:
        suggestions = _suggest_fix(new_body)
        raise RefusalError(
            "recurate: refused — " + "; ".join(violations) + "\n"
            "Suggested fix: " + "; ".join(suggestions)
        )
    if not data.get("trigger"):
        raise RefusalError(
            "recurate: refused — missing trigger: field is non-overridable; --force cannot resolve it"
        )

    _write_category(curated_path, data, new_body)
    if not logs:
        logs.append("no changes")
    return curated_path, logs


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
        # Scan only real markdown list items; prose and headings are not bullets.
        bullets = _extract_list_items(body)
        for i, bullet in enumerate(bullets, 1):
            if len(bullet) > MAX_BULLET_LEN:
                findings.append(f"bullet {i} exceeds 200 chars ({len(bullet)} chars)")
        # near-duplicate detection within the file (length-relative rule)
        for i, a in enumerate(bullets):
            for j, b in enumerate(bullets):
                if i < j and is_near_duplicate(a, b):
                    findings.append(
                        f"near-duplicate vs bullet {j + 1} (edit distance {levenshtein(a, b)})"
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
