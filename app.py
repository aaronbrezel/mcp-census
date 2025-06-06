import os

import gradio as gr
from dotenv import load_dotenv
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from phoenix.otel import register
from smolagents import InferenceClientModel, MCPClient, ToolCallingAgent

load_dotenv()

register()
SmolagentsInstrumentor().instrument()

try:
    mcp_client = MCPClient(
        {"url": "http://localhost:7860/gradio_api/mcp/sse", "transport": "sse"}
    )
    tools = mcp_client.get_tools()

    model = InferenceClientModel(
        provider="nebius",
        model_id="Qwen/Qwen2.5-32B-Instruct",
        token=os.getenv("HF_TOKEN"),
    )

    agent = ToolCallingAgent(tools=[*tools], model=model, planning_interval=4)

    task = """
    If you are unsure about what the user is asking for, ask clarifying questions like what state they are looking.
    When searching for FIPS zip codes, take the first five digits of the zip code and prepend ZCTA5. That becomes your “zip code tabulation area” name
    When providing your final answer to the user, clearly explain step-by-step how you arrived at your answer as a bulleted list.
    Include any documentation links you have access to. 
    Suggest follow up questions as well.
    """

    agent.prompt_templates["system_prompt"] = (
        agent.prompt_templates["system_prompt"] + task
    )

    demo = gr.ChatInterface(
        fn=lambda message, history: str(agent.run(message)),
        type="messages",
        examples=[
            "What can you do?",
            "Tell me about the decennial census",
            "FIPS code for California",
            "Over 65 population for Los Angeles County",
            "FIPS code for 11050",
            "What locations can I look up for the decenial census",
        ],
        title="AI Agent with U.S. Census Bureau MCP Tools",
        description="This is a simple agent that uses MCP tools to answer questions about the 2020 decennial Census.",
    )

    demo.launch()
finally:
    mcp_client.disconnect()
