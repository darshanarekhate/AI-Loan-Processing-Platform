from langchain_core.messages import HumanMessage, AIMessage

from langchain_app.chains import ask_policy
from langchain_app.llm import llm
from langchain_app.memory import memory

from langchain_app.tools import (
    get_customer_info,
    get_loan_info,
    get_ocr_info,
    get_kyc_info,
    get_fraud_info,
    get_ai_decision,
)


def ask_ai(question, customer_id, application_id):

    question_lower = question.lower()

    # ==========================================================
    # Customer Information
    # ==========================================================

    if any(
        keyword in question_lower
        for keyword in [
            "customer",
            "customer information",
            "customer details",
            "profile",
            "email",
            "phone",
            "aadhaar",
            "pan",
            "dob",
        ]
    ):

        answer = get_customer_info.invoke(
            {
                "customer_id": customer_id
            }
        )

    # ==========================================================
    # Fraud Information (Moved before Loan Information)
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "fraud",
            "fraudulent",
            "fraud score",
            "fraud status",
            "risk level",
            "suspicious",
            "scam",
            "fake",
        ]
    ):

        answer = get_fraud_info.invoke(
            {
                "application_id": application_id
            }
        )

    # ==========================================================
    # Loan Information
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "loan",
            "loan status",
            "application status",
            "credit score",
            "income",
            "loan amount",
            "approved",
            "approval",
            "rejected",
            "manual review",
        ]
    ):

        answer = get_loan_info.invoke(
            {
                "application_id": application_id
            }
        )

    # ==========================================================
    # OCR Information
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "ocr",
            "document",
            "pan card",
            "aadhaar card",
            "extracted",
        ]
    ):

        answer = get_ocr_info.invoke(
            {
                "application_id": application_id
            }
        )

    # ==========================================================
    # KYC Information
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "kyc",
            "verification",
            "verified",
            "name match",
            "pan match",
            "aadhaar match",
            "dob match",
            "similarity",
        ]
    ):

        answer = get_kyc_info.invoke(
            {
                "application_id": application_id
            }
        )

    # ==========================================================
    # AI Decision
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "decision",
            "recommendation",
            "explanation",
            "why rejected",
            "why approved",
            "loan decision",
        ]
    ):

        answer = get_ai_decision.invoke(
            {
                "application_id": application_id
            }
        )

    # ==========================================================
    # Loan Policy (RAG)
    # ==========================================================

    elif any(
        keyword in question_lower
        for keyword in [
            "policy",
            "minimum",
            "documents required",
            "eligibility",
            "home loan",
            "car loan",
            "education loan",
            "personal loan",
            "interest",
            "emi",
            "faq",
            "processing fee",
            "tenure",
            "prepayment",
            "foreclosure",
        ]
    ):

        answer = ask_policy(question)

    # ==========================================================
    # General Gemini Chat
    # ==========================================================

    else:

        history = ""

        for msg in memory.messages:

            if isinstance(msg, HumanMessage):
                role = "User"
            else:
                role = "Assistant"

            history += f"{role}: {msg.content}\n"

        prompt = f"""
You are an AI Loan Assistant.

You help customers understand:

- Loan applications
- OCR
- KYC
- Fraud Detection
- AI Loan Decision
- Loan policies
- EMI
- Eligibility
- Banking questions

Conversation History:
{history}

Current Question:
{question}
"""

        response = llm.invoke(prompt)

        answer = response.content

    # ==========================================================
    # Save Conversation
    # ==========================================================

    memory.add_message(
        HumanMessage(content=question)
    )

    memory.add_message(
        AIMessage(content=answer)
    )

    return answer