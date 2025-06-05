import os

import gradio as gr
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

try:
    mcp_client = MCPClient(
        {"url": "http://localhost:7860/gradio_api/mcp/sse", "transport": "sse"}
    )
    tools = mcp_client.get_tools()

    # model = InferenceClientModel(token=os.getenv("HUGGINGFACE_API_TOKEN"))
    # TODO: we need to replace with with a Modal hosted model
    model = OpenAIServerModel(
        model_id="gemini-2.0-flash",
        api_key=os.environ.get("GEMINI_API_KEY"),
        # Google Gemini OpenAI-compatible API base URL
        api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    agent = ToolCallingAgent(tools=[*tools], model=model, planning_interval=4)

    task = """
    If you are unsure about what the user is asking for, ask clarifying questions like what state they are looking.
    When searching for FIPS zip codes, take the first five digits of the zip code and prepend ZCTA5. That becomes your “zip code tabulation area” name
    When providing your final answer to the user, clearly explain step-by-step how you arrived at your answer.
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
