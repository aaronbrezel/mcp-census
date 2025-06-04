import os
from typing import List, Tuple

import gradio as gr
import requests
from dotenv import load_dotenv

from utils import build_fips_lookup, find_required_in_clauses

load_dotenv()  # Loads variables from a .env file into os.environ
API_KEY: str | None = os.getenv("CENSUS_API_KEY", None)
if not API_KEY:
    # If no API key is found, immediately raise an error to stop execution
    raise ValueError("Set a CENSUS_API_KEY environment variable")

# Base URL for the 2020 Decennial Census Data Profile (DP) endpoint
BASE_URL = "https://api.census.gov/data/2020/dec/dp"


def fips_translation_2020(
    geography_hierarchy: str,
    name: str,
    required_parent_geographies: List[Tuple[str, int]] | None = None,
) -> dict:
    """
    Fetches FIPS code for a given geography hierarchy and name.

    Args:
        geography_hierarchy (str): The geographic level to query (e.g. 'region', 'state', 'county').
        name (str): The name of the geographic entity (e.g., 'California', 'Los Angeles County, California').
        required_parent_geographies (List[Tuple[str, int]], optional): List of tuples specifying required parent geographies
            and their FIPS codes. Each tuple should be in the format (parent_geography, fips_code).
    Returns:
        Dict[str, str]: dictionary representing FIPS code values for provided geography_hierarchy.
    """

    BASE_URL = "https://api.census.gov/data/2020/dec/dp"

    variables = ["NAME"]
    for_clause = f"{geography_hierarchy}:*"
    params = {"get": variables, "for": for_clause, "key": API_KEY}
    if required_parent_geographies:
        in_clause = " ".join(
            [
                f"{parent_geography}:{code}"
                for parent_geography, code in required_parent_geographies
            ]
        )
        params["in"] = in_clause

    try:
        response = requests.get(BASE_URL, params=params)
        # Store text in case of error
        error_text = response.text
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        if error_text == "error: unknown/unsupported geography hierarchy":
            required_in_clauses = find_required_in_clauses(geography_hierarchy)
            print(required_in_clauses)
            raise ValueError(
                "Invalid geography hierarchy provided.",
                "Acceptable required_parent_geographies must be provided.",
                f"{geography_hierarchy} requires the following parent geographies: {required_in_clauses}",
            )
        raise RuntimeError(f"Failed to fetch data from the Census API: {e} ") from e

    # Right now, build_fips_lookup builds a lookup table that includes the FIPS code for
    # The requested geogrpahy and all of its parent geographies.
    # If we only want the FIPS code for the requested geography, we can modify this function.
    lookup = build_fips_lookup(data)

    try:
        return lookup[name]
    except KeyError:
        raise KeyError(
            f"Could not find FIPS code for {name} in {geography_hierarchy}."
            f"Ensure the name is correct. Perhaps you need to include a parent geography in the name?"
        )


def demographic_profile_2020(
    get_variables: str, for_clause: str, in_clauses: str | None = None
):
    """
    Fetches demographic profile data from the U.S. Census Bureau API.

    Args:
        get_variables (str): The Census variables to retreive, comma-separated.
        for_clause (str): The geographic level to query (e.g., 'us:*', 'state:06', 'state:04,06').
        in_clause (str, optional): Higher-level geography for nested queries (e.g., 'state:06').

    Returns:
        list[dict]: Parsed response with column headers and row data as dictionaries.
    """
    BASE_URL = "https://api.census.gov/data/2020/dec/dp"

    params = [("get", get_variables), ("for", for_clause), ("key", API_KEY)]
    if in_clauses:
        for in_clause in in_clauses.split(","):
            params.append(("in", in_clause))

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Convert to list of dicts for easier handling
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]


demo = gr.Interface(
    fn=fips_translation_2020,
    inputs=["textbox", "textbox", "textbox"],
    outputs=gr.JSON(),
    title="Census Demographic Profile",
    description="Fetches demographic profile data from the U.S. Census Bureau API for the year 2020.",
)


# demo = gr.Interface(
#     fn=fips_translation_2020,
#     inputs=[
#         gr.Textbox(label="Geography Hierarchy (e.g. 'state', 'county')"),
#         gr.Textbox(
#             label="Geographic Name (e.g. 'California', 'Los Angeles County, California')"
#         ),
#         gr.Dataframe(
#             headers=["Parent Geography", "FIPS Code"],
#             datatype=["str", "number"],
#             row_count=(0, "dynamic"),
#             col_count=(2, "fixed"),
#             label="Optional: Parent Geographies (add rows as needed)",
#         ),
#     ],
#     outputs=gr.JSON(),
#     title="Census Demographic Profile",
#     description="Fetches demographic profile data from the U.S. Census Bureau API for the year 2020.",
# )


if __name__ == "__main__":
    demo.launch(mcp_server=True)
