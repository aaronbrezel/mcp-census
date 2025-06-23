---
title: 🏘️ Mcp Census
emoji: 🏘️
colorFrom: yellow
colorTo: indigo
sdk: gradio
sdk_version: 5.33.0
python_version: 3.13
app_file: gradio_app.py
pinned: false
short_description: MCP server leveraging U.S. Census Bureau tooling
---

# mcp-census

A work-in-progress MCP server leveraging U.S. Census Bureau tooling for LLM interoperability.

A deployed interactive version of the mcp server is available at [https://abrezey-mcp-census.hf.space/](https://abrezey-mcp-census.hf.space/). A deployed census MCP server is available at [https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse](https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse). Pushes to the `main` branch of this repo will trigger a redeployment of these resources via GitHub Actions.

This repo was built for the [Gradio/Hugging Face Agents MCP Hackathon](https://huggingface.co/Agents-MCP-Hackathon).

## Example usage

Right now, we recommend using `mcp-census` in conjunction with a MCP Client like Claude Desktop or Cursor. If you prefer to run your own client application, check out [Local Agent Quickstart](#local-agent-quickstart).

**What is the population of Hennepin County, MN for those who are 65 and older?**

https://github.com/user-attachments/assets/c979b9aa-8299-4eec-ad32-362d28ced5e4

**What is the racial/ethnic breakdown of Yolo County?**

https://github.com/user-attachments/assets/d7c34ecb-4503-4bde-a7eb-b865a6f076c8

**Lookup data from the US 2020 Decennial Census and provide a CSV containing data about the number of housing units, total population, and median age for all counties in New York State. For the column containing the county identifier, please provide a complete FIPS containing the state and county as a joined value.**

https://github.com/user-attachments/assets/cffd80f0-0830-4534-ab1a-9574608967ad

## Local MCP server quickstart

We suggest using [`uv`](https://docs.astral.sh/uv/) to manage dependencies, but you can install the required packages directly from the [`pyproject.toml` file](pyproject.toml)

Linting and formatting provided by [`ruff`](https://docs.astral.sh/ruff/) and [`pre-commit`](https://pre-commit.com/)
```zsh
uv run pre-commit install
```

## API Key

```zsh
cp .env.example .env
```

Then fill out your API keys

To request a census API key, visit https://api.census.gov/data/key_signup.html
To request a Hugging Face token, visit https://huggingface.co/docs/hub/security-tokens

The MCP server does not require a Hugging Face token, though it becomes useful during agent development.

### Gradio MCP server

```zsh
uv run --group gradio-deployment python gradio_app.py
```

Assuming you have no other Gradio applications running, this will serve your MCP server at http://localhost:7860/gradio_api/mcp/sse

To update dependencies for the Gradio deployment

```zsh
uv export --group gradio-deployment > requirements.txt
```

### Fast MCP server

In dev mode

```zsh
uv run mcp dev server.py
```

To install in your local Claude Desktop app

```zsh
uv run mcp install server.py --with-editable .
```

`--with-editable .` ensures that the server gets installed with the dependencies defined in `pyproject.toml`. Subject to change as [work continues](https://github.com/aaronbrezel/mcp-census/pull/8) on the package structure of `mcp-census`.

## Local Agent Quickstart

You need to start all three applications (MCP server, Agent, Phoenix) for the system to work at the moment.

### Agent (and MCP client)

```zsh
uv run --group agent python agent.py
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
