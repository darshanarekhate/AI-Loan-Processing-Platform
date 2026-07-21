from langchain_groq import ChatGroq
from config import GROQ_API_KEY

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0
)


def ai_decision(state):

    prompt = f"""
You are an experienced bank loan approval officer.

Applicant Information

User ID:
{state["user_id"]}

Documents Uploaded:
{state["documents_uploaded"]}

OCR Completed:
{state["ocr_completed"]}

KYC Score:
{state["kyc_score"]}

KYC Status:
{state["kyc_status"]}

Fraud Detected:
{state["fraud"]}

Fraud Reason:
{state["fraud_reason"]}

Rules

1. If fraud is detected, REJECT the loan immediately.

2. Otherwise, if the KYC score is 80 or above, APPROVE the loan.

3. Otherwise, REJECT the loan.

Return ONLY in this format.

Decision:
APPROVED or REJECTED

Explanation:
<Explain the reason clearly in 3-5 sentences>
"""

    response = llm.invoke(prompt)

    return response.content