import os

import gradio as gr
from dotenv import load_dotenv
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from phoenix.otel import register
from smolagents import InferenceClientModel, MCPClient, ToolCallingAgent

load_dotenv()

register()
SmolagentsInstrumentor().instrument()


mcp_client = MCPClient(
    # To connect to a local mcp server
    # {"url": "http://localhost:7860/gradio_api/mcp/sse", "transport": "sse"},
    # To connect to a remote mcp server
    {
        "url": "https://abrezey-mcp-census.hf.space/gradio_api/mcp/sse",
        "transport": "sse",
    },
)
mcp_tools = mcp_client.get_tools()


task = """
    If you are unsure about what the user is asking for, ask clarifying questions like what state they are looking.
    When searching for FIPS zip codes, take the first five digits of the zip code and prepend ZCTA5. That becomes your “zip code tabulation area” name
    When providing your final answer to the user, clearly explain step-by-step how you arrived at your answer as a bulleted list.
    Include any documentation links you have access to.
    Suggest follow up questions as well.
    """


def agent_chat(message, history, hf_token_state, hf_inference_model_id_state):
    # Use the provided token, fallback to environment variable if missing
    hf_token = hf_token_state if hf_token_state else os.getenv("HF_TOKEN")

    model = InferenceClientModel(
        model_id=hf_inference_model_id_state,
        token=hf_token,
    )

    agent = ToolCallingAgent(tools=[*mcp_tools], model=model, planning_interval=4)
    agent.prompt_templates["system_prompt"] += task

    return str(agent.run(message))


def agent_tab():
    with gr.Blocks():
        gr.Markdown("## Census Agent: Ask Questions about the 2020 Decennial Census")
        gr.Markdown(
            "Use this agent to explore census documentation, data FIPS codes. Provide a token if needed."
        )
        with gr.Row():
            with gr.Column(scale=1):
                hf_token_input = gr.Textbox(
                    label="🔑 Hugging Face API Token",
                    placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxx",
                    type="password",
                    info="Get your token from https://huggingface.co/settings/tokens",
                )

                hf_model_input = gr.Textbox(
                    label="🤖 Hugging Face Model",
                    placeholder="Qwen/Qwen2.5-32B-Instruct",
                    value="Qwen/Qwen2.5-32B-Instruct",
                    info="Recommended: Qwen/Qwen2.5-32B-Instruct",
                )

                # Hidden state values
                hf_token_state = gr.State(value=None)
                hf_model_state = gr.State(value=hf_model_input.value)

                # Button to confirm and update state
                confirm_button = gr.Button("✅ Confirm Settings")

                # Status message for user feedback
                status_message = gr.Markdown("", visible=False)

                # Update states on click with feedback
                def update_settings(token, model):
                    if not model.strip():
                        return (
                            "",
                            "Qwen/Qwen2.5-32B-Instruct",
                            gr.Markdown(
                                "❌ **Error:** Model name cannot be empty!",
                                visible=True,
                            ),
                        )

                    token_status = (
                        "✅ Token provided"
                        if token.strip()
                        else "⚠️ Using environment token"
                    )
                    return (
                        token,
                        model,
                        gr.Markdown(
                            f"✅ **Settings confirmed!**\n- Model: `{model}`\n- {token_status}",
                            visible=True,
                        ),
                    )

                confirm_button.click(
                    update_settings,
                    inputs=[hf_token_input, hf_model_input],
                    outputs=[hf_token_state, hf_model_state, status_message],
                )

                # Update states on click
                confirm_button.click(
                    lambda token, model: (token, model),
                    inputs=[hf_token_input, hf_model_input],
                    outputs=[hf_token_state, hf_model_state],
                )

            with gr.Column(scale=2):
                gr.ChatInterface(
                    fn=agent_chat,
                    additional_inputs=[hf_token_state, hf_model_state],
                    type="messages",
                    examples=[
                        ["What can you do?"],
                        ["Tell me about the decennial census"],
                        ["FIPS code for California"],
                        ["Over 65 population for Los Angeles County"],
                        ["FIPS code for 11050"],
                        ["What locations can I look up for the decenial census"],
                    ],
                    title="AI Agent with U.S. Census Bureau MCP Tools",
                    description="This is a simple agent that uses MCP tools to answer questions about the 2020 decennial Census.",
                )


with gr.Blocks(title="Census MCP Server Demo") as demo:
    with gr.Tab("🏘️ Decennial census agent"):
        agent_tab()

    # TODO: For ease of use, we could try to combine the mcp server and agent as part of the same gradio demo
    # with gr.Tab("🔬 Decennial census MCP server"):
    #     mcp_sever_tab()

if __name__ == "__main__":
    demo.launch()
