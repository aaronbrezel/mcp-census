---
title: Mcp Census
emoji: 🏘️
colorFrom: yellow
colorTo: indigo
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
short_description: MCP server leveraging U.S. Census Bureau tooling
---

# mcp-census

MCP server leveraging U.S. Census Bureau tooling for LLM interoperability.

This repo was built for the [Gradio/Hugging Face Agents MCP Hackathon](https://huggingface.co/Agents-MCP-Hackathon). 

This project is a work in progress. A deployed interactive version of the mcp server is available at [https://abrezey-mcp-census.hf.space/](https://abrezey-mcp-census.hf.space/). A deployed census MCP server is available at [https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse](https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse).

## Local MCP server quickstart

We suggest using [`uv`](https://docs.astral.sh/uv/) to manage dependencies, but you can install the required packages directly from the [`pyproject.toml` file](pyproject.toml)

You need to start all three applications (MCP server, Agent, Phoenix) for the system to work at the moment.

## API Key

```zsh
cp .env.example .env
```

Then fill out your API keys

To request a census API key, visit https://api.census.gov/data/key_signup.html
To request a Hugging Face token, visit https://huggingface.co/docs/hub/security-tokens

The MCP server does not require a Hugging Face token, though it becomes useful during agent development.

### MCP server

```zsh
uv run python app.py
```

Assuming you have no other gradio applications running, this will serve your MCP server at http://localhost:7860/gradio_api/mcp/sse

## Local Agent Quickstart

### Agent (and MCP client)

```zsh
uv run python agent.py
```

### Observability

When debugging Agents, observability is key. The agent is currently configured to send logs to a phoenix server.

```zsh
uv run python -m phoenix.server.main serve
```

The agent will not work without this server running. 

## MCP architecture

<img src="assets/mcp-census.png" alt="MCP Census" width="200" height="auto">

## Possible improvements

### Evaluation

* We recommend starting here to provide a strong benchmark with which to evaluate improvements.
* MCP server tools can be evaluated via unit tests. Agentic behavior can be evaluated on criteria described [here](https://hamel.dev/blog/posts/evals/) and emerging frameworks such as [RAGAS](https://docs.ragas.io/en/stable/).

### MCP Client

* Rather than build tool sets for every Census dataset (decennial, american community survey, etc.), it may be more comprensive to build tooling around the [machine readable dataset discovery tool](https://www.census.gov/data/developers/updates/new-discovery-tool.html).
* The Census Bureau publishes myriad documentation. Enabling semantic retrieval via RAG should provide agents with information to better respond to user queries.

### Agent

* Agentic Behavior can be fine tuned via foundation model choice, prompting as well as introduction of additional tooling such as data exporting. The exact optimizations may depend on intended use case.
* Improved citations of census bureau documentation.
