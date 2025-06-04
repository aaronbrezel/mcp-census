import os

import gradio as gr
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

try:
    mcp_client = MCPClient({"url": "http://localhost:7860/gradio_api/mcp/sse"})
    tools = mcp_client.get_tools()

    # model = InferenceClientModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))
    # TODO: we need to replace with with a Modal hosted model
    model = model = OpenAIServerModel(
        model_id="gemini-2.0-flash",
        api_key=os.environ.get("GEMINI_API_KEY"),
        # Google Gemini OpenAI-compatible API base URL
        api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    agent = ToolCallingAgent(tools=[*tools], model=model, planning_interval=4)

    task = """
    Before searching for school district or congressional district, make sure you know what state the user is looking for. Ask the user if you don’t know. 
    When searching for FIPS zip codes, take the first five digits of the zip code and prepend ZCTA5. That becomes your “zip code tabulation area” name
    If you can’t find a fips code on first pass, you should ask the user for additional information like the state or metropolitan statistical area/micropolitan statistical area they are searching for
    """

    agent.prompt_templates["system_prompt"] = (
        agent.prompt_templates["system_prompt"] + task
    )

    demo = gr.ChatInterface(
        fn=lambda message, history: str(agent.run(message)),
        type="messages",
        examples=[
            "FIPS code for California",
            "FIPS code for 11050",
        ],
        title="Agent with MCP Tools",
        description="This is a simple agent that uses MCP tools to answer questions.",
    )

    demo.launch()
finally:
    mcp_client.disconnect()
