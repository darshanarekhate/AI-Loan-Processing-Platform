import sys
from functools import lru_cache
from pathlib import Path

# ============================================================
# Add project root to Python path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# MCP
# ============================================================

from mcp.server.fastmcp import FastMCP

from mcp_server.policy_facts import (
    parse_eligible_vehicles,
    parse_ltv_percent,
    parse_tenure_months,
    read_policy,
)


# ============================================================
# Create MCP Server
# ============================================================

mcp = FastMCP("Loan Policy Server")


@lru_cache(maxsize=1)
def get_policy_retriever():
    """
    Load the FAISS retriever on first use (embedding model is heavy).
    """

    from langchain_app.retriever import get_retriever

    return get_retriever()


# ============================================================
# MCP Tool: Search Loan Policy
# ============================================================

@mcp.tool()
def search_loan_policy(question: str) -> str:
    """
    Search the loan policy knowledge base and return
    relevant policy information.
    """

    docs = get_policy_retriever().invoke(question)

    if not docs:
        return (
            "No relevant information was found "
            "in the loan policy."
        )

    return "\n\n---\n\n".join(doc.page_content for doc in docs)


# ============================================================
# MCP Tool: Get Car Loan LTV
# ============================================================

@mcp.tool()
def get_car_loan_ltv() -> str:
    """
    Return the maximum Loan-to-Value (LTV)
    for a car loan.
    """

    ltv = parse_ltv_percent(read_policy("car_loan.txt"))

    if ltv is None:
        return "The car loan LTV is not specified in the loan policy."

    return (
        f"The bank may finance up to {ltv}% of the "
        "vehicle's on-road price, subject to policy "
        "and customer eligibility."
    )


# ============================================================
# MCP Tool: Get Car Loan Tenure
# ============================================================

@mcp.tool()
def get_car_loan_tenure() -> str:
    """
    Return the minimum and maximum car loan tenure.
    """

    tenure = parse_tenure_months(read_policy("car_loan.txt"))

    if tenure is None:
        return "The car loan tenure is not specified in the loan policy."

    minimum, maximum = tenure

    return (
        f"Car loan tenure ranges from {minimum} months "
        f"to {maximum} months."
    )


# ============================================================
# MCP Tool: Get Eligible Vehicles
# ============================================================

@mcp.tool()
def get_eligible_car_vehicles() -> str:
    """
    Return the vehicles eligible for a car loan.
    """

    vehicles = parse_eligible_vehicles(read_policy("car_loan.txt"))

    if not vehicles:
        return "Eligible vehicles are not listed in the loan policy."

    return "Eligible vehicles include: " + ", ".join(vehicles) + "."


# ============================================================
# Start MCP Server
# ============================================================

if __name__ == "__main__":
    mcp.run()
