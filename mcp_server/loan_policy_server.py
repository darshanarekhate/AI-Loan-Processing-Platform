import sys
from pathlib import Path

# ============================================================
# Add project root to Python path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# LangChain Loan Policy Retriever
# ============================================================

from langchain_app.retriever import get_retriever


# ============================================================
# MCP
# ============================================================

from mcp.server.fastmcp import FastMCP


# ============================================================
# Create MCP Server
# ============================================================

mcp = FastMCP("Loan Policy Server")


# ============================================================
# Retriever
# ============================================================

retriever = get_retriever()


# ============================================================
# MCP Tool: Search Loan Policy
# ============================================================

@mcp.tool()
def search_loan_policy(question: str) -> str:
    """
    Search the loan policy knowledge base and return
    relevant policy information.
    """

    docs = retriever.invoke(question)

    if not docs:
        return (
            "No relevant information was found "
            "in the loan policy."
        )

    results = []

    for doc in docs:
        results.append(doc.page_content)

    return "\n\n---\n\n".join(results)


# ============================================================
# MCP Tool: Get Car Loan LTV
# ============================================================

@mcp.tool()
def get_car_loan_ltv() -> str:
    """
    Return the maximum Loan-to-Value (LTV)
    for a car loan.
    """

    return (
        "The bank may finance up to 90% of the "
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

    return (
        "Car loan tenure ranges from "
        "12 months to 84 months."
    )


# ============================================================
# MCP Tool: Get Eligible Vehicles
# ============================================================

@mcp.tool()
def get_eligible_car_vehicles() -> str:
    """
    Return the vehicles eligible for a car loan.
    """

    return (
        "Eligible vehicles include: "
        "New Cars, Used Cars, SUVs, Hatchbacks, "
        "Sedans, and Multi-Utility Vehicles (MUVs)."
    )


# ============================================================
# Start MCP Server
# ============================================================

if __name__ == "__main__":
    mcp.run()