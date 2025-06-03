import os
import gradio as gr
import requests
from dotenv import load_dotenv

load_dotenv()


BASE_URL = "https://api.census.gov/data/2020/dec/dp"


def demographic_profile_2020(
    get_variables: str, for_clause: str, in_clause: str | None = None
):
    """
    Fetches demographic profile data from the U.S. Census Bureau API.

    Args:
        get_variables (str): The Census variables to retreive, comma-separated.
        for_clause (str): The geographic level to query (e.g., 'us:*', 'state:06').
        in_clause (str, optional): Higher-level geography for nested queries (e.g., 'state:06').

    Returns:
        list[dict]: Parsed response with column headers and row data as dictionaries.
    """
    api_key = os.getenv("CENSUS_API_KEY", None)
    if not api_key:
        raise ValueError("API key is required.")

    base_url = "https://api.census.gov/data/2020/dec/dp"

    params = {"get": get_variables, "for": for_clause, "key": api_key}
    if in_clause:
        params["in"] = in_clause

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Convert to list of dicts for easier handling
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]


demo = gr.Interface(
    fn=demographic_profile_2020,
    inputs=["textbox", "textbox", "textbox"],
    outputs=gr.JSON(),
    title="Census Demographic Profile",
    description="Fetches demographic profile data from the U.S. Census Bureau API for the year 2020.",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
