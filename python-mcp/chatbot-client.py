import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

BANK_SERVER_URL = "http://localhost:8888/sse"
# print(httpx.get(BANK_SERVER_URL))

async def interactive_chat():
    async with sse_client(BANK_SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("Bank Chatbot 🤖 (type 'exit' to quit)")

            while True:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    break

                if "login" in user_input:
                    result = await session.call_tool(
                        "login",
                        arguments={"username": "testuser", "password": "bankofanthos"}
                    )
                    print("Bot:", result.content[0].text)

                elif "balance" in user_input:
                    result = await session.call_tool("get_balance", arguments={})
                    print("Bot:", result.content[0].text)

                else:
                    print("Bot: Sorry, I don’t understand. Try 'login' or 'balance'.")

if __name__ == "__main__":
    asyncio.run(interactive_chat())
