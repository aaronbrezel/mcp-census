import gradio as gr
from mcp_functions.census_api_calls import (
    decennial_2020_demographic_profile,
    decennial_2020_demographic_profile_fips_lookup,
)
from mcp_functions.census_api_docs import (
    import_decennial_2020_datasets_homepage,
    import_decennial_2020_demographic_profile_geographies,
    import_decennial_2020_demographic_profile_variables,
)
from mcp_functions.census_utils import (
    decennial_2020_dhc_semantic_search,
    required_geograpy_hierarchy_parents,
)

decennial_2020_demographic_and_housing_characteristics_semantic_search_interface = gr.Interface(
    fn=decennial_2020_dhc_semantic_search,
    inputs=["textbox"],
    outputs=gr.JSON(),
    title="U.S. Census Bureau 2020 demographic and housing characteristics documentation",
    description="Fetches demographic and housing characteristics documentation for the 2020 U.S. Census Bureau decennial census.",
)

decennial_2020_demographic_profile_interface = gr.Interface(
    fn=decennial_2020_demographic_profile,
    inputs=["textbox", "textbox", "textbox"],
    outputs=gr.JSON(),
    title="U.S. Census Bureau 2020 Demographic Profile data",
    description="Fetches demographic profile data from the 2020 U.S. Census Bureau decennial API.",
)

decennial_2020_demographic_profile_fips_lookup_interface = gr.Interface(
    fn=decennial_2020_demographic_profile_fips_lookup,
    inputs=["textbox", "textbox", "textbox"],
    outputs=gr.JSON(),
    title="FIPS code lookup for the U.S. Census Bureau 2020 decennial census demographic profile dataset",
    description="Lookup FIPS codes for geography hierarchies provided by the U.S. Census Bureau 2020 decennial census demographic profile dataset",
)

decennial_2020_demographic_profile_geographies_required_parent_geographies_interface = gr.Interface(
    fn=required_geograpy_hierarchy_parents,
    inputs=["textbox"],
    outputs=gr.JSON(),
    title="Geography Hierarchy required parent geographies",
    description="Utility function that provides required parent geographies when requesting geography hierarchies during U.S. Census Bureau 2020 decennial census demographic profile API calls",
)

decennial_2020_demographic_profile_geographies_interface = gr.Interface(
    fn=import_decennial_2020_demographic_profile_geographies,
    inputs=[],
    outputs=gr.TextArea(),
    title="U.S. Census Bureau 2020 decennial census demographic profile dataset geographies",
    description="Information on available geographies for the the U.S. Census Bureau 2020 decennial census demographic profile API.",
)

decennial_2020_demographic_profile_variables_interface = gr.Interface(
    fn=import_decennial_2020_demographic_profile_variables,
    inputs=[],
    outputs=gr.TextArea(),
    title="U.S. Census Bureau 2020 decennial census demographic profile dataset variables",
    description="Information on available variables for the the U.S. Census Bureau 2020 decennial census demographic profile API.",
)


decennial_2020_datasets_homepage_interface = gr.Interface(
    fn=import_decennial_2020_datasets_homepage,
    inputs=[],
    outputs=gr.TextArea(),
    title="U.S. Census Bureau 2020 decennial census datasets",
    description="Recieve information on available datasets as well as links to helpful documentation",
)


demo = gr.TabbedInterface(
    [
        decennial_2020_datasets_homepage_interface,
        decennial_2020_demographic_profile_geographies_interface,
        decennial_2020_demographic_profile_variables_interface,
        decennial_2020_demographic_profile_geographies_required_parent_geographies_interface,
        decennial_2020_demographic_profile_fips_lookup_interface,
        decennial_2020_demographic_profile_interface,
        decennial_2020_demographic_and_housing_characteristics_semantic_search_interface,
    ],
    [
        "2020 U.S. Census Bureau decennial census API Homepage",
        "2020 U.S. Census Bureau decennial census demographic profile API geographies",
        "2020 U.S. Census Bureau decennial census demographic profile API variables",
        "2020 U.S. Census Bureau decennial census demographic profile geography hierarchy required parent geographies",
        "2020 U.S. Census Bureau decennial census demographic profile geography hierarchy FIPS code lookup",
        "2020 U.S. Census Bureau decennial census demographic profile API data",
        "2020 U.S. Census Bureau decennial census demographic and housing characteristics documentation",
    ],
)


if __name__ == "__main__":
    demo.launch(mcp_server=True)
