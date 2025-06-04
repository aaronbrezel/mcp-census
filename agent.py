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
    agent = ToolCallingAgent(tools=[*tools], model=model)

    demo = gr.ChatInterface(
        fn=lambda message, history: str(agent.run(message)),
        type="messages",
        examples=[
            "FIPS code for California",
            "What is the population of New York City?",
        ],
        title="Agent with MCP Tools",
        description="This is a simple agent that uses MCP tools to answer questions.",
    )

    demo.launch()
finally:
    mcp_client.disconnect()
