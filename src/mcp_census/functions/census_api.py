import os
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv

from ..vector_dbs.datasets_db import search_census_datasets

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
    Semantic fetch list of available Census datasets based on a query string.

    Optionally include filters for year, dataset, and API base URL.

    Leverages a Semantically searchable vector database of Census datasets based on
    the data available at https://api.census.gov/data.html

    Args:
        query (str): Query string to search datasets.
        year (str): Optional year filter.
        dataset (str): Optional dataset identifier filter.
        api_base_url (str): Optional API base URL filter.

    Returns:
        List[str]: A dictionary containing dataset metadata for the specified year.
    """

    return search_census_datasets(
        query,
        vintage=int(year) if year else None,
        key=dataset,
        api_base_url=api_base_url,
    )


async def fetch_dataset_geographies(year: str, dataset: str) -> dict:
    """
    Fetches information on available geographies for a specific Census dataset.

    Wraps the Census API call https://api.census.gov/data/{year}/{dataset}/geography.html

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.

    Returns:
        str: Dataset geography information in dict format.
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}/geography.json"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def fetch_dataset_variables(year: str, dataset: str) -> dict:
    """
    Fetches information on available variables for a specific Census dataset.

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}/variables.html

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.

    Returns:
        str: Dataset variable information in dict format.
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}/variables.json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def fetch_dataset_examples(year: str, dataset: str) -> dict:
    """
    Fetches example API calls for a specific Census dataset.

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}/examples.html

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.

    Returns:
        dict: Dataset example API calls in dict format.
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
    Fetches required parent geographies for a specific geography within a specific Census dataset

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}/geography.html

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.
        geography_name (str): The name of the geography.

    Returns:
        list | None: required parent geographies for specific geography.
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
    Fetches all available FIPS codes for a given geography within a specific Census dataset.

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}?get=NAME&for={geography}:*&in={required_parent_geographies}&key={API_KEY}

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.
        geography (str): The geography of interest.
        required_parent_geographies (Dict[str, str]): Optional dict of required geographies and their FIPS codes necessary for the request. E.g.: {"state": "05,06", "county": "001"}
    Returns:
        dict: A dictionary containing all FIPS codes for the specified geography.

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
    required_parent_geographies: Dict[str, str] | None = None,
) -> Dict[str, str]:
    """
    Fetches the FIPS codes corresponding to a given geography name within a specific Census dataset.

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}?get=NAME&for={geography}:*&in={required_parent_geographies}&key={API_KEY}
    Then, searches the response for the specified name.

    Args:
        name (str): The lookup value for the geography, e.g., a specific state or county name.
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.
        geography (str): The geography of interest.
        required_parent_geographies (Dict[str, str] | None): Optional dict of required parent geographies and their FIPS codes necessary for the request. E.g.: {"state": "05,06", "county": "001"}
    Returns:
        Dict[str, str]: A dictionary containing the FIPS codes for the specified lookup.

    """
    resp = await fetch_dataset_fips(
        year=year,
        dataset=dataset,
        geography=geography,
        required_parent_geographies=required_parent_geographies,
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
    geographies: Dict[str, str],
    required_parent_geographies: Dict[str, str] | None = None,
):
    """
    Fetches data from a specific Census dataset for given variables and geographies.

    Wraps the Census API endpoint https://api.census.gov/data/{year}/{dataset}?get={variables}&for={geography}:*&in={required_parent_geographies}&key={API_KEY}

    Args:
        year (str): The year of the dataset.
        dataset (str): The dataset identifier.
        variables (list[str]): List of variables to fetch.
        geographies (Dict[str, str]): Dictionary of geographies and their FIPS codes.  E.g.: {"state": "05,06", "county": "001"}
        required_parent_geographies (Dict[str, str] | None): Optional dict of required parent geographies and their FIPS codes necessary for the request. E.g.: {"state": "05,06", "county": "001"}
    """
    url: str = f"https://api.census.gov/data/{year}/{dataset}"

    params = {"get": variables, "key": API_KEY}
    params["for"] = [f"{geo}:{fips}" for geo, fips in geographies.items()]
    if required_parent_geographies:
        params["in"] = [
            f"{geo}:{fips}" for geo, fips in required_parent_geographies.items()
        ]

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
