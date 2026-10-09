import logging
from functools import lru_cache

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from langchain_app.state import AgentState
from langchain_app.llm import get_llm
from langchain_app.agent_tools import AGENT_TOOLS


logger = logging.getLogger(__name__)


# =========================================================
# System Prompt
# =========================================================

SYSTEM_PROMPT = """
You are an Enterprise AI Loan Assistant for a bank.

Your responsibilities:

1. Help authenticated customers understand their loan application.

2. Retrieve customer-specific information using the appropriate tools.

3. Answer general bank policy questions using the loan_policy tool.

4. Never invent customer information.

5. Never guess customer-specific values.

6. If the user asks for customer-specific information, ALWAYS use
   the appropriate customer/application tool before answering.

7. After a tool returns information, use that information to answer
   the customer's question directly.

8. Do not say that information is unavailable if the authorized tool
   has returned it.

9. For simple factual questions, give a short direct answer.

10. For complex questions, provide a clear explanation.

11. Protect sensitive information and respect masking performed by
    the tools.

12. NEVER ask the user to provide a customer ID or application ID
    to retrieve their own information.

13. NEVER attempt to retrieve another customer's information.

14. Customer and application authorization is controlled by the
    application runtime context, not by the user's message.

15. Treat tool results as the source of truth for customer-specific
    information.

Tool selection:

- Customer name, email, phone, PAN, Aadhaar, DOB
  -> customer_information

- Loan amount, loan type, monthly income, credit score,
  application status, risk level
  -> loan_information

- OCR/document extraction
  -> ocr_information

- KYC verification
  -> kyc_information

- Fraud analysis
  -> fraud_information

- AI loan decision
  -> ai_decision_information

- Loan eligibility, interest rates, tenure, LTV,
  required documents and other bank policies
  -> loan_policy

Important:

The authenticated customer ID and application ID are supplied by
the application runtime.

Do not attempt to supply, modify, guess, or request these IDs
as tool arguments.

When an authorized tool returns valid information, trust the
tool result as the source of truth.
"""


# =========================================================
# Agent Node
# =========================================================

def agent_node(
    state: AgentState,
    config: RunnableConfig,
):
    """
    Main reasoning node.

    The authenticated customer/application information is passed
    through LangGraph runtime configuration.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    llm_with_tools = get_llm().bind_tools(AGENT_TOOLS)

    response = llm_with_tools.invoke(
        messages,
        config=config,
    )

    if getattr(response, "tool_calls", None):
        logger.info(
            "Agent tool calls: %s",
            [call["name"] for call in response.tool_calls],
        )

    return {
        "messages": [response]
    }


# =========================================================
# Tool Node
# =========================================================

tool_node = ToolNode(AGENT_TOOLS)


# =========================================================
# Decide Next Step
# =========================================================

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


# =========================================================
# Build Graph
# =========================================================

@lru_cache(maxsize=1)
def get_agent():
    """
    Compile the LangGraph agent once, on first use.
    """

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
    )

    graph.add_edge(
        "tools",
        "agent",
    )

    return graph.compile()
