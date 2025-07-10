import gradio as gr

from src.mcp_census.functions.census_api import (
    fetch_dataset_data,
    fetch_dataset_examples,
    fetch_dataset_fips,
    fetch_dataset_geographies,
    fetch_dataset_required_parent_geographies,
    fetch_dataset_variables,
    fetch_datasets,
    lookup_dataset_fips,
)

with gr.Blocks() as mcp_server:
    gr.Markdown(
        """
        # U.S. Census Bureau API Gradio MCP Server
        This MCP Server allows you to interact with the U.S. Census Bureau API to fetch datasets, geographies, variables, examples, and more.

        ## Available Tooling
        - **Fetch Census Datasets**: Retrieve a list of available Census datasets.
        - **Fetch Dataset Geographies**: Get information on available geographies for a specific Census dataset.
        - **Fetch Dataset Variables**: Retrieve information on available variables for a specific Census dataset
        - **Fetch Dataset Examples**: Get example API calls for a specific Census dataset.
        - **Fetch Dataset Required Parent Geographies**: Get required parent geographies for a specific geography for a specific Census dataset.
        - **Fetch Dataset FIPS Codes**: Retrieve FIPS codes for geographies within a specific Census dataset.
        - **Lookup Dataset FIPS Codes**: Look up FIPS codes by geography name for a specific Census Dataset.

        For the full MCP schema, please refer to the [schema endpoint](/gradio_api/mcp/schema)

        ## Use this MCP Server
        ```json
        {
            "mcpServers": {
                "mcp-census": {
                    "url": "https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse"
                }
            }
        }
        ```

        Gradio has more MCP Server documentation available [here](https://www.gradio.app/guides/building-mcp-server-with-gradio).
        """
    )
    gr.api(fetch_dataset_data, api_name="fetch_dataset_data")
    gr.api(fetch_dataset_examples, api_name="fetch_dataset_examples")
    gr.api(fetch_dataset_fips, api_name="fetch_dataset_fips")
    gr.api(fetch_dataset_geographies, api_name="fetch_dataset_geographies")
    gr.api(
        fetch_dataset_required_parent_geographies,
        api_name="fetch_dataset_required_parent_geographies",
    )
    gr.api(fetch_dataset_variables, api_name="fetch_dataset_variables")
    gr.api(fetch_datasets, api_name="fetch_datasets")
    gr.api(lookup_dataset_fips, api_name="lookup_dataset_fips")


if __name__ == "__main__":
    mcp_server.launch(mcp_server=True)
