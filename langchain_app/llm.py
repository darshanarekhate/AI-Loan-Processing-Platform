import logging
from functools import lru_cache

from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm():
    """
    Create the Groq chat model on first use.

    Lazy creation means the assistant's database and policy routes keep
    working even when GROQ_API_KEY is not configured.
    """

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured in the .env file."
        )

    logger.info("Primary LLM: Groq - %s", GROQ_MODEL)

    return ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=0.2,
        max_retries=2,
    )
