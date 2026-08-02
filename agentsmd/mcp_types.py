"""MCP resource URI and tool name constants."""

from __future__ import annotations

RESOURCE_CATEGORIES = "catalogue://categories"
RESOURCE_CURATED = "catalogue://curated/{category}"
RESOURCE_PROPOSED = "catalogue://proposed/{category}"
RESOURCE_PROPOSED_LIST = "catalogue://proposed-list"

TOOL_ADDCONTENT = "catalogue_addcontent"
TOOL_ADDCATEGORY = "catalogue_addcategory"
TOOL_CURATECONTENT = "catalogue_curatecontent"
TOOL_CURATECATEGORY = "catalogue_curatecategory"
TOOL_FETCH_SOURCES = "catalogue_fetch_sources"
