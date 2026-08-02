"""Deterministic operator CLI for the AgentsMDGenerator catalogue."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import click

from . import catalogue


def _ensure_master_repo() -> None:
    if not Path("prompt-catalogue").is_dir():
        click.echo(
            "error: not in the AgentsMDGenerator master repo; prompt-catalogue/ not found",
            err=True,
        )
        sys.exit(1)


@click.group()
def main() -> None:
    """agentsmd — operator CLI for the AgentsMDGenerator catalogue."""
    pass


@main.command()
@click.argument("category")
@click.option("--body", required=True, help="Body text to append")
@click.option("--no-trim-tails", is_flag=True, help="Skip trailer trimming")
@click.option("--title", help="Category title for new files")
def addcontent(category: str, body: str, no_trim_tails: bool, title: str | None) -> None:
    """Append a pre-trimmed entry to a proposed category."""
    _ensure_master_repo()
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
    _ensure_master_repo()
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
    _ensure_master_repo()
    try:
        path = catalogue.curatecontent(category, force=force)
        click.echo(f"curatecontent: promoted {path}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Override size/bullet-length caps")
def curatecategory(name: str, force: bool) -> None:
    """Promote a proposed category to curated."""
    _ensure_master_repo()
    try:
        # Check for remap candidates: other proposed entries with overlapping trigger text
        proposed = catalogue.list_proposed()
        candidates = [
            p
            for p in proposed
            if p != name and catalogue.read_body(p, proposed=True)
        ]
        if candidates:
            click.echo(f"remap candidates: {', '.join(candidates)}")
            click.echo("confirm each remap explicitly before proceeding")
            sys.exit(0)
        path = catalogue.curatecategory(name, force=force)
        click.echo(f"curatecategory: promoted {path}")
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@main.command()
def list_cmd() -> None:
    """List curated and proposed categories."""
    _ensure_master_repo()
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
    _ensure_master_repo()
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
    _ensure_master_repo()
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
