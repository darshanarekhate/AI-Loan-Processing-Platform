import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():

    client = MultiServerMCPClient(
        {
            "loan_policy": {
                "command": r"C:\Users\Dell\OneDrive\Documents\Generative AI\genv\Scripts\mcp.exe",
                "args": [
                    "run",
                    "mcp_server/loan_policy_server.py",
                ],
                "transport": "stdio",
            }
        }
    )

    print("\nConnecting to Loan Policy MCP Server...\n")

    tools = await client.get_tools()

    print(f"Found {len(tools)} MCP tools:\n")

    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())