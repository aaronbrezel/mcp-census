import ast
import os
from collections import defaultdict
from typing import List, Tuple

import requests
from dotenv import load_dotenv

from functions.utils import build_fips_lookup, find_required_parent_geographies


def parse_required_parent_geographies_string(data_str: str) -> List[Tuple[str, str]]:
    try:
        result = ast.literal_eval(data_str)

        # Validate structure
        if not isinstance(result, list):
            raise ValueError("Parsed required parent geographies string is not a list.")
        for item in result:
            if not (
                isinstance(item, tuple)
                and len(item) == 2
                and all(isinstance(elem, str) for elem in item)
            ):
                raise ValueError(
                    "Each item in the parse required parent geographies list must be a tuple of two strings."
                )

        return result

    except (SyntaxError, ValueError) as e:
        raise ValueError(
            f"Failed to parse input string into List[Tuple[str, str]]: {e}"
        )


load_dotenv()  # Loads variables from a .env file into os.environ
API_KEY: str | None = os.getenv("CENSUS_API_KEY", None)
if not API_KEY:
    # If no API key is found, immediately raise an error to stop execution
    raise ValueError("Set a CENSUS_API_KEY environment variable")


def dec2020_dp_fips_lookup(
    geography_hierarchy: str,
    name: str,
    required_parent_geographies: str,
):
    """
    Fetches FIPS code for a given geography hierarchy and name. Also returns FIPS code for any parent geographies.

    Args:
        geography_hierarchy (str): The geographic level to query (e.g. 'region', 'state', 'county', etc.).
        name (str): The name of the geographic entity (e.g., 'California', 'Los Angeles County, California').
        required_parent_geographies (str): A string representing required parent geographies and their FIPS codes in the format "[('<geography hierarchy>', '<FIPS code>'), ('<geography hierarchy>', '<FIPS code>')]"
    Returns:
        Dict[str, str]: dictionary representing FIPS code values for provided geography_hierarchy.
    """

    BASE_URL = "https://api.census.gov/data/2020/dec/dp"

    variables = ["NAME"]
    for_clause = f"{geography_hierarchy}:*"
    params = {"get": variables, "for": for_clause, "key": API_KEY}

    ###################
    # Parse parent geographies into API friendly string
    ###################
    parsed_parent_geographies: List[Tuple[str, str]] = (
        parse_required_parent_geographies_string(required_parent_geographies)
    )
    if parsed_parent_geographies:
        # Group values by key
        grouped = defaultdict(list)
        for key, value in parsed_parent_geographies:
            grouped[key].append(value)
        # Build the final string
        result = " ".join(f"{key}:{','.join(grouped[key])}" for key in grouped)
        params["in"] = result

    try:
        response = requests.get(BASE_URL, params=params)
        # Store text in case of error
        error_text = response.text
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        if error_text == "error: unknown/unsupported geography hierarchy":
            # TODO: This error gets raise both if a parent geography is missing AND if the requested
            # geography is invalid. We need to impove this raised error to help parse the difference.
            raise ValueError(
                "Invalid geography hierarchy provided.",
                "Acceptable required_parent_geographies must be provided.",
                f"{geography_hierarchy} requires the following parent geographies: {find_required_parent_geographies(geography_hierarchy)}",
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
            f"Perhaps you input the wrong name or geography_hierarchy?"
            f"Try appending a geography to your name input like so: `name, state`"
        )


def dec2020_dp(get_variables: str, for_clauses: str, in_clauses: str):
    """
    Fetches demographic profile data from the U.S. Census Bureau API.

    Args:
        get_variables (str): The Census variables to retreive, comma-separated (e.g., 'DP1_0001C', 'DP1_0001C,DP1_0003C').
        for_clauses (str): The geographic level to query (e.g., 'us:*', 'state:06', 'state:04,06').
        in_clauses (str): Higher-level geography for nested queries (e.g., 'state:06', 'state:06 county:037,038').

    Returns:
        list[dict]: Parsed response with column headers and row data as dictionaries.
    """
    BASE_URL = "https://api.census.gov/data/2020/dec/dp"

    params = [
        ("get", get_variables),
        ("for", for_clauses),
        ("in", in_clauses),
        ("key", API_KEY),
    ]

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Convert to list of dicts for easier handling
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]
