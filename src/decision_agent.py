"""
LLM explanation layer for loan decisions.

The decision itself comes from services.decision_engine. This module
only turns the rule outcome into a short customer-friendly explanation.
If no LLM is configured (or the call fails) the deterministic summary
is returned, so the decision flow never depends on an external API.
"""

import logging
from functools import lru_cache

from config import GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL
from services.decision_engine import DecisionResult


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_llm():
    """
    Create the explanation LLM lazily (Gemini first, then Groq).
    """

    if GEMINI_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
        )

    if GROQ_API_KEY:
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0,
        )

    return None


def build_explanation_prompt(
    result: DecisionResult,
    loan_type: str,
    loan_amount: float,
    monthly_income: float,
    credit_score: int,
) -> str:

    checks = "\n".join(
        f"- {check.name}: {'PASS' if check.passed else 'FAIL'} ({check.detail})"
        for check in result.checks
    )

    reasons = "\n".join(f"- {reason}" for reason in result.reasons)

    return f"""
You are a bank loan officer writing to a customer.

The bank's rule engine has ALREADY decided this application.
You must NOT change, question or re-evaluate the decision.

Loan type: {loan_type}
Requested amount: Rs. {loan_amount:,.0f}
Monthly income: Rs. {monthly_income:,.0f}
Credit score: {credit_score}

FINAL DECISION: {result.decision}
RISK LEVEL: {result.risk_level}

Policy checks:
{checks}

Reasons:
{reasons}

Estimated EMI: Rs. {result.emi:,.0f} for {result.tenure_months} months at {result.interest_rate:.2f}% p.a.
Maximum affordable amount at 50% FOIR: Rs. {result.max_eligible_amount:,.0f}

Write 3-5 short sentences explaining the decision to the customer.
If the decision is not APPROVED, give one concrete, actionable
suggestion (for example a lower amount or a longer tenure).
Do not include customer IDs, PAN or Aadhaar numbers.
""".strip()


def explain_decision(
    result: DecisionResult,
    loan_type: str,
    loan_amount: float,
    monthly_income: float,
    credit_score: int,
) -> str:
    """
    Return a natural-language explanation followed by the rule summary.
    """

    summary = result.summary()

    try:
        llm = _get_llm()
    except Exception:
        logger.exception("Could not initialise the explanation LLM")
        llm = None

    if llm is None:
        return summary

    prompt = build_explanation_prompt(
        result,
        loan_type,
        loan_amount,
        monthly_income,
        credit_score,
    )

    try:
        response = llm.invoke(prompt)
        explanation = str(response.content).strip()
    except Exception:
        logger.exception("LLM explanation failed; using rule summary")
        return summary

    if not explanation:
        return summary

    return f"{explanation}\n\n---\n\n{summary}"
