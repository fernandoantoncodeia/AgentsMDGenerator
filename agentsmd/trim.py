"""Trim-pass logic for catalogue entries."""

from __future__ import annotations

import re
from typing import Iterable


MAX_BULLET_LEN = 200
DEDUPE_DISTANCE = 30


def levenshtein(a: str, b: str) -> int:
    """Return the Levenshtein distance between two strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    curr = [0] * (len(b) + 1)
    for i, ca in enumerate(a, 1):
        curr[0] = i
        for j, cb in enumerate(b, 1):
            insert = prev[j] + 1
            delete = curr[j - 1] + 1
            replace = prev[j - 1] + (0 if ca == cb else 1)
            curr[j] = min(insert, delete, replace)
        prev, curr = curr, prev
    return prev[len(b)]


def _trim_trailer(bullet: str) -> tuple[str, str | None]:
    """Drop a single verbose trailing clause from a bullet. Return (trimmed, trailer).

    Trailers are matched only in the final sentence and anchored to the end of
    the bullet, so the whole trailing clause is removed at once. This avoids
    breaking a bullet mid-token (e.g. the dot inside ``requirements.txt``).
    """
    # Operate only on the last sentence so connectives inside earlier sentences
    # are never touched.
    boundary = list(re.finditer(r"(?<=[.!?])\s+", bullet))
    head = bullet[: boundary[-1].end()] if boundary else ""
    tail = bullet[boundary[-1].end() :] if boundary else bullet

    patterns = [
        r",?\s+where\s+.+$",
        r",?\s+in which case\s+.+$",
        r"\s*;\s*note that\s+.+$",
    ]
    for pattern in patterns:
        match = re.search(pattern, tail, flags=re.IGNORECASE)
        if match:
            trailer = match.group(0).strip()
            new_tail = tail[: match.start()].strip()
            if not new_tail:
                # The whole final sentence is the trailer; nothing to keep.
                continue
            if not new_tail.endswith((".", ";", ":", "!", "?")):
                new_tail = new_tail.rstrip(",") + "."
            return (head + new_tail).strip(), trailer
    return bullet, None


def trim_tail(bullet: str) -> tuple[str, str | None]:
    """Trim verbose trailers from a bullet until no more are found."""
    original = bullet
    trailers: list[str] = []
    while True:
        trimmed, trailer = _trim_trailer(bullet)
        if trailer is None:
            break
        bullet = trimmed
        trailers.append(trailer)
    if trailers:
        return bullet, " ".join(trailers)
    return original, None


def split_long_bullet(bullet: str) -> list[str]:
    """Split a bullet >200 chars at the first sentence boundary.

    Returns a list of one or two bullets. If a half is still >200 chars, the
    caller should treat that as a failure rather than recurse indefinitely.
    """
    if len(bullet) <= MAX_BULLET_LEN:
        return [bullet]
    match = re.search(r"(?<=[.!?])\s+", bullet)
    if not match:
        return [bullet]
    first = bullet[: match.end()].strip()
    second = bullet[match.end() :].strip()
    if not second:
        return [bullet]
    return [first, second]


def dedupe(bullets: list[str], existing: Iterable[str]) -> tuple[list[str], int]:
    """Drop bullets whose edit distance to any existing bullet is ≤30 chars."""
    dropped = 0
    kept: list[str] = []
    existing_list = list(existing)
    for bullet in bullets:
        if any(levenshtein(bullet, ex) <= DEDUPE_DISTANCE for ex in existing_list):
            dropped += 1
            continue
        kept.append(bullet)
    return kept, dropped


def pre_trim(
    bullets: list[str],
    existing_curated: Iterable[str] | None = None,
    existing_proposed: Iterable[str] | None = None,
    trim_tails: bool = True,
) -> tuple[list[str], list[str]]:
    """Run the full pre-trim pass on a list of bullets.

    Returns (trimmed_bullets, log_lines). The log lines describe dedupe,
    tail-trim, and split actions taken.
    """
    logs: list[str] = []
    existing = list(existing_curated or []) + list(existing_proposed or [])

    # 1. Trim tails
    trimmed: list[str] = []
    for i, bullet in enumerate(bullets):
        if trim_tails:
            new_bullet, trailer = trim_tail(bullet)
            if trailer:
                logs.append(f"trim tail on bullet {i + 1} (dropped \"{trailer}\")")
        else:
            new_bullet = bullet
        trimmed.append(new_bullet)

    # 2. Dedupe
    kept, dropped = dedupe(trimmed, existing)
    if dropped:
        logs.append(f"dedupe {dropped} bullets vs curated")

    # 3. Split long bullets
    result: list[str] = []
    for i, bullet in enumerate(kept):
        if len(bullet) > MAX_BULLET_LEN:
            halves = split_long_bullet(bullet)
            if len(halves) == 2 and all(len(h) <= MAX_BULLET_LEN for h in halves):
                result.extend(halves)
                logs.append(f"split bullet {i + 1} into two bullets")
                continue
            # If split didn't help or a half is still too long, keep it and let
            # the caller refuse after pre-trim.
        result.append(bullet)

    return result, logs


def scan_bullets(bullets: list[str]) -> list[str]:
    """Return a list of findings for bullets that violate the length cap."""
    findings: list[str] = []
    for i, bullet in enumerate(bullets, 1):
        if len(bullet) > MAX_BULLET_LEN:
            findings.append(f"bullet {i} exceeds {MAX_BULLET_LEN} chars ({len(bullet)} chars)")
    return findings
