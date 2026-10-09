"""
Structured facts parsed from the policy documents.

The MCP server answers "exact" questions (LTV, tenure, eligible
vehicles) from these parsers instead of hard-coded strings, so the
answers always follow Knowledge_Base/car_loan.txt.
"""

import re
from pathlib import Path


KNOWLEDGE_BASE = Path(__file__).resolve().parent.parent / "Knowledge_Base"


def read_policy(name: str) -> str:
    return (KNOWLEDGE_BASE / name).read_text(encoding="utf-8")


def parse_ltv_percent(text: str) -> int | None:
    section = re.search(
        r"Loan-to-Value.*?up to\s*(\d+)\s*%",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    return int(section.group(1)) if section else None


def parse_tenure_months(text: str) -> tuple[int, int] | None:
    section = re.search(
        r"Loan Tenure\s*Minimum:\s*(\d+)\s*Months\s*Maximum:\s*(\d+)\s*Months",
        text,
        re.IGNORECASE,
    )

    if not section:
        return None

    return int(section.group(1)), int(section.group(2))


def parse_eligible_vehicles(text: str) -> list[str]:
    """
    Return the bullet points listed under the "Eligible Vehicles" heading.
    """

    section = re.search(
        r"Eligible Vehicles\s*\n((?:\s*•[^\n]+\n?)+)",
        text,
        re.IGNORECASE,
    )

    if not section:
        return []

    return [
        line.strip().lstrip("•").strip()
        for line in section.group(1).splitlines()
        if line.strip()
    ]
