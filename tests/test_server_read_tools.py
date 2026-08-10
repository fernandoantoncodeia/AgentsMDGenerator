from __future__ import annotations

import asyncio

from agentsmd import server


def test_read_tools_delegate_to_resource_payloads(monkeypatch):
    expected = {
        "categories": {"contents": [{"name": "python-project"}]},
        "curated": {"body": "- Use pytest."},
        "proposed": {"proposed": ["go-project"]},
        "config": {"agents_md_max_lines": 512},
    }

    async def categories():
        return expected["categories"]

    async def curated(category: str):
        assert category == "python-project"
        return expected["curated"]

    async def proposed_list():
        return expected["proposed"]

    async def config():
        return expected["config"]

    monkeypatch.setattr(server, "categories_resource", categories)
    monkeypatch.setattr(server, "curated_resource", curated)
    monkeypatch.setattr(server, "proposed_list_resource", proposed_list)
    monkeypatch.setattr(server, "config_resource", config)

    async def run():
        return (
            await server.list_categories_tool(),
            await server.get_curated_tool("python-project"),
            await server.list_proposed_tool(),
            await server.get_config_tool(),
        )

    assert asyncio.run(run()) == (
        expected["categories"],
        expected["curated"],
        expected["proposed"],
        expected["config"],
    )


def test_read_tool_names_are_registered():
    async def run():
        return {tool.name for tool in await server.server.list_tools()}

    tool_names = asyncio.run(run())
    assert {
        "catalogue_list_categories",
        "catalogue_get_curated",
        "catalogue_list_proposed",
        "catalogue_get_config",
    } <= tool_names
