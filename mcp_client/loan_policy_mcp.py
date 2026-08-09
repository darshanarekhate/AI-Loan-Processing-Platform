import os

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


# ============================================================
# MCP ENVIRONMENT PYTHON
# ============================================================

MCP_PYTHON = os.path.join(
    BASE_DIR,
    "mcp_env",
    "Scripts",
    "python.exe",
)


# ============================================================
# MCP CLIENT
# ============================================================

client = MultiServerMCPClient(
    {
        "loan_policy": {
            "transport": "stdio",

            # Launch the MCP server directly using
            # the Python executable from mcp_env.
            "command": MCP_PYTHON,

            # IMPORTANT:
            # Do NOT use "-m mcp run" here.
            # LangChain stdio should launch the Python file directly.
            "args": [
                MCP_SERVER_FILE,
            ],
        }
    }
)


# ============================================================
# LOAD MCP TOOLS
# ============================================================

async def get_loan_policy_tools():
    """
    Load all tools exposed by the Loan Policy MCP Server.
    """

    tools = await client.get_tools()

    return tools


# ============================================================
# FIND MCP TOOL
# ============================================================

async def get_loan_policy_tool(
    tool_name: str,
):
    """
    Return a specific tool from the Loan Policy MCP Server.
    """

    tools = await get_loan_policy_tools()

    for tool in tools:

        if tool.name == tool_name:
            return tool

    raise RuntimeError(
        f"MCP tool '{tool_name}' was not found."
    )


# ============================================================
# CAR LOAN LTV
# ============================================================

async def get_car_loan_ltv():
    """
    Retrieve maximum car-loan LTV through MCP.
    """

    tool = await get_loan_policy_tool(
        "get_car_loan_ltv"
    )

    return await tool.ainvoke({})


# ============================================================
# CAR LOAN TENURE
# ============================================================

async def get_car_loan_tenure():
    """
    Retrieve car-loan tenure through MCP.
    """

    tool = await get_loan_policy_tool(
        "get_car_loan_tenure"
    )

    return await tool.ainvoke({})


# ============================================================
# ELIGIBLE VEHICLES
# ============================================================

async def get_eligible_car_vehicles():
    """
    Retrieve eligible car vehicles through MCP.
    """

    tool = await get_loan_policy_tool(
        "get_eligible_car_vehicles"
    )

    return await tool.ainvoke({})


# ============================================================
# POLICY SEARCH
# ============================================================

async def search_loan_policy(
    question: str,
):
    """
    Search the loan policy knowledge base through MCP.
    """

    tool = await get_loan_policy_tool(
        "search_loan_policy"
    )

    return await tool.ainvoke(
        {
            "question": question
        }
    )

# ============================================================
# SYNCHRONOUS MCP WRAPPERS
# ============================================================

import asyncio


def get_car_loan_ltv_sync():
    return asyncio.run(
        get_car_loan_ltv()
    )


def get_car_loan_tenure_sync():
    return asyncio.run(
        get_car_loan_tenure()
    )


def get_eligible_car_vehicles_sync():
    return asyncio.run(
        get_eligible_car_vehicles()
    )


def search_loan_policy_sync(
    question: str,
):
    return asyncio.run(
        search_loan_policy(question)
    )