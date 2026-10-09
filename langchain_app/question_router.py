"""
Deterministic question router for the AI Loan Assistant.

Simple factual questions are answered straight from the database or
the policy MCP server without spending LLM tokens; anything that
needs reasoning returns None and goes through LangGraph + Groq.

Pure module (no LLM / database imports) so it is unit-testable.
"""

import re


# Checked FIRST: these need actual reasoning.
REASONING_KEYWORDS = [
    "why",
    "explain",
    "based on",
    "analyse",
    "analyze",
    "analysis",
    "assess",
    "assessment",
    "evaluate",
    "evaluation",
    "compare",
    "comparison",
    "impact",
    "affect",
    "affects",
    "effect",
    "recommend",
    "recommendation",
    "should i",
    "would i",
    "could i",
    "how can i improve",
    "what does this mean",
    "what does that mean",
    "how does this affect",
    "how will this affect",
    "what are the implications",
]

# General policy questions that mention a customer-data keyword
# (e.g. "What documents are required for KYC?") must go to policy.
POLICY_FIRST_KEYWORDS = [
    "documents required",
    "required documents",
    "documents are required",
    "what documents",
    "which documents",
    "kyc guidelines",
    "kyc process",
    "kyc policy",
    "fraud policy",
]

ROUTE_KEYWORDS = [
    (
        "customer",
        [
            "customer information",
            "customer details",
            "profile details",
            "my profile",
            "my name",
            "my email",
            "my phone",
            "my pan",
            "my aadhaar",
            "my date of birth",
            "my dob",
        ],
    ),
    (
        "kyc",
        [
            "kyc",
            "identity verification",
            "pan verification",
            "aadhaar verification",
        ],
    ),
    (
        "fraud",
        [
            "fraud",
            "fraudulent",
            "suspicious activity",
        ],
    ),
    (
        "ai_decision",
        [
            "ai decision",
            "loan decision",
            "approval reason",
            "rejection reason",
            "loan recommendation",
        ],
    ),
    (
        "ocr",
        [
            "ocr",
            "extracted data",
            "extracted document",
            "scanned document",
            "extracted pan",
            "extracted aadhaar",
            "extracted name",
            "extracted dob",
        ],
    ),
    (
        "loan",
        [
            "loan amount",
            "loan type",
            "monthly income",
            "credit score",
            "loan status",
            "application status",
            "risk level",
            "my tenure",
            "loan details",
        ],
    ),
    (
        "policy",
        [
            "eligibility",
            "eligible",
            "interest rate",
            "emi",
            "tenure",
            "down payment",
            "ltv",
            "loan to value",
            "loan-to-value",
            "loan policy",
            "bank policy",
            "loan requirements",
            "car loan",
            "home loan",
            "personal loan",
            "education loan",
        ],
    ),
]


def _contains(text: str, keywords) -> bool:
    """
    Whole-word / whole-phrase match, so "emi" does not match "remind".
    """

    return any(
        re.search(rf"\b{re.escape(keyword)}\b", text)
        for keyword in keywords
    )


def detect_route(question: str) -> str | None:
    """
    Return the direct route for a question, or None when the question
    needs LLM reasoning.

    Example:
        "What is my credit score?"               -> "loan"
        "Based on my credit score, should I..."  -> None (LLM)
    """

    q = question.lower().strip()

    if not q:
        return None

    if _contains(q, REASONING_KEYWORDS):
        return None

    if _contains(q, POLICY_FIRST_KEYWORDS):
        return "policy"

    for route, keywords in ROUTE_KEYWORDS:
        if _contains(q, keywords):
            return route

    return None
