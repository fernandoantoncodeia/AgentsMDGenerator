"""MCP server for the AgentsMDGenerator catalogue."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import click
from mcp.server import MCPServer
from mcp.server.mcpserver.context import Context

from . import catalogue
from .mcp_types import (
    RESOURCE_CATEGORIES,
    RESOURCE_CONFIG,
    RESOURCE_CURATED,
    RESOURCE_PROPOSED,
    RESOURCE_PROPOSED_LIST,
    TOOL_ADDCATEGORY,
    TOOL_ADDCONTENT,
    TOOL_CURATECATEGORY,
    TOOL_CURATECONTENT,
    TOOL_FETCH_SOURCES,
)

OPERATOR_CLIENT_NAME = "agentsmd-operator-cli"


def _is_operator(ctx: Context | None) -> bool:
    """Return True if the current MCP client is the operator CLI.

    The client declares its name during MCP initialize; the operator CLI
    connects with clientInfo.name == OPERATOR_CLIENT_NAME. An explicit
    AGENTSMD_OPERATOR=1 environment flag on the server also grants operator
    rights (used by stdio deployments the operator runs locally).
    """
    if os.environ.get("AGENTSMD_OPERATOR") == "1":
        return True
    if ctx is None:
        return False
    try:
        client_params = ctx.session.client_params
    except Exception:
        return False
    if client_params is None:
        return False
    client_info = getattr(client_params, "client_info", None)
    if client_info is None:
        return False
    return getattr(client_info, "name", "") == OPERATOR_CLIENT_NAME


def _operator_only(ctx: Context | None) -> None:
    if not _is_operator(ctx):
        raise RuntimeError(
            "curation tools are restricted to operators; use agentsmd curatecontent in the master repo"
        )


def _result(ok: bool, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": ok, "message": message, **(data or {})}


server = MCPServer("agentsmd-mcp-server")


@server.resource(RESOURCE_CATEGORIES)
async def categories_resource() -> dict[str, Any]:
    """Return metadata for all curated categories."""
    try:
        cats = catalogue.list_curated()
        return {
            "contents": [
                {
                    "name": c.name,
                    "title": c.title,
                    "trigger": c.trigger,
                    "heuristic": c.heuristic,
                }
                for c in cats
            ]
        }
    except catalogue.CatalogueError as e:
        return {"error": str(e)}


@server.resource(RESOURCE_CONFIG)
async def config_resource() -> dict[str, Any]:
    """Return the resolved line caps and the source that won each resolution."""
    try:
        caps = catalogue.resolved_caps()
        return {
            "category_max_lines": caps.category_max_lines,
            "agents_md_max_lines": caps.agents_md_max_lines,
            "agents_md_max_bytes": caps.agents_md_max_bytes,
            "sources": caps.sources,
        }
    except catalogue.CatalogueError as e:
        return {"error": str(e)}


@server.resource(RESOURCE_PROPOSED_LIST)
async def proposed_list_resource() -> dict[str, Any]:
    """Return the list of proposed category names."""
    try:
        return {"proposed": catalogue.list_proposed()}
    except catalogue.CatalogueError as e:
        return {"error": str(e)}


@server.resource(RESOURCE_CURATED)
async def curated_resource(category: str) -> dict[str, Any]:
    """Return the body of a curated category."""
    try:
        body = catalogue.read_body(category, proposed=False)
        if body is None:
            return {"error": "not found", "category": category}
        return {"body": body}
    except catalogue.CatalogueError as e:
        return {"error": str(e)}


@server.resource(RESOURCE_PROPOSED)
async def proposed_resource(category: str) -> dict[str, Any]:
    """Return the body of a proposed category."""
    try:
        body = catalogue.read_body(category, proposed=True)
        if body is None:
            return {"error": "not found", "category": category}
        return {"body": body}
    except catalogue.CatalogueError as e:
        return {"error": str(e)}


@server.tool(name=TOOL_ADDCONTENT)
async def addcontent_tool(
    category: str,
    body: str,
    no_trim_tails: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Append a bullet to a proposed category."""
    try:
        path, logs = catalogue.addcontent(category, body, no_trim_tails=no_trim_tails)
        return _result(
            True,
            f"addcontent: wrote {path}",
            {"path": str(path), "logs": logs},
        )
    except catalogue.RefusalError as e:
        return _result(False, str(e))
    except catalogue.CatalogueError as e:
        return _result(False, str(e))


@server.tool(name=TOOL_ADDCATEGORY)
async def addcategory_tool(
    name: str,
    trigger: str,
    body: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a proposed category with a starter body."""
    try:
        path, logs = catalogue.addcategory(name, trigger, body)
        return _result(
            True,
            f"addcategory: wrote {path}",
            {"path": str(path), "logs": logs},
        )
    except catalogue.RefusalError as e:
        return _result(False, str(e))
    except catalogue.CatalogueError as e:
        return _result(False, str(e))


@server.tool(name=TOOL_CURATECONTENT)
async def curatecontent_tool(
    category: str,
    force: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Merge a proposed category into the curated category."""
    _operator_only(ctx)
    try:
        path = catalogue.curatecontent(category, force=force)
        return _result(True, f"curatecontent: promoted {path}", {"path": str(path)})
    except catalogue.RefusalError as e:
        return _result(False, str(e))
    except catalogue.CatalogueError as e:
        return _result(False, str(e))


@server.tool(name=TOOL_CURATECATEGORY)
async def curatecategory_tool(
    name: str,
    force: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Promote a proposed category to curated."""
    _operator_only(ctx)
    try:
        path = catalogue.curatecategory(name, force=force)
        return _result(True, f"curatecategory: promoted {path}", {"path": str(path)})
    except catalogue.RefusalError as e:
        return _result(False, str(e))
    except catalogue.CatalogueError as e:
        return _result(False, str(e))


@server.tool(name=TOOL_FETCH_SOURCES)
async def fetch_sources_tool(urls: list[str]) -> dict[str, Any]:
    """Fetch raw bodies from a list of URLs."""
    try:
        results = catalogue.fetch_sources(urls)
        return {"sources": results}
    except Exception as e:
        return _result(False, str(e))


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport protocol",
)
@click.option("--port", default=3000, help="Port for SSE transport")
@click.option("--host", default="127.0.0.1", help="Host for SSE transport")
@click.option(
    "--catalogue-root",
    default=None,
    help="Path to the prompt-catalogue directory (or a directory containing it)",
)
def main(transport: str, port: int, host: str, catalogue_root: str | None) -> None:
    """Run the agentsmd MCP server."""
    catalogue.set_catalogue_root(catalogue_root)
    try:
        catalogue.resolve_catalogue_dir()
    except catalogue.CatalogueError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)

    if transport == "stdio":
        asyncio.run(server.run_stdio_async())
    else:
        asyncio.run(server.run_sse_async(host=host, port=port))


if __name__ == "__main__":
    main()
