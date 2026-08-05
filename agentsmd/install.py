"""Provision the agentsmd MCP server and update-agents workflow at the user level.

Wires the catalogue MCP server plus the /update-agents skill and command into
Factory (~/.factory/) and Claude (~/.claude/) so any project on the machine can
launch and use the generator.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import click

SERVER_NAME = "agentsmd"


def _asset_root() -> Path | None:
    """Locate the bundled workflow assets, falling back to a repo checkout."""
    packaged = Path(__file__).parent / "_assets" / "workflow"
    if (packaged / "skills" / "update-agents" / "SKILL.md").is_file():
        return packaged
    repo = Path(__file__).resolve().parent.parent / ".factory"
    if (repo / "skills" / "update-agents" / "SKILL.md").is_file():
        return repo
    return None


def _server_entry(command: str) -> dict:
    return {"type": "stdio", "command": command, "connectTimeout": 30000}


def _merge_mcp(config_path: Path, command: str) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError as e:
            raise click.ClickException(f"{config_path} is not valid JSON: {e}")
    servers = data.setdefault("mcpServers", {})
    servers[SERVER_NAME] = _server_entry(command)
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _copy_workflow(asset_root: Path, tool_home: Path, written: list[str]) -> None:
    skill_src = asset_root / "skills" / "update-agents" / "SKILL.md"
    cmd_src = asset_root / "commands" / "update-agents.md"
    skill_dst = tool_home / "skills" / "update-agents" / "SKILL.md"
    cmd_dst = tool_home / "commands" / "update-agents.md"
    skill_dst.parent.mkdir(parents=True, exist_ok=True)
    cmd_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(skill_src, skill_dst)
    shutil.copyfile(cmd_src, cmd_dst)
    written.append(str(skill_dst))
    written.append(str(cmd_dst))


@click.command()
@click.option(
    "--tool",
    type=click.Choice(["factory", "claude", "both"]),
    default="both",
    help="Which agent to configure",
)
@click.option(
    "--server-command",
    default="agentsmd-server",
    help="Executable to launch the MCP server (default: agentsmd-server on PATH)",
)
@click.option(
    "--home",
    default=None,
    help="Override the home directory (mainly for testing)",
)
def main(tool: str, server_command: str, home: str | None) -> None:
    """Install the agentsmd MCP server and update-agents workflow at the user level."""
    home_dir = Path(home).expanduser() if home else Path.home()
    asset_root = _asset_root()
    if asset_root is None:
        raise click.ClickException(
            "workflow assets not found; install the package (pip/pipx) or run from a repo checkout"
        )

    written: list[str] = []
    do_factory = tool in ("factory", "both")
    do_claude = tool in ("claude", "both")

    if do_factory:
        factory_mcp = home_dir / ".factory" / "mcp.json"
        _merge_mcp(factory_mcp, server_command)
        written.append(str(factory_mcp))
        _copy_workflow(asset_root, home_dir / ".factory", written)

    if do_claude:
        claude_mcp = home_dir / ".claude.json"
        _merge_mcp(claude_mcp, server_command)
        written.append(str(claude_mcp))
        _copy_workflow(asset_root, home_dir / ".claude", written)

    click.echo(f"agentsmd-install: configured {tool} (server command: {server_command})")
    for path in written:
        click.echo(f"  wrote {path}")
    click.echo("Open any project and run /update-agents to generate or refresh AGENTS.md.")


if __name__ == "__main__":
    main()
