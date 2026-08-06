"""Deterministic operator CLI for the AgentsMDGenerator catalogue."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import click

from . import catalogue


def _resolve_or_exit() -> None:
    try:
        catalogue.resolve_catalogue_dir()
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@click.group()
@click.option(
    "--catalogue-root",
    default=None,
    help="Path to the prompt-catalogue directory (or a directory containing it)",
)
def main(catalogue_root: str | None) -> None:
    """agentsmd — operator CLI for the AgentsMDGenerator catalogue."""
    catalogue.set_catalogue_root(catalogue_root)


@main.command()
@click.argument("category")
@click.option("--body", required=True, help="Body text to append")
@click.option("--no-trim-tails", is_flag=True, help="Skip trailer trimming")
@click.option("--title", help="Category title for new files")
def addcontent(category: str, body: str, no_trim_tails: bool, title: str | None) -> None:
    """Append a pre-trimmed entry to a proposed category."""
    _resolve_or_exit()
    try:
        path, logs = catalogue.addcontent(
            category, body, title=title, no_trim_tails=no_trim_tails
        )
        click.echo(f"addcontent: wrote {path}")
        for log in logs:
            click.echo(f"  - {log}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("name")
@click.option("--trigger", required=True, help="Trigger rule")
@click.option("--body", required=True, help="Starter body")
@click.option("--title", help="Category title")
def addcategory(name: str, trigger: str, body: str, title: str | None) -> None:
    """Create a proposed category with a starter body."""
    _resolve_or_exit()
    try:
        path, logs = catalogue.addcategory(name, trigger, body, title=title)
        click.echo(f"addcategory: wrote {path}")
        for log in logs:
            click.echo(f"  - {log}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("category")
@click.option("--force", is_flag=True, help="Override size/bullet-length caps")
def curatecontent(category: str, force: bool) -> None:
    """Merge a proposed category into curated."""
    _resolve_or_exit()
    try:
        path = catalogue.curatecontent(category, force=force)
        click.echo(f"curatecontent: promoted {path}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


# Generic trigger words that do not, on their own, indicate two categories
# describe the same kind of project. Overlap on these must not flag a remap.
_TRIGGER_STOPWORDS = frozenset(
    {
        "project", "contains", "contain", "containing", "or", "and", "a", "an",
        "the", "of", "in", "on", "to", "with", "for", "that", "is", "are", "any",
        "files", "file", "present", "src", "main", "source", "sources", "tree",
        "directory", "directories", "depending", "declaring", "extensions",
        "docs", "named", "code", "repo", "repository",
    }
)


def _trigger_tokens(trigger: str | None) -> set[str]:
    """Return the distinctive lowercase tokens of a trigger expression.

    Tokens start with an alphanumeric and may include . _ * - so that dotted
    filenames (e.g. package.swift, pom.xml) stay whole and do not collide on a
    shared bare stem. Generic words are dropped so unrelated triggers do not
    appear to overlap.
    """
    tokens = re.findall(r"[a-z0-9][a-z0-9._*\-]*", (trigger or "").lower())
    return {t for t in tokens if len(t) > 2 and t not in _TRIGGER_STOPWORDS}


@main.command()
def caps() -> None:
    """Print the resolved line caps and the source that won each resolution."""
    _resolve_or_exit()
    try:
        c = catalogue.resolved_caps()
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    click.echo(f"category_max_lines:  {c.category_max_lines} ({c.sources['category_max_lines']})")
    click.echo(f"agents_md_max_lines: {c.agents_md_max_lines} ({c.sources['agents_md_max_lines']})")
    click.echo(f"agents_md_max_bytes: {c.agents_md_max_bytes} ({c.sources['agents_md_max_bytes']})")


@main.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Override size/bullet-length caps")
@click.option("--no-trim-tails", is_flag=True, help="Skip the trailer-trim phase")
def recurate(name: str, force: bool, no_trim_tails: bool) -> None:
    """Re-sweep a curated category: dedupe near-duplicate bullets and trim trailers."""
    _resolve_or_exit()
    try:
        path, logs = catalogue.recurate(
            name, force=force, trim_tails=not no_trim_tails
        )
        click.echo(f"recurate: rewrote {path}")
        for log in logs:
            click.echo(f"  - {log}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Override size/bullet-length caps")
@click.option(
    "--no-remap",
    is_flag=True,
    help="Promote as-is even if genuine remap candidates exist; leave other drafts untouched",
)
def curatecategory(name: str, force: bool, no_remap: bool) -> None:
    """Promote a proposed category to curated."""
    _resolve_or_exit()
    try:
        # A remap candidate is another proposed entry whose trigger shares
        # distinctive evidence with this one; generic words are ignored.
        own_tokens = _trigger_tokens(catalogue.read_frontmatter(name, proposed=True).get("trigger"))
        candidates = [
            p
            for p in catalogue.list_proposed()
            if p != name
            and own_tokens & _trigger_tokens(
                catalogue.read_frontmatter(p, proposed=True).get("trigger")
            )
        ]
        if candidates and not no_remap:
            click.echo(f"remap candidates: {', '.join(candidates)}")
            click.echo(
                "not promoted: these drafts share trigger evidence. Re-run with "
                "--no-remap to promote as-is, or curate/remove the listed drafts first."
            )
            sys.exit(0)
        path = catalogue.curatecategory(name, force=force)
        click.echo(f"curatecategory: promoted {path}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
def list_cmd() -> None:
    """List curated and proposed categories."""
    _resolve_or_exit()
    curated = {c.name for c in catalogue.list_curated()}
    proposed = set(catalogue.list_proposed())
    click.echo("Curated:")
    for name in sorted(curated):
        click.echo(f"  {name}")
    click.echo("Proposed:")
    for name in sorted(proposed):
        click.echo(f"  {name}")
    pending = curated & proposed
    if pending:
        click.echo("Pending curation:")
        for name in sorted(pending):
            click.echo(f"  {name}")


@main.command()
def status() -> None:
    """Run the catalog self-discipline scan."""
    _resolve_or_exit()
    results = catalogue.self_discipline_scan()
    for name, findings in results:
        for finding in findings:
            click.echo(f"{name}: {finding}")


@main.command()
@click.option(
    "--source",
    multiple=True,
    help="Additional ad-hoc source URL",
)
def browsecontent(source: tuple[str, ...]) -> None:
    """Fetch six canonical sources, diff, and emit suggested commands."""
    _resolve_or_exit()
    canonical = [
        "https://agents.md/",
        "https://github.com/agentsmd/agents.md",
        "https://www.builder.io/blog/agents-md",
        "https://www.morphllm.com/agents-md-guide",
        "https://blakecrosley.com/blog/agents-md-patterns",
        "https://asdlc.io/practices/agents-md-spec/",
        "https://www.betterclaw.io/blog/agents-md-best-practices",
    ]
    urls = list(canonical) + list(source)
    results = catalogue.fetch_sources(urls)
    click.echo("Source freshness:")
    for r in results:
        status_code = r.get("status") or "error"
        last = r.get("last_modified") or "n/a"
        click.echo(f"  {r['url']} — {status_code} (last-modified: {last})")
    failures = [r for r in results if (r.get("status") or 0) >= 400]
    if failures:
        click.echo("Hard source failures detected; no catalogue updates proposed.")
        sys.exit(1)

    # Minimal diff: compare source titles/keywords against existing curated titles
    curated = catalogue.list_curated()
    curated_titles = {c.title.lower() for c in curated}
    click.echo("\nDiff summary:")
    for r in results:
        text = r.get("body", "")
        if not text:
            continue
        # Very simple heuristic: look for section headings in the source
        headings = re.findall(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)
        for heading in headings:
            key = heading.lower()
            if any(key in title for title in curated_titles):
                continue
            # Suggest a new category if heading looks like an agent instruction
            if any(word in key for word in ["agent", "prompt", "instruction", "rule"]):
                slug = re.sub(r"[^a-z0-9]+", "-", key).strip("-")[:40]
                click.echo(
                    f"[generic] Run: agentsmd addcategory {slug} --trigger \"*\" --body \"{heading}\""
                )
    click.echo("\nno drift detected — review the commands above and run manually.")


if __name__ == "__main__":
    main()
