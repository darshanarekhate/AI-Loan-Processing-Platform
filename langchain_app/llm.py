import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured in the .env file."
    )


# ============================================================
# Primary LLM
# ============================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.2,
    max_retries=2,
)


print("Primary LLM: Groq - llama-3.3-70b-versatile")