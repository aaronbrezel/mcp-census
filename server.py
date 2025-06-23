from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from src.mcp_census.functions.census_api_calls import (
    dec2020_dp,
    dec2020_dp_fips_lookup,
)
from src.mcp_census.functions.census_api_docs import (
    import_dec2020_datasets_homepage,
    import_dec2020_dp_geographies,
    import_dec2020_dp_variables,
)
from src.mcp_census.functions.census_utils import (
    dec2020_dhc_semantic_search,
    required_geograpy_hierarchy_parents,
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
    fn=import_dec2020_datasets_homepage,
    annotations=ToolAnnotations(title="DEC2020 Datasets homepage", readOnlyHint=True),
)
mcp.add_tool(
    fn=import_dec2020_dp_geographies,
    annotations=ToolAnnotations(
        title="DEC2020 DP Dataset geographies", readOnlyHint=True
    ),
)
mcp.add_tool(
    fn=import_dec2020_dp_variables,
    annotations=ToolAnnotations(
        title="DEC2020 DP Dataset variables", readOnlyHint=True
    ),
)

mcp.add_tool(
    fn=dec2020_dp,
    annotations=ToolAnnotations(title="DEC2020 DP Dataset request", readOnlyHint=True),
)
mcp.add_tool(
    fn=dec2020_dp_fips_lookup,
    annotations=ToolAnnotations(
        title="DEC2020 DP Dataset fips lookup", readOnlyHint=True
    ),
)

mcp.add_tool(
    fn=dec2020_dhc_semantic_search,
    annotations=ToolAnnotations(title="DEC2020 DHC Documentation", readOnlyHint=True),
)
mcp.add_tool(
    fn=required_geograpy_hierarchy_parents,
    annotations=ToolAnnotations(
        title="DEC2020 DP Dataset geographic hierarchies", readOnlyHint=True
    ),
)

if __name__ == "__main__":
    mcp.run()
