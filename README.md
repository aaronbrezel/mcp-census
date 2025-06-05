# mcp-census
Proof of concept for an MCP Server delivering Census Bureau 2020 decennial data for AI Agent interoperability


##  API Key

```txt
CENSUS_API_KEY=<your key here>
GEMINI_API_KEY=<your key here>
```

To request a census API key, visit https://api.census.gov/data/key_signup.html
To request a gemini API key, visit https://ai.google.dev/gemini-api/docs/api-key

## Run the MCP server

```zsh
uv run python mcp_server/app.py
```

## Run the agent

```zsh
uv run python app.py
```
