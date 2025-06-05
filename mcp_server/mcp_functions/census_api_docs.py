import requests
from markdownify import markdownify


def import_decennial_2020_datasets_homepage() -> str:
    """
    Fetches the homepage for the the U.S. Census Bureau 2020 decennial census API housed at https://api.census.gov/data/2020/dec/dp.html.
    Contains descriptions of available datasets.
    Also includes links to additional helpful documentation such as available geographies and example API calls.

    Args:

    Returns:
        str: The homepage in markdown format
    """

    response = requests.get("https://api.census.gov/data/2020/dec/dp.html")

    return markdownify(response.text.strip())


def import_decennial_2020_demographic_profile_geographies() -> str:
    """
    Fetches information on available geographies for the the U.S. Census Bureau 2020 decennial census demographic profile API housed at https://api.census.gov/data/2020/dec/dp/geography.html.
    Includes:
        * Geography Levels
        * Geography Hierarchy.

    Args:

    Returns:
        str: The information in markdown format
    """

    response = requests.get("https://api.census.gov/data/2020/dec/dp/geography.html")

    return markdownify(response.text.strip())


def import_decennial_2020_demographic_profile_variables() -> str:
    """
    Fetches information on available variables for the the U.S. Census Bureau 2020 decennial census demographic profile API housed at https://api.census.gov/data/2020/dec/dp/variables.html.
        * "Name" -- used to access variable during API calls
        * "Label" -- description of variable

    Args:

    Returns:
        str: The information in markdown format
    """

    response = requests.get("https://api.census.gov/data/2020/dec/dp/variables.html")

    return markdownify(response.text.strip())
