"""Provision the agentsmd MCP server and update-agents workflow at the user level.

Wires the catalogue MCP server plus the /update-agents skill and command into
Factory (~/.factory/) and Claude (~/.claude/) so any project on the machine can
launch and use the generator.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import click

SERVER_NAME = "agentsmd"
ENV_VAR_NAME = "AGENTSMD_MCP_URL"
_MARKER_BEGIN = "# agentsmd-install: begin"
_MARKER_END = "# agentsmd-install: end"


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


def _resolve_shell_rc(home_dir: Path, shell_env: str | None) -> Path:
    """Pick the shell profile to write AGENTSMD_MCP_URL into."""
    shell_name = Path(shell_env).name if shell_env else ""
    if shell_name == "bash":
        return home_dir / ".bashrc"
    return home_dir / ".zshrc"


def _write_env_var(rc_path: Path, server_command: str) -> None:
    """Idempotently insert/update the AGENTSMD_MCP_URL export in rc_path."""
    block = f'{_MARKER_BEGIN}\nexport {ENV_VAR_NAME}="{server_command}"\n{_MARKER_END}\n'

    existing = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""
    start = existing.find(_MARKER_BEGIN)
    end = existing.find(_MARKER_END)
    if start != -1 and end != -1:
        end += len(_MARKER_END)
        # Consume a single trailing newline after the marker so re-writes don't grow blank lines.
        if end < len(existing) and existing[end] == "\n":
            end += 1
        updated = existing[:start] + block + existing[end:]
    else:
        separator = "" if not existing or existing.endswith("\n") else "\n"
        updated = existing + separator + block

    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_path.write_text(updated, encoding="utf-8")


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
@click.option(
    "--no-shell-env",
    is_flag=True,
    default=False,
    help="Skip writing AGENTSMD_MCP_URL to the user's shell profile",
)
def main(tool: str, server_command: str, home: str | None, no_shell_env: bool) -> None:
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

    if not no_shell_env:
        rc_path = _resolve_shell_rc(home_dir, os.environ.get("SHELL"))
        _write_env_var(rc_path, server_command)
        click.echo(f"  wrote {rc_path} (export {ENV_VAR_NAME})")
        click.echo(f"Open a new shell (or `source {rc_path}`) to pick up {ENV_VAR_NAME}.")

    click.echo("Open any project and run /update-agents to generate or refresh AGENTS.md.")


if __name__ == "__main__":
    main()
