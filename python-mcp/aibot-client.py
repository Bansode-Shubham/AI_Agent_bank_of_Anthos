import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import json

from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

# Configure OpenAI API
client = OpenAI(
    base_url="https://kodekey.ai.kodekloud.com/v1",  # adjust if needed
    api_key=os.getenv("OPENAI_API_KEY"),
)
BANK_SERVER_URL = "https://reimagined-space-train-x757667p7p63p645-8888.app.github.dev/sse"

# tools_result = await session.list_tools()
# tools_text = "Available tools:\n"
# for tool in tools_result.tools:
#     tools_text += f"- {tool.name}: {tool.description}\n"
#     if tool.inputSchema and "properties" in tool.inputSchema:
#         tools_text += "  arguments:\n"
#         for arg, details in tool.inputSchema["properties"].items():
#             arg_type = details.get("type", "unknown")
#             tools_text += f"    - {arg} ({arg_type})\n"



# SYSTEM_PROMPT = f"""
# You are a banking assistant. You can call tools via MCP.
# Here are the available tools and their arguments:

# {tools_text}

# Rules:
# 1. Only call a tool if the user explicitly asks for a banking action.
# 2. If the user says something like "hi", "hello", or asks a general question, respond normally without calling any tools.
# 3. If calling a tool, respond **only in JSON**:
# 4. If not calling a tool, respond in plain text.
# """

async def interactive_chat():
    async with sse_client(BANK_SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tools_text = "Available tools:\n"
            for tool in tools_result.tools:
                tools_text += f"- {tool.name}: {tool.description}\n"
                if tool.inputSchema and "properties" in tool.inputSchema:
                    tools_text += "  arguments:\n"
                    for arg, details in tool.inputSchema["properties"].items():
                        arg_type = details.get("type", "unknown")
                        tools_text += f"    - {arg} ({arg_type})\n"
         
            print(tools_text)
            SYSTEM_PROMPT = f"""
            You are a banking assistant. You can call tools via MCP.
            Here are the available tools and their arguments:

            {tools_text}

            Rules:
            1. Only call a tool if the user explicitly asks for a banking action.
            2. If the user says something like "hi", "hello", or asks a general question, respond normally in plain text.
            3. If calling a tool, respond **only in JSON** with the following schema:

                {{
                    "tool": "tool_name",
                    "arguments": {{
                        "arg1": "value1",
                        "arg2": "value2"
                    }}
                }}
            """
            print(SYSTEM_PROMPT)
            print("Bank Chatbot 🤖 (type 'exit' to quit)")
            chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

            while True:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    break
                chat_history.append({"role": "user", "content": user_input})
                # Step 1: Ask LLM how to handle input
                resp = client.chat.completions.create(
                    model="openai/gpt-4.1-mini",
                    messages=chat_history
                )

                llm_text = resp.choices[0].message.content
                print("LLM raw:", llm_text)

                try:
                    tool_call = json.loads(llm_text)
                    tool_name = tool_call.get("tool")
                    arguments = tool_call.get("arguments", {})
                except json.JSONDecodeError:
                    # Not JSON → treat as normal chat response
                    print("Bot:", llm_text)
                    chat_history.append({"role": "assistant", "content": llm_text})
                    continue

                if tool_name:
                    result = await session.call_tool(tool_name, arguments)
                    print(result)
                    print("Bot:", result.content[0].text)
                    chat_history.append({"role": "assistant", "content": result.content[0].text})

                else:
                    print("Bot:", llm_text)
                    chat_history.append({"role": "assistant", "content": llm_text})


if __name__ == "__main__":
    asyncio.run(interactive_chat())


# print("Bank Chatbot 🤖 (type 'exit' to quit)")

# chat_history = [
#     {
#         "role": "system",
#         "content": (
#             "You are a helpful assistant for a dummy bank. "
#             "You have access to MCP tools via the Bank Server. "
#             "Always use the provided MCP tools (login, get_balance, send_payment) "
#             "instead of guessing or role-playing banking steps."
#         ),
#     }
# ]

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         break

#     chat_history.append({"role": "user", "content": user_input})

#     response = client.chat.completions.create(
#         model="openai/gpt-4.1-mini",
#         messages=chat_history,
#         # 👇 This is where MCP is really enabled
#         extra_headers={
#             "anthropic-beta": "mcp",  # tells the API to use MCP
#             "mcp-server": "https://reimagined-space-train-x757667p7p63p645-8888.app.github.dev/sse",
#         },
#     )

#     bot_message = response.choices[0].message.content
#     print("Bot:", bot_message)
#     chat_history.append({"role": "assistant", "content": bot_message})
