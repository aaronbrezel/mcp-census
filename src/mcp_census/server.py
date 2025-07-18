from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
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


@mcp.prompt()
def census_question_workflow(question: str) -> list[base.Message]:
    """Guide systematic Census data analysis with step-by-step tool usage."""
    return [
        base.UserMessage("A user has asked a question about census data:"),
        base.UserMessage(question),
        base.AssistantMessage(
            "Follow this systematic workflow to answer Census questions:\n\n"
            "🔍 **Step 1: Understand the Question**\n"
            "   - Identify what data is needed (population, income, housing, etc.)\n"
            "   - Determine the geographic scope (state, county, tract, etc.)\n"
            "   - Note the time period of interest\n\n"
            "📊 **Step 2: Find Relevant Datasets**\n"
            "   - Use `fetch_datasets` with a descriptive query\n"
            "   - Include year filter if specific time period needed\n\n"
            "🔢 **Step 3: Explore Variables**\n"
            "   - Use `fetch_dataset_variables` to find specific data points\n"
            "   - Use semantic query to filter thousands of variables\n\n"
            "🗺️ **Step 4: Check Geographic Availability**\n"
            "   - Use `fetch_dataset_geographies` to see available levels\n"
            "   - Use `fetch_dataset_required_parent_geographies` if needed\n\n"
            "📍 **Step 5: Handle Geographic Names**\n"
            "   - Use `lookup_dataset_fips` to convert place names to FIPS codes\n"
            "   - Use `fetch_dataset_fips` to explore available areas\n\n"
            "📈 **Step 6: Retrieve Data**\n"
            "   - Use `fetch_dataset_data` with proper parameters\n"
            "   - target_geographies: what areas you want data for\n"
            "   - parent_geographies: required parent constraints\n\n"
            "💡 **Need Help?** Use `fetch_dataset_examples` for usage patterns"
        ),
        base.AssistantMessage("Let's systematically work through your Census question."),
    ]


mcp.add_tool(
    fn=fetch_datasets,
    annotations=ToolAnnotations(
        title="🔍 Search Census Datasets",
        description="Search for relevant Census datasets using semantic search. Start here to find datasets matching your data needs.",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=fetch_dataset_geographies,
    annotations=ToolAnnotations(
        title="🗺️ Get Available Geographic Levels",
        description="Discover what geographic levels (state, county, tract, etc.) are available for a dataset.",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_variables,
    annotations=ToolAnnotations(
        title="🔢 Explore Dataset Variables",
        description="Find specific data variables in a dataset. Use semantic query to filter thousands of variables to relevant ones.",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_examples,
    annotations=ToolAnnotations(
        title="💡 Get Dataset Usage Examples",
        description="See example API calls for proper usage patterns. Use when unsure how to structure your data request.",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_required_parent_geographies,
    annotations=ToolAnnotations(
        title="🔗 Check Required Parent Geographies",
        description="Find what parent geographies are needed for a specific geographic level (e.g., tracts require county and state).",
        readOnlyHint=True,
    ),
)
mcp.add_tool(
    fn=fetch_dataset_fips,
    annotations=ToolAnnotations(
        title="📍 Browse Available FIPS Codes",
        description="Explore all available FIPS codes for a geographic level. Helpful for discovering available counties, tracts, etc.",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=lookup_dataset_fips,
    annotations=ToolAnnotations(
        title="🔍 Convert Place Names to FIPS Codes",
        description="Convert place names (like 'Los Angeles County') to FIPS codes needed for data requests.",
        readOnlyHint=True,
    ),
)

mcp.add_tool(
    fn=fetch_dataset_data,
    annotations=ToolAnnotations(
        title="📈 Retrieve Census Data",
        description="Get actual Census data values. Use as final step after identifying variables and geographies. Requires proper target_geographies and parent_geographies parameters.",
        readOnlyHint=True,
    ),
)
