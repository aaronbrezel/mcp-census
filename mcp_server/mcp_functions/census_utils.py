from typing import List

from langchain_core.documents import Document
from vector_databases.census_dhc_dp_techdoc import census_dhc_dp_techdoc

from mcp_functions.utils import find_required_parent_geographies


def required_geograpy_hierarchy_parents(geography_hierarchy: str) -> List[str | None]:
    """
    Given the intent to look up a geography hierarchy within from U.S. Census Bureau 2020 decennial census demographic profile API,
    return the parent geographies that must be included

    Args:
        geography_hierarchy (str): The geographic level to query (e.g. 'region', 'state', 'county', 'principal city (or part)', etc.).
    Returns:
        List[str]: List of strings representing the required parent geographies.
    """

    return find_required_parent_geographies(geography_hierarchy)


def decennial_2020_dhc_semantic_search(
    query: str,
) -> List[Document]:
    """
    Perform a semantic search on the 2020 Census Demographic and Housing Characteristics File (DHC) housed at https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf

    Args:
        query (str): The semantic query to perform.
    Returns:
        (List[Document]): The semantically related documents
    """
    docs = census_dhc_dp_techdoc.vector_store.similarity_search(query, k=4)

    return docs
