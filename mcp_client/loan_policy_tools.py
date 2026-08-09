from langchain_core.tools import StructuredTool

from mcp_client.loan_policy_mcp import (
    get_car_loan_ltv,
    get_car_loan_tenure,
    get_eligible_car_vehicles,
    search_loan_policy,
)


# ============================================================
# MCP TOOL WRAPPERS
# ============================================================

async def car_loan_ltv_tool():
    """Get the maximum financing percentage for a car loan."""
    return await get_car_loan_ltv()


async def car_loan_tenure_tool():
    """Get the minimum and maximum tenure available for a car loan."""
    return await get_car_loan_tenure()


async def eligible_car_vehicles_tool():
    """Get the vehicle types eligible for a car loan."""
    return await get_eligible_car_vehicles()


async def loan_policy_search_tool(question: str):
    """Search the loan policy knowledge base for an answer."""
    return await search_loan_policy(question)


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

car_loan_ltv = StructuredTool.from_function(
    coroutine=car_loan_ltv_tool,
    name="get_car_loan_ltv",
    description=(
        "Use this tool when the user asks about car loan LTV, "
        "maximum financing percentage, vehicle financing percentage, "
        "or how much of the vehicle price the bank can finance."
    ),
)


car_loan_tenure = StructuredTool.from_function(
    coroutine=car_loan_tenure_tool,
    name="get_car_loan_tenure",
    description=(
        "Use this tool when the user asks about car loan tenure, "
        "loan duration, minimum tenure, maximum tenure, "
        "or repayment period."
    ),
)


eligible_car_vehicles = StructuredTool.from_function(
    coroutine=eligible_car_vehicles_tool,
    name="get_eligible_car_vehicles",
    description=(
        "Use this tool when the user asks which vehicles are eligible "
        "for a car loan, such as cars, SUVs, hatchbacks, sedans, or MUVs."
    ),
)


loan_policy_search = StructuredTool.from_function(
    coroutine=loan_policy_search_tool,
    name="search_loan_policy",
    description=(
        "Search the loan policy knowledge base. "
        "Use this tool when the user's question requires information "
        "from the bank's loan policy documents."
    ),
)


# ============================================================
# ALL MCP TOOLS
# ============================================================

MCP_TOOLS = [
    car_loan_ltv,
    car_loan_tenure,
    eligible_car_vehicles,
    loan_policy_search,
]