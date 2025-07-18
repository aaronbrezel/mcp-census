import os
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv

from ..vector_dbs.datasets_db import search_census_datasets
from ..vector_dbs.quick_search import Document, quick_faiss_search

load_dotenv()  # Loads variables from a .env file into os.environ
API_KEY: str | None = os.getenv("CENSUS_API_KEY", None)
if not API_KEY:
    # If no API key is found, immediately raise an error to stop execution
    raise ValueError("Set a CENSUS_API_KEY environment variable")


async def fetch_datasets(
    query: str,
    year: Optional[str] = None,
    dataset: Optional[str] = None,
    api_base_url: Optional[str] = None,
) -> List[str]:
    """
    Search for relevant Census datasets using semantic search.

    Use this tool first to discover datasets that match your data needs.
    The search uses AI to understand your query and find relevant datasets.

    Args:
        query (str): Describe what data you're looking for (e.g., "population by age", "housing costs", "employment statistics")
        year (str, optional): Filter by specific year (e.g., "2020", "2021")
        dataset (str, optional): Filter by dataset identifier (e.g., "acs1", "dec/pl")
        api_base_url (str, optional): Filter by API base URL

    Returns:
        List[str]: List of relevant dataset metadata including titles, descriptions, and identifiers.

    Example:
        To find population data: query="population demographics by age and race", year="2021"
    """

    return search_census_datasets(
        query,
        vintage=int(year) if year else None,
        key=dataset,
        api_base_url=api_base_url,
    )


async def fetch_dataset_geographies(year: str, dataset: str) -> dict:
    """
    Get available geographic levels for a dataset (state, county, tract, etc.).

    Use this after selecting a dataset to understand what geographic breakdowns are available.
    This helps you determine the appropriate geography for your data request.

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier from fetch_datasets (e.g., "acs/acs1")

    Returns:
        dict: Geographic levels available including required parent geographies.

    Example:
        For ACS data: year="2021", dataset="acs/acs1"
        Returns info about state, county, tract, block group availability
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}/geography.json"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def fetch_dataset_variables(
    year: str, dataset: str, query: Optional[str] = None
) -> dict:
    """
    Get available data variables for a dataset with optional semantic filtering.

    Use this to discover what specific data points are available in your chosen dataset.
    The query parameter helps narrow down thousands of variables to relevant ones.

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier from fetch_datasets (e.g., "acs/acs1")
        query (str, optional): Semantic search to filter variables (e.g., "median income", "poverty rate")

    Returns:
        dict: Variable definitions with codes, labels, and concepts.

    Example:
        To find income variables: year="2021", dataset="acs/acs1", query="household income median"
        Returns variables like B19013_001E (median household income)
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}/variables.json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        if query:
            response = resp.json()
            variables: List[Document] = [
                Document(
                    page_content=f"Variable: {variable_name}\nDetails: {response['variables'][variable_name]}",
                    metadata={variable_name: response["variables"][variable_name]},
                )
                for variable_name in response["variables"]
            ]
            search_results = quick_faiss_search(variables, query)
            # Reformat back into Census API-style response dict
            return {
                "variables": {
                    k: v for doc in search_results for k, v in doc.metadata.items()
                }
            }
        return resp.json()


async def fetch_dataset_examples(year: str, dataset: str) -> dict:
    """
    Get example API calls for a dataset to understand proper usage patterns.

    Use this when you're unsure how to structure your data request.
    Provides real examples of working API calls with proper parameter formats.

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier (e.g., "acs/acs1")

    Returns:
        dict: Example API calls with explanations and expected responses.

    Example:
        For ACS examples: year="2021", dataset="acs/acs1"
        Returns various example calls showing proper variable and geography usage
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}/examples.json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def fetch_dataset_required_parent_geographies(
    year: str, dataset: str, geography_name: str
) -> list:
    """
    Get required parent geographies for a specific geographic level.

    Use this to understand what parent geographies are needed when requesting
    data for a specific geographic level (e.g., tracts require county and state).

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier (e.g., "acs/acs1")
        geography_name (str): Geographic level name (e.g., "tract", "block group")

    Returns:
        list: Required parent geography levels that must be specified.

    Example:
        For tract data: geography_name="tract"
        Returns: ["state", "county"] indicating you need both state and county FIPS
    """

    url: str = f"https://api.census.gov/data/{year}/{dataset}/geography.json"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        geographies = resp.json()
        for geography in geographies["fips"]:
            if geography["name"] == geography_name:
                return geography.get("requires", [])

    return []


async def fetch_dataset_fips(
    year: str,
    dataset: str,
    geography: str,
    required_parent_geographies: Dict[str, str] | None = None,
) -> dict:
    """
    Get all available FIPS codes for a geographic level within a dataset.

    Use this to discover what geographic areas are available at a specific level.
    Helpful for exploring available counties, tracts, etc.

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier (e.g., "acs/acs1")
        geography (str): Geographic level (e.g., "county", "tract", "state")
        required_parent_geographies (Dict[str, str], optional): Parent geography constraints
            Format: {"parent_type": "fips_codes"}
            Example: {"state": "06"} to get counties only in California

    Returns:
        list: All available FIPS codes and names for the specified geography.

    Example:
        Get all counties in California:
        geography="county", required_parent_geographies={"state": "06"}
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}"
    variables = ["NAME"]
    for_clause = [f"{geography}:*"]
    params = {"get": variables, "for": for_clause, "key": API_KEY}
    if required_parent_geographies:
        params["in"] = [
            f"{geography}:{fips_code}"
            for geography, fips_code in required_parent_geographies.items()
        ]

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


async def lookup_dataset_fips(
    name: str,
    year: str,
    dataset: str,
    geography: str,
    parent_geographies: Dict[str, str] | None = None,
) -> Dict[str, str]:
    """
    Convert a place name to its FIPS code for use in data requests.

    Use this when you have a place name (like "Los Angeles County") and need
    the corresponding FIPS code for data requests.

    Args:
        name (str): Exact place name to look up (e.g., "Los Angeles County", "California")
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier (e.g., "acs/acs1")
        geography (str): Geographic level to search (e.g., "county", "state")
        parent_geographies (Dict[str, str], optional): Parent geography constraints
            Format: {"parent_type": "fips_codes"}
            Example: {"state": "06"} when looking up counties in California

    Returns:
        Dict[str, str]: FIPS codes for the named geography.

    Example:
        Find FIPS for Los Angeles County:
        name="Los Angeles County, California", geography="county", parent_geographies={"state": "06"}
    """
    resp = await fetch_dataset_fips(
        year=year,
        dataset=dataset,
        geography=geography,
        required_parent_geographies=parent_geographies,
    )

    header, *rows = resp
    lookup_dict = {
        row[0]: {col: row[idx] for idx, col in enumerate(header) if idx != 0}
        for row in rows
    }
    # TODO: It'd be really great if we could leverage Elicitation to perform some fuzzy matching on name lookups
    lookup_value = lookup_dict[name]
    return lookup_value


async def fetch_dataset_data(
    year: str,
    dataset: str,
    variables: list[str],
    target_geographies: Dict[str, str],
    parent_geographies: Dict[str, str] | None = None,
):
    """
    Fetch actual Census data for specific variables and geographic areas.

    This is the final step - use after identifying variables and geographies from other tools.
    Returns the actual data values you requested.

    Args:
        year (str): Dataset year (e.g., "2021")
        dataset (str): Dataset identifier (e.g., "acs/acs1")
        variables (list[str]): Variable codes to fetch (e.g., ["B19013_001E", "NAME"])
        target_geographies (Dict[str, str]): Geographic areas to get data for
            Format: {"geography_type": "fips_codes"}
            Examples:
            - {"state": "*"} for all states
            - {"county": "001,002"} for specific counties
            - {"tract": "*"} for all tracts
        parent_geographies (Dict[str, str], optional): Required parent geography constraints
            Format: {"parent_type": "fips_codes"}
            Examples:
            - {"state": "06"} when requesting counties in California
            - {"state": "06", "county": "001"} when requesting tracts in a specific county

    Returns:
        list: Census API response with data rows and headers.

    Example:
        Get median income for all counties in California:
        target_geographies={"county": "*"}, parent_geographies={"state": "06"}
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}"

    params = {"get": variables, "key": API_KEY}
    params["for"] = [f"{geo}:{fips}" for geo, fips in target_geographies.items()]
    if parent_geographies:
        params["in"] = [f"{geo}:{fips}" for geo, fips in parent_geographies.items()]

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
