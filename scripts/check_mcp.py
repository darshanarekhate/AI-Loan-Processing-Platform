"""
Manual smoke test for the Loan Policy MCP server.

    python -m scripts.check_mcp

Starts the server over stdio, lists its tools and calls each one.
Requires the full requirements.txt (embedding model + FAISS index).
"""

import asyncio

from mcp_client.loan_policy_mcp import call_policy_tool, get_loan_policy_tools


async def main():
    tools = await get_loan_policy_tools()

    print(f"Connected. {len(tools)} tools:")

    for tool in tools:
        print(f"  - {tool.name}")

    for name, question in [
        ("get_car_loan_ltv", ""),
        ("get_car_loan_tenure", ""),
        ("get_eligible_car_vehicles", ""),
        ("search_loan_policy", "What credit score is required for a car loan?"),
    ]:
        print(f"\n== {name} ==")
        print(await call_policy_tool(name, question))


if __name__ == "__main__":
    asyncio.run(main())
