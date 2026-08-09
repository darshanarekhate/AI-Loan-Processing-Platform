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

    print("Available tools:")

    for tool in tools:
        print(f"- {tool.name}")

    print("\nCalling get_car_loan_ltv...\n")

    ltv_tool = next(
        tool for tool in tools
        if tool.name == "get_car_loan_ltv"
    )

    result = await ltv_tool.ainvoke({})

    print("MCP Tool Response:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())