import asyncio
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient


# ============================================================
# MCP SERVER CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MCP_SERVER_FILE = os.path.join(
    BASE_DIR,
    "mcp_server",
    "loan_policy_server.py",
)

# Launch the server with the same interpreter as the app, so it
# works on Windows, macOS, Linux and inside any virtual environment.
# MCP_PYTHON can override it (e.g. a dedicated MCP environment).
MCP_PYTHON = os.getenv("MCP_PYTHON", sys.executable)

POLICY_TOOLS = {
    "get_car_loan_ltv",
    "get_car_loan_tenure",
    "get_eligible_car_vehicles",
    "search_loan_policy",
}


# ============================================================
# MCP CLIENT
# ============================================================

client = MultiServerMCPClient(
    {
        "loan_policy": {
            "transport": "stdio",
            "command": MCP_PYTHON,
            # Launch the Python file directly (not "-m mcp run").
            "args": [
                MCP_SERVER_FILE,
            ],
        }
    }
)


# ============================================================
# TOOLS
# ============================================================

async def get_loan_policy_tools():
    """
    Load all tools exposed by the Loan Policy MCP Server.
    """

    return await client.get_tools()


async def call_policy_tool(
    tool_name: str,
    question: str = "",
):
    """
    Call one Loan Policy MCP tool by name.
    """

    if tool_name not in POLICY_TOOLS:
        raise ValueError(f"Unknown MCP policy tool '{tool_name}'.")

    tools = await get_loan_policy_tools()

    tool = next(
        (tool for tool in tools if tool.name == tool_name),
        None,
    )

    if tool is None:
        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found."
        )

    arguments = (
        {"question": question}
        if tool_name == "search_loan_policy"
        else {}
    )

    return await tool.ainvoke(arguments)


def call_policy_tool_sync(
    tool_name: str,
    question: str = "",
):
    """
    Synchronous wrapper for Streamlit (which has no running loop).
    """

    return asyncio.run(
        call_policy_tool(tool_name, question)
    )
