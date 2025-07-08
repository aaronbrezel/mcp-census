from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .functions.census_api import (
    fetch_dataset_data,
    fetch_dataset_examples,
    fetch_dataset_fips,
    fetch_dataset_geographies,
    fetch_dataset_required_parent_geographies,
    fetch_dataset_variables,
    fetch_datasets,
    lookup_dataset_fips,
)

mcp = FastMCP("MCP Census")

# Define MCP Tools, Resources, Prompts and Samplings

################
# Census API dataset documentation as MCP Resources. Think of resources as "plugins" to the
# LLM context window that give it a starting knowledge base.
# Resource uri guide: https://modelcontextprotocol.io/docs/concepts/resources#resource-uris
# TODO: Unfortunately, this configuration runs afoul of Claude Desktop's context size limit
#       We'll need to find a way to help the LLM understand what datasets are available without
#       blowing up the context size. Tooling may be the way to go
################
# @mcp.resource("census://data")
# async def fetch_census_datasets() -> str:
#     """
#     Fetch the list of available datasets from the Census Data API
#     """
#     url = "https://api.census.gov/data.html"

#     async with httpx.AsyncClient() as client:
#         resp = await client.get(url)
#         resp.raise_for_status()
#         return markdownify(resp.text.strip())
# @mcp.resource("census://data/{year}/{endpoint}")
# async def fetch_census_dataset(year: str, endpoint: str) -> str:
#     """Fetch raw metadata or documentation from the Census Data API."""
#     url = f"https://api.census.gov/data/{year}/{endpoint}.html"
#     async with httpx.AsyncClient() as client:
#         resp = await client.get(url)
#         resp.raise_for_status()
#         return markdownify(resp.text.strip())


mcp.add_tool(
    fn=fetch_datasets,
    annotations=ToolAnnotations(
        title="Fetch Census Datasets by Year",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=fetch_dataset_geographies,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Geographies",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_variables,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Variables",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_examples,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Example API Calls",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_required_parent_geographies,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Required Geographies",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_fips,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Geography FIPS Codes",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=lookup_dataset_fips,
    annotations=ToolAnnotations(
        title="Census Dataset FIPS Codes lookup by name",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=fetch_dataset_data,
    annotations=ToolAnnotations(
        title="Fetch Census Dataset Data",
        readOnlyHint=True,
    ),
)
