import asyncio
import json
import os

from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI


load_dotenv()

mcp_server_url = os.environ["MCP_SERVER_URL"]
circle_id = os.environ["CIRCLE_ID"]

groq = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)


def build_tool_definitions(tools):
    definitions = []

    for tool in tools:
        definitions.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
        )

    return definitions


async def main():

    async with Client(mcp_server_url) as mcp:

        # Discover tools from the MCP server
        tools = await mcp.list_tools()

        tool_definitions = build_tool_definitions(tools)

        print("=================================")
        print("   Care Circle MCP Assistant")
        print("=================================")
        print(f"Connected to MCP server")
        print(f"Discovered {len(tools)} tools:")
        
        for tool in tools:
            print(f"  - {tool.name}")

        print()
        print("Type 'quit' to exit.")
        print()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful healthcare assistant for the Care Circle app. "
                    "You can use the available MCP tools to access and update care-circle "
                    "information. Always use the appropriate tool when real data is needed. "
                    "Never invent medication, appointment, refill, or care-circle data. "
                    "Keep responses concise and easy to understand."
                ),
            }
        ]

        while True:

            user_input = input("You: ").strip()

            if user_input.lower() in {"quit", "exit"}:
                print("Goodbye!")
                break

            if not user_input:
                continue

            messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            response = groq.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tool_definitions,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # Save the assistant's decision
            messages.append(assistant_message)

            if assistant_message.tool_calls:

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # The circle is fixed for this simulation.
                    if "circle_id" in [
                        property_name
                        for tool in tools
                        if tool.name == tool_name
                        for property_name in tool.inputSchema.get(
                            "properties", {}
                        )
                    ]:
                        arguments["circle_id"] = circle_id

                    print(f"\n🔧 Calling MCP tool: {tool_name}")
                    print(f"📦 Arguments: {arguments}")

                    try:
                        result = await mcp.call_tool(
                            tool_name,
                            arguments,
                        )

                        tool_result = result.data

                        print(f"📡 MCP result: {tool_result}")

                    except Exception as error:
                        tool_result = {
                            "status": "error",
                            "message": str(error),
                        }

                        print(f" MCP error: {error}")

                    # Give the MCP result back to Groq
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        }
                    )

                # Ask Groq to turn the tool result into a human response
                final_response = groq.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                )

                answer = final_response.choices[0].message.content

                messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                print(f"\nAssistant: {answer}\n")

            else:
                # The model answered without needing an MCP tool
                answer = assistant_message.content

                print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())