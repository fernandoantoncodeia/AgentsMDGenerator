"""MCP resource URI and tool name constants."""

from __future__ import annotations

RESOURCE_CATEGORIES = "catalogue://categories"
RESOURCE_CURATED = "catalogue://curated/{category}"
RESOURCE_PROPOSED = "catalogue://proposed/{category}"
RESOURCE_PROPOSED_LIST = "catalogue://proposed-list"
RESOURCE_CONFIG = "catalogue://config"

TOOL_ADDCONTENT = "catalogue_addcontent"
TOOL_ADDCATEGORY = "catalogue_addcategory"
TOOL_CURATECONTENT = "catalogue_curatecontent"
TOOL_CURATECATEGORY = "catalogue_curatecategory"
TOOL_FETCH_SOURCES = "catalogue_fetch_sources"
TOOL_LIST_CATEGORIES = "catalogue_list_categories"
TOOL_GET_CURATED = "catalogue_get_curated"
TOOL_LIST_PROPOSED = "catalogue_list_proposed"
TOOL_GET_CONFIG = "catalogue_get_config"
