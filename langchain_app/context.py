from dataclasses import dataclass


@dataclass
class AgentContext:
    """
    Authenticated user context for the AI Loan Assistant.

    These values come from the authenticated Streamlit session
    and must not be chosen by the LLM.
    """

    customer_id: str
    application_id: str