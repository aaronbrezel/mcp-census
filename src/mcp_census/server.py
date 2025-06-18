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
# TODO: For now, we're going to define all of our census python functions
# as MCP tools. However, we'll likely want to transition most of the documentation-based
# Tools into resources.
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
