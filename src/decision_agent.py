from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)


def ai_decision(
    customer_id,
    application_id,
    kyc_status,
    fraud_status,
    fraud_reason,
    credit_score,
    monthly_income,
    loan_amount,
):

    prompt = f"""
You are a Senior Bank Loan Approval Officer.

Applicant Details

Customer ID:
{customer_id}

Application ID:
{application_id}

Credit Score:
{credit_score}

Monthly Income:
₹{monthly_income:,.0f}

Requested Loan Amount:
₹{loan_amount:,.0f}

KYC Status:
{kyc_status}

Fraud Status:
{fraud_status}

Fraud Reason:
{fraud_reason}

Rules

1. If Fraud Status is HIGH
Decision = REJECTED

2. Else if KYC Status is MANUAL REVIEW
Decision = MANUAL REVIEW

3. Else if Credit Score >= 750
Decision = APPROVED

4. Else if Credit Score between 650 and 749
Decision = MANUAL REVIEW

5. Else
Decision = REJECTED

Return ONLY in this format.

Decision:
APPROVED
or
REJECTED
or
MANUAL REVIEW

Explanation:
Explain in 3-5 short sentences.
"""

    response = llm.invoke(prompt)

    return response.content