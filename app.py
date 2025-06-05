import ast
import os
from collections import defaultdict

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
    # required_parent_geographies: pd.DataFrame, # required_parent_geographies (pd.DataFrame): A Dataframe representing required parent geographies and their FIPS codes.
    required_parent_geographies: str | None = None,
) -> dict:
    """
    Fetches FIPS code for a given geography hierarchy and name.

    Args:
        geography_hierarchy (str): The geographic level to query (e.g. 'region', 'state', 'county', etc.).
        name (str): The name of the geographic entity (e.g., 'California', 'Los Angeles County, California').
        required_parent_geographies (str | None): A string representing required parent geographies and their FIPS codes in the format [(<geography hierarchy>, <FIPS code>)]
    Returns:
        Dict[str, str]: dictionary representing FIPS code values for provided geography_hierarchy.
    """

    BASE_URL = "https://api.census.gov/data/2020/dec/dp"

    variables = ["NAME"]
    for_clause = f"{geography_hierarchy}:*"
    params = {"get": variables, "for": for_clause, "key": API_KEY}

    # if required_parent_geographies.size != 0:
    #     in_geo = (
    #         required_parent_geographies.groupby("Geography")["FIPS Code"]
    #         .apply(list)
    #         .to_dict()
    #     )
    #     in_clause = " ".join(
    #         f"{geo}:{','.join(codes)}" for geo, codes in in_geo.items()
    #     )
    #     params["in"] = in_clause
    if required_parent_geographies:

        # Parse the string into a Python list
        try:
            pairs = ast.literal_eval(required_parent_geographies)
        except SyntaxError as e:
            raise SyntaxError(
                f"{e}. Did you remember to wrap your strings in quotes?"
            ) from e

        # Group values by key
        grouped = defaultdict(list)
        for key, value in pairs:
            grouped[key].append(value)
        # Build the final string
        result = " ".join(f"{key}:{','.join(grouped[key])}" for key in grouped)
        if result != "[]":
            params["in"] = result

    try:
        response = requests.get(BASE_URL, params=params)
        # Store text in case of error
        error_text = response.text
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        if error_text == "error: unknown/unsupported geography hierarchy":
            required_in_clauses = find_required_in_clauses(geography_hierarchy)
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
            f"Ensure the name is correct. Perhaps you input the wrong name or geography_hierarchy?"
            f"Try appending the a state to your name input like so: `name, Arizona`"
        )


def geography_hierarchy_guessing_assistant_2020(query_text: str) -> str:
    """
    A simple assistant that suggests a likely Census 2020 geography hierarchy based on the query text. Follows
    a basic string matching heuristic to determine a likely geographic hierarchy that can be utilized for FIPS translation or other census-related queries.

    Args:
        query_text (str): the text in need of a geography hierarchy guess.
    Returns:
        str: A string representing the guessed geography hierarchy (e.g., 'school district (elementary)', 'state legislative district (lower chamber)', 'zip code tabulation area', etc.). Use this string to query the Census API for FIPS codes or other demographic data.
    """

    if query_text.isdigit() and len(query_text) == 5:
        return "zip code tabulation area"
    elif (
        len(query_text) == 10
        and query_text[:5].isdigit()
        and query_text[5] == "-"
        and query_text[6:].isdigit()
    ):
        return "zip code tabulation area"
    elif "zcta5" in query_text.lower() or "zcta" in query_text.lower():
        return "zip code tabulation area"

    elif "high school" in query_text.lower():
        return "school district (secondary)"
    elif "elementary" in query_text.lower():
        return "school district (elementary)"
    elif (
        "unified district" in query_text.lower()
        or "unified school" in query_text.lower()
    ):
        return "school district (unified)"
    elif "congressional district" in query_text.lower():
        return "congressional district"
    elif "state senate" in query_text.lower():
        return "state legislative district (upper chamber)"
    elif "state house" in query_text.lower():
        return "state legislative district (lower chamber)"

    return "unknown geography hierarchy"


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


demographic_profile_2020_interface = gr.Interface(
    fn=demographic_profile_2020,
    inputs=["textbox", "textbox", "textbox"],
    outputs=gr.JSON(),
    title="Census Demographic Profile",
    description="Fetches demographic profile data from the U.S. Census Bureau API for the year 2020.",
)

fips_translation_2020_interface = gr.Interface(
    fn=fips_translation_2020,
    inputs=[
        gr.Textbox(label="Geography Hierarchy (e.g. 'state', 'county')"),
        gr.Textbox(
            label="Geographic Name (e.g. 'California', 'Los Angeles County, California')"
        ),
        gr.Textbox(
            label="Required Parent Geographies and their FIPS Codes in the format [('<geography hierarchy>', '<FIPS code>')]. E.g. [('state', '06'), ('county', '037')].",
            placeholder="e.g. [('state', '06'), ('county', '037')]",
        ),
        # gr.Dataframe(
        #     headers=["Geography Hierarchy", "FIPS Code"],
        #     datatype=["str", "str"],
        #     row_count=(0, "dynamic"),
        #     col_count=(2, "fixed"),
        #     label="Required Parent Geographies and their FIPS codes",
        # ),
    ],
    outputs=gr.JSON(),
    title="CFIPS Translation 2020",
    description="Fetches FIPS codes from 2020 U.S. Census Bureau API.",
)

geography_hierarchy_guessing_assistant_2020_interface = gr.Interface(
    fn=geography_hierarchy_guessing_assistant_2020,
    inputs=["textbox"],
    outputs=gr.Text(),
    title="Census Geography Hierarchy Guessing Assistant 2020",
    description="Based on query text, suggests a likely Census 2020 geography hierarchy for FIPS translation or other census-related queries.",
)


demo = gr.TabbedInterface(
    [
        demographic_profile_2020_interface,
        fips_translation_2020_interface,
        geography_hierarchy_guessing_assistant_2020_interface,
    ],
    [
        "Demographic Profile 2020",
        "FIPS Translation 2020",
        "Geography Hierarchy Guessing Assistant 2020",
    ],
)


if __name__ == "__main__":
    demo.launch(mcp_server=True)
