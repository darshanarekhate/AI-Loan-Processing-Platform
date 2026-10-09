import logging

from langchain_core.messages import HumanMessage

from langchain_app.agent import get_agent
from langchain_app.context import AgentContext
from langchain_app.question_router import detect_route
from langchain_app.state import AgentState

from langchain_app.agent_tools import (
    customer_information,
    loan_information,
    ocr_information,
    kyc_information,
    fraud_information,
    ai_decision_information,
)


logger = logging.getLogger(__name__)


DIRECT_TOOLS = {
    "customer": customer_information,
    "loan": loan_information,
    "kyc": kyc_information,
    "fraud": fraud_information,
    "ocr": ocr_information,
    "ai_decision": ai_decision_information,
}


# ============================================================
# MCP RESPONSE CLEANER
# ============================================================

def clean_mcp_response(result) -> str:
    """
    Convert MCP tool response into clean text.

    MCP responses commonly look like:

    [
        {
            "type": "text",
            "text": "actual response",
            "id": "..."
        }
    ]

    The UI should receive only the actual text.
    """

    if result is None:
        return ""

    if isinstance(result, list):

        parts = []

        for item in result:

            if isinstance(item, dict):

                if item.get("type") == "text" and item.get("text"):
                    parts.append(str(item["text"]))

            elif isinstance(item, str) and item.strip():
                parts.append(item.strip())

        return "\n".join(parts).strip()

    if isinstance(result, dict):

        if "text" in result:
            return str(result["text"]).strip()

    return str(result).strip()


# ============================================================
# MCP POLICY EXECUTION
# ============================================================

def _pick_mcp_tool(question: str) -> str:
    """
    Choose the dedicated MCP policy tool for a question.
    """

    q = question.lower()

    about_car = "car" in q or "vehicle" in q

    if "ltv" in q or "loan to value" in q or "loan-to-value" in q:
        return "get_car_loan_ltv"

    if about_car and (
        "tenure" in q or "repayment period" in q or "how long" in q
    ):
        return "get_car_loan_tenure"

    if about_car and (
        "eligible vehicle" in q
        or "which vehicle" in q
        or "vehicles are eligible" in q
    ):
        return "get_eligible_car_vehicles"

    return "search_loan_policy"


def execute_mcp_policy(
    question: str,
) -> str:
    """
    Execute loan-policy questions through MCP.

    If the MCP server cannot be reached, fall back to the in-process
    RAG pipeline so policy answers stay available.
    """

    tool_name = _pick_mcp_tool(question)

    try:

        from mcp_client.loan_policy_mcp import call_policy_tool_sync

        logger.info("MCP tool: %s", tool_name)

        answer = clean_mcp_response(
            call_policy_tool_sync(tool_name, question)
        )

        if answer:
            return answer

    except Exception:

        logger.exception("MCP policy call failed; using local RAG")

    from langchain_app.chains import ask_policy

    return ask_policy(question)


# ============================================================
# Direct Tool Execution
# ============================================================

def execute_direct_route(
    route: str,
    customer_id: str,
    application_id: str,
    question: str,
) -> str:
    """
    Execute database tools or MCP policy tools directly
    without invoking the Groq LLM.
    """

    if route == "policy":
        return execute_mcp_policy(question)

    tool = DIRECT_TOOLS.get(route)

    if tool is None:
        raise ValueError(f"Unsupported direct route: {route}")

    return str(
        tool.invoke(
            {},
            config={
                "configurable": {
                    "customer_id": customer_id,
                    "application_id": application_id,
                }
            },
        )
    )


# ============================================================
# Response text
# ============================================================

def _message_text(content) -> str:

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    parts.append(item["text"])

            elif isinstance(item, str) and item.strip():
                parts.append(item)

        return "\n".join(parts).strip()

    return str(content).strip()


# ============================================================
# Error mapping
# ============================================================

def _friendly_error(error: Exception) -> str:

    message = str(error).lower()

    if isinstance(error, PermissionError):
        return "⚠️ You are not authorised to view this application."

    if (
        "429" in message
        or "rate limit" in message
        or "rate_limit" in message
        or "too many requests" in message
        or "tokens per day" in message
    ):
        return (
            "⚠️ The AI service has temporarily reached its usage limit.\n\n"
            "Database and loan-policy information remain available "
            "directly. Please try the AI reasoning question again later."
        )

    if (
        "groq_api_key" in message
        or "401" in message
        or "invalid api key" in message
        or "invalid_api_key" in message
    ):
        return (
            "⚠️ The AI reasoning service is not configured.\n\n"
            "Direct questions (loan amount, KYC status, policy) still work."
        )

    # Technical details go to the server log, not to the customer.
    return (
        "⚠️ The AI assistant encountered an error. "
        "Please try again in a moment."
    )


# ============================================================
# Ask Agent
# ============================================================

def ask_agent(
    question: str,
    customer_id: str,
    application_id: str,
) -> dict:
    """
    Entry point for the LangGraph AI Loan Assistant.

    Direct database and policy routes are handled without
    invoking Groq. Questions requiring actual reasoning are sent
    through LangGraph + Groq.
    """

    try:

        route = detect_route(question)

        logger.info("Assistant route: %s", route or "llm")

        if route is not None:

            response_text = execute_direct_route(
                route=route,
                customer_id=customer_id,
                application_id=application_id,
                question=question,
            ).strip()

        else:

            state: AgentState = {
                "messages": [HumanMessage(content=question)],
                "context": AgentContext(
                    customer_id=customer_id,
                    application_id=application_id,
                ),
            }

            result = get_agent().invoke(
                state,
                config={
                    "configurable": {
                        "customer_id": customer_id,
                        "application_id": application_id,
                    },
                    "recursion_limit": 25,
                },
            )

            messages = result.get("messages", [])

            response_text = (
                _message_text(messages[-1].content) if messages else ""
            )

        if not response_text:

            return {
                "success": False,
                "error": (
                    "⚠️ The AI assistant did not return a response. "
                    "Please try again."
                ),
            }

        return {
            "success": True,
            "response": response_text,
        }

    except Exception as error:

        logger.exception("AI assistant error")

        return {
            "success": False,
            "error": _friendly_error(error),
        }
