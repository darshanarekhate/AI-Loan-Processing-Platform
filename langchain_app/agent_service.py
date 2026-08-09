from langchain_core.messages import HumanMessage

from langchain_app.agent import agent
from langchain_app.context import AgentContext
from langchain_app.state import AgentState
from langchain_app.llm import llm

from langchain_app.agent_tools import (
    customer_information,
    loan_information,
    ocr_information,
    kyc_information,
    fraud_information,
    ai_decision_information,
    loan_policy,
)

# ============================================================
# MCP POLICY TOOLS
# ============================================================

from mcp_client.loan_policy_mcp import (
    get_car_loan_ltv_sync,
    get_car_loan_tenure_sync,
    get_eligible_car_vehicles_sync,
    search_loan_policy_sync,
)


# ============================================================
# Active LLM Information
# ============================================================

print("====================================")
print("ACTIVE LLM:", type(llm).__name__)
print("====================================")


# ============================================================
# Direct Route Detection
# ============================================================

def detect_route(question: str):
    """
    Detect questions that can be answered directly without
    sending the request through the LLM.

    Important:
    Reasoning questions are detected FIRST.

    Example:
        "What is my credit score?"
            -> loan direct route

        "Based on my credit score, explain whether..."
            -> LangGraph + Groq

    This prevents questions containing words such as
    "income" or "credit score" from being incorrectly
    routed to the direct database tool.
    """

    q = question.lower().strip()

    # ========================================================
    # 1. REASONING / EXPLANATION QUESTIONS
    # ========================================================
    #
    # These must be checked BEFORE customer/loan/policy
    # keyword detection.
    #
    # They require LangGraph + Groq reasoning.
    # ========================================================

    reasoning_keywords = [
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
        "what does this mean",
        "what does that mean",
        "how does this affect",
        "how will this affect",
        "what are the implications",
    ]

    if any(keyword in q for keyword in reasoning_keywords):
        return None

    # ========================================================
    # 2. CUSTOMER INFORMATION
    # ========================================================

    customer_keywords = [
        "customer information",
        "customer details",
        "profile details",
        "my name",
        "my email",
        "my phone",
        "my pan",
        "my aadhaar",
        "my date of birth",
        "my dob",
    ]

    if any(keyword in q for keyword in customer_keywords):
        return "customer"

    # ========================================================
    # 3. LOAN INFORMATION
    # ========================================================

    loan_keywords = [
        "loan amount",
        "loan type",
        "monthly income",
        "credit score",
        "loan status",
        "application status",
        "risk level",
        "loan details",
        "complete loan details",
    ]

    if any(keyword in q for keyword in loan_keywords):
        return "loan"

    # ========================================================
    # 4. KYC
    # ========================================================

    kyc_keywords = [
        "kyc",
        "kyc status",
        "kyc verification",
        "identity verification",
        "pan verification",
        "aadhaar verification",
    ]

    if any(keyword in q for keyword in kyc_keywords):
        return "kyc"

    # ========================================================
    # 5. FRAUD
    # ========================================================

    fraud_keywords = [
        "fraud",
        "fraud status",
        "fraud score",
        "fraud risk",
        "fraud analysis",
        "fraud detection",
        "suspicious activity",
    ]

    if any(keyword in q for keyword in fraud_keywords):
        return "fraud"

    # ========================================================
    # 6. AI DECISION
    # ========================================================

    decision_keywords = [
        "why was my loan approved",
        "why was my loan rejected",
        "why approved",
        "why rejected",
        "approval reason",
        "rejection reason",
        "ai decision",
        "loan decision",
        "loan recommendation",
    ]

    if any(keyword in q for keyword in decision_keywords):
        return "ai_decision"

    # ========================================================
    # 7. OCR
    # ========================================================

    ocr_keywords = [
        "ocr",
        "ocr information",
        "extracted data",
        "extracted document",
        "scanned document",
        "extracted pan",
        "extracted aadhaar",
        "extracted name",
        "extracted dob",
    ]

    if any(keyword in q for keyword in ocr_keywords):
        return "ocr"

    # ========================================================
    # 8. GENERAL LOAN POLICY
    # ========================================================

    policy_keywords = [
        "eligibility",
        "eligible",
        "required documents",
        "documents required",
        "interest rate",
        "interest rates",
        "emi",
        "loan tenure",
        "tenure",
        "down payment",
        "ltv",
        "loan policy",
        "bank policy",
        "loan requirements",
        "car loan eligibility",
        "home loan eligibility",
        "personal loan eligibility",
        "car loan",
        "home loan",
        "personal loan",
        "education loan",
    ]

    if any(keyword in q for keyword in policy_keywords):
        return "policy"

    # ========================================================
    # 9. NO DIRECT ROUTE
    # ========================================================
    #
    # Questions that do not match a direct route go through
    # LangGraph + Groq.
    # ========================================================

    return None


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

    # --------------------------------------------------------
    # List response
    # --------------------------------------------------------

    if isinstance(result, list):

        parts = []

        for item in result:

            # Dictionary returned by MCP
            if isinstance(item, dict):

                if item.get("type") == "text":

                    text = item.get(
                        "text",
                        "",
                    )

                    if text:
                        parts.append(
                            str(text)
                        )

            # String item
            elif isinstance(item, str):

                if item.strip():
                    parts.append(
                        item.strip()
                    )

        return "\n".join(parts).strip()

    # --------------------------------------------------------
    # Dictionary response
    # --------------------------------------------------------

    if isinstance(result, dict):

        if result.get("type") == "text":

            return str(
                result.get(
                    "text",
                    "",
                )
            ).strip()

        if "text" in result:

            return str(
                result["text"]
            ).strip()

    # --------------------------------------------------------
    # String response
    # --------------------------------------------------------

    return str(result).strip()


# ============================================================
# MCP POLICY EXECUTION
# ============================================================

def execute_mcp_policy(
    question: str,
) -> str:
    """
    Execute loan-policy questions through MCP.

    Dedicated MCP tools are used whenever the question
    clearly matches a specific policy operation.

    General policy questions use search_loan_policy().
    """

    q = question.lower().strip()

    # ========================================================
    # CAR LOAN LTV
    # ========================================================

    if (
        "ltv" in q
        and (
            "car" in q
            or "vehicle" in q
            or "loan" in q
        )
    ):

        print("MCP TOOL: get_car_loan_ltv")

        result = get_car_loan_ltv_sync()

        return clean_mcp_response(
            result
        )

    # ========================================================
    # CAR LOAN TENURE
    # ========================================================

    if (
        (
            "tenure" in q
            or "repayment period" in q
            or "how long" in q
        )
        and (
            "car" in q
            or "vehicle" in q
            or "loan" in q
        )
    ):

        print("MCP TOOL: get_car_loan_tenure")

        result = get_car_loan_tenure_sync()

        return clean_mcp_response(
            result
        )

    # ========================================================
    # ELIGIBLE VEHICLES
    # ========================================================

    if (
        (
            "eligible vehicle" in q
            or "eligible vehicles" in q
            or "which vehicles" in q
            or "which vehicle" in q
            or "vehicles are eligible" in q
        )
        and (
            "car" in q
            or "vehicle" in q
            or "loan" in q
        )
    ):

        print(
            "MCP TOOL: get_eligible_car_vehicles"
        )

        result = get_eligible_car_vehicles_sync()
        return clean_mcp_response(
            result
        )

    # ========================================================
    # GENERAL LOAN POLICY SEARCH
    # ========================================================

    print("MCP TOOL: search_loan_policy")

    result = search_loan_policy_sync(
        question
    )

    return clean_mcp_response(
        result
    )


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

    context_config = {
        "configurable": {
            "customer_id": customer_id,
            "application_id": application_id,
        }
    }

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    if route == "customer":

        result = customer_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # Loan
    # --------------------------------------------------------

    if route == "loan":

        result = loan_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # KYC
    # --------------------------------------------------------

    if route == "kyc":

        result = kyc_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # Fraud
    # --------------------------------------------------------

    if route == "fraud":

        result = fraud_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    if route == "ocr":

        result = ocr_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # AI Decision
    # --------------------------------------------------------

    if route == "ai_decision":

        result = ai_decision_information.invoke(
            {},
            config=context_config,
        )

        return str(result)

    # --------------------------------------------------------
    # Loan Policy
    #
    # IMPORTANT:
    #
    # Policy questions now go through MCP.
    #
    # Groq is NOT called here.
    # --------------------------------------------------------

    if route == "policy":

        return execute_mcp_policy(
            question
        )

    # --------------------------------------------------------
    # Unsupported Route
    # --------------------------------------------------------

    raise ValueError(
        f"Unsupported direct route: {route}"
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
    invoking Groq.

    Questions requiring actual reasoning are sent through
    LangGraph + Groq.
    """

    try:

        # ----------------------------------------------------
        # Detect Route
        # ----------------------------------------------------

        route = detect_route(
            question
        )

        print("\n====================================")
        print("ASK_AGENT")
        print("====================================")
        print(
            f"Customer ID: {customer_id}"
        )
        print(
            f"Application ID: {application_id}"
        )
        print(
            f"Question: {question}"
        )
        print(
            f"Detected route: {route}"
        )

        # ----------------------------------------------------
        # Direct Route
        # ----------------------------------------------------

        if route is not None:

            print(
                "ROUTE: DIRECT TOOL"
            )

            print(
                f"DIRECT TOOL: {route}"
            )

            # ------------------------------------------------
            # MCP indicator
            # ------------------------------------------------

            if route == "policy":

                print(
                    "POLICY ROUTE: MCP"
                )

            response_text = execute_direct_route(
                route=route,
                customer_id=customer_id,
                application_id=application_id,
                question=question,
            )

            response_text = str(
                response_text
            ).strip()

            print(
                "DIRECT TOOL RESPONSE:"
            )

            print(
                response_text
            )

            print(
                "===================================="
            )

            if not response_text:

                return {
                    "success": False,
                    "error": (
                        "⚠️ The requested information "
                        "was not returned."
                    ),
                }

            return {
                "success": True,
                "response": response_text,
            }

        # ----------------------------------------------------
        # LangGraph + Groq
        # ----------------------------------------------------

        print(
            "ROUTE: LANGGRAPH + LLM"
        )

        context = AgentContext(
            customer_id=customer_id,
            application_id=application_id,
        )

        state: AgentState = {
            "messages": [
                HumanMessage(
                    content=question
                )
            ],
            "context": context,
        }

        config = {
            "configurable": {
                "customer_id": customer_id,
                "application_id": application_id,
            },
            "recursion_limit": 50,
        }

        result = agent.invoke(
            state,
            config=config,
        )

        messages = result.get(
            "messages",
            [],
        )

        if not messages:

            return {
                "success": False,
                "error": (
                    "⚠️ The AI assistant did not "
                    "return any messages."
                ),
            }

        content = messages[-1].content

        # ----------------------------------------------------
        # Convert Structured Content
        # ----------------------------------------------------

        if isinstance(
            content,
            list,
        ):

            parts = []

            for item in content:

                if isinstance(
                    item,
                    dict,
                ):

                    if item.get(
                        "type"
                    ) == "text":

                        text = item.get(
                            "text",
                            "",
                        )

                        if text:

                            parts.append(
                                text
                            )

                elif isinstance(
                    item,
                    str,
                ):

                    if item.strip():

                        parts.append(
                            item
                        )

            response_text = "\n".join(
                parts
            ).strip()

        else:

            response_text = str(
                content
            ).strip()

        # ----------------------------------------------------
        # Empty Response Protection
        # ----------------------------------------------------

        if not response_text:

            return {
                "success": False,
                "error": (
                    "⚠️ The AI assistant did not "
                    "return a response. "
                    "Please try again."
                ),
            }

        print(
            "\nFINAL AI RESPONSE:"
        )

        print(
            response_text
        )

        print(
            "===================================="
        )

        return {
            "success": True,
            "response": response_text,
        }

    # ========================================================
    # Error Handling
    # ========================================================

    except Exception as e:

        error_message = str(e)

        error_lower = (
            error_message.lower()
        )

        print(
            "\n===================================="
        )

        print(
            "AGENT ERROR"
        )

        print(
            "===================================="
        )

        print(
            error_message
        )

        print(
            "===================================="
        )

        # ----------------------------------------------------
        # Groq Rate Limit
        # ----------------------------------------------------

        if (
            "429" in error_message
            or "rate limit" in error_lower
            or "rate_limit" in error_lower
            or "too many requests"
            in error_lower
            or "tokens per day"
            in error_lower
        ):

            return {
                "success": False,
                "error": (
                    "⚠️ The AI service has temporarily "
                    "reached the Groq usage limit.\n\n"
                    "Database and MCP loan-policy "
                    "information remain available "
                    "directly. "
                    "Please try the AI reasoning question "
                    "again later."
                ),
            }

        # ----------------------------------------------------
        # Groq Authentication
        # ----------------------------------------------------

        if (
            "401" in error_message
            or "authentication"
            in error_lower
            or "invalid api key"
            in error_lower
            or "invalid_api_key"
            in error_lower
        ):

            return {
                "success": False,
                "error": (
                    "⚠️ Groq API authentication failed.\n\n"
                    "Please check the GROQ_API_KEY "
                    "configuration."
                ),
            }

        # ----------------------------------------------------
        # MCP Error
        # ----------------------------------------------------

        if (
            "mcp" in error_lower
            or "stdio" in error_lower
            or "jsonrpc" in error_lower
            or "connection closed"
            in error_lower
        ):

            return {
                "success": False,
                "error": (
                    "⚠️ The Loan Policy MCP service "
                    "could not be reached.\n\n"
                    "Customer and loan database "
                    "information remain available. "
                    "Please try the policy question again."
                ),
            }

        # ----------------------------------------------------
        # Generic Error
        # ----------------------------------------------------

        return {
            "success": False,
            "error": (
                "⚠️ The AI assistant encountered "
                "an error.\n\n"
                f"Technical details: "
                f"{error_message}"
            ),
        }