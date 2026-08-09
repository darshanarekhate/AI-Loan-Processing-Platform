from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

from langchain_app.context import AgentContext


class AgentState(TypedDict):
    """
    Shared state for the AI Loan Agent.
    """

    messages: Annotated[list, add_messages]

    context: AgentContext