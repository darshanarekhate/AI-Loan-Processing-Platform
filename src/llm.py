import json
import re

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from config import GROQ_API_KEY


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0,
)


def analyze_loan(state):

    prompt = f"""
You are an AI Loan Approval Officer.

Analyze the following loan application.

Name: {state["name"]}
Age: {state["age"]}
PAN: {state["pan"]}
Aadhaar: {state["aadhaar"]}
Monthly Income: {state["income"]}
Loan Amount: {state["loan_amount"]}
Credit Score: {state["credit_score"]}
KYC Score: {state["kyc_score"]}

Respond ONLY with a valid JSON object.

Example:

{{
    "decision":"APPROVED",
    "explanation":"Reason for approval."
}}

Do not use markdown.
Do not write anything before or after the JSON.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    content = response.content.strip()

    print("\n" + "=" * 60)
    print("RAW LLM RESPONSE")
    print("=" * 60)
    print(content)

    # Remove markdown fences if present
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        data = json.loads(content)

    except json.JSONDecodeError:

        # Extract first JSON object from the response
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError(
                f"LLM did not return valid JSON.\n\nResponse was:\n{content}"
            )

        data = json.loads(match.group())

    state["decision"] = data["decision"]
    state["explanation"] = data["explanation"]

    return state