import logging

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from langchain_app.context import AgentContext

from database.authorization_repository import is_application_authorized
from database.customer_repository import get_customer_by_id
from database.loan_repository import get_loan_by_application
from database.ocr_repository import get_ocr_results
from database.kyc_result_repository import get_kyc_result
from database.fraud_repository import get_fraud_result
from database.decision_repository import get_decision

from langchain_app.chains import ask_policy
from utils.masking import mask_aadhaar, mask_pan, mask_phone


logger = logging.getLogger(__name__)


# ============================================================
# RuntimeConfig Context
# ============================================================

def get_context_from_config(
    config: RunnableConfig | None,
) -> AgentContext:
    """
    Retrieve customer/application context from LangGraph RuntimeConfig.

    Expected configuration:

    {
        "configurable": {
            "customer_id": "...",
            "application_id": "..."
        }
    }

    The IDs come from the authenticated Streamlit session, never from
    the LLM. There is deliberately no global fallback: a module-level
    "current context" would be shared by every concurrent session.
    """

    configurable = (config or {}).get("configurable", {})

    customer_id = configurable.get("customer_id")
    application_id = configurable.get("application_id")

    if not customer_id or not application_id:
        raise PermissionError(
            "Authenticated customer context is missing."
        )

    if not is_application_authorized(application_id, customer_id):
        raise PermissionError(
            "Application does not belong to the authenticated customer."
        )

    return AgentContext(
        customer_id=customer_id,
        application_id=application_id,
    )


# ============================================================
# Customer Information
# ============================================================

@tool
def customer_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve the authenticated customer's profile.

    Use this tool for:
    - customer information
    - profile details
    - name
    - email
    - phone number
    - PAN
    - Aadhaar
    - date of birth

    Sensitive information is masked.
    """

    context = get_context_from_config(config)

    customer = get_customer_by_id(
        context.customer_id
    )

    if not customer:
        return (
            "Customer information was not found."
        )

    return (
        "Customer Information\n\n"
        f"Customer ID: {customer['customer_id']}\n"
        f"Name: {customer['full_name']}\n"
        f"Email: {customer['email']}\n"
        f"Phone: {mask_phone(customer['phone'])}\n"
        f"PAN: {mask_pan(customer['pan'])}\n"
        f"Aadhaar: {mask_aadhaar(customer['aadhaar'])}\n"
        f"Date of Birth: {customer['date_of_birth']}"
    )


# ============================================================
# Loan Information
# ============================================================

@tool
def loan_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve the authenticated customer's loan application.

    Use this tool for:
    - loan amount
    - loan type
    - monthly income
    - credit score
    - application status
    - risk level
    - complete loan details
    """

    context = get_context_from_config(config)

    loan = get_loan_by_application(
        context.application_id
    )

    if not loan:
        return "Loan application not found."

    return (
        f"Application ID: {loan['application_id']}\n"
        f"Loan Type: {loan['loan_type']}\n"
        f"Loan Amount: ₹{loan['loan_amount']:,.0f}\n"
        f"Monthly Income: ₹{loan['monthly_income']:,.0f}\n"
        f"Tenure: {loan['tenure_months'] or '-'} months\n"
        f"Credit Score: {loan['credit_score']}\n"
        f"Application Status: {loan['application_status']}\n"
        f"Risk Level: {loan['risk_level']}"
    )


# ============================================================
# OCR Information
# ============================================================

@tool
def ocr_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve OCR extraction results.
    """

    context = get_context_from_config(config)

    results = get_ocr_results(
        context.application_id
    )

    if not results:
        return "No OCR results found."

    output = []

    for row in results:

        output.append(
            f"Document Type: {row['document_type']}\n"
            f"Extracted Name: {row['extracted_name']}\n"
            f"PAN: {mask_pan(row['extracted_pan'])}\n"
            f"Aadhaar: {mask_aadhaar(row['extracted_aadhaar'])}\n"
            f"DOB: {row['extracted_dob']}\n"
            f"Confidence: {row['confidence'] or 0:.2f}%"
        )

    return "\n\n".join(output)


# ============================================================
# KYC Information
# ============================================================

@tool
def kyc_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve KYC verification results.

    Use this tool for:
    - KYC status
    - KYC verification
    - identity verification
    - PAN verification
    - Aadhaar verification
    - name verification
    - DOB verification
    - similarity score
    """

    context = get_context_from_config(config)

    kyc = get_kyc_result(
        context.application_id
    )

    if not kyc:
        return "KYC verification result not found."

    return (
        f"Verification Status: "
        f"{kyc['verification_status']}\n"
        f"Name Match: {bool(kyc['name_match'])}\n"
        f"PAN Match: {bool(kyc['pan_match'])}\n"
        f"Aadhaar Match: {bool(kyc['aadhaar_match'])}\n"
        f"DOB Match: {bool(kyc['dob_match'])}\n"
        f"Similarity Score: "
        f"{kyc['similarity_score']}%\n"
        f"Remarks: {kyc['remarks']}"
    )


# ============================================================
# Fraud Information
# ============================================================

@tool
def fraud_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve fraud analysis results for the
    authenticated customer's loan application.

    Use this tool for:
    - fraud status
    - fraud score
    - fraud risk
    - fraud detection
    - fraud analysis
    """

    context = get_context_from_config(config)

    fraud = get_fraud_result(
        context.application_id
    )

    if not fraud:
        return "Fraud analysis has not been run for this application yet."

    return (
        f"Fraud Status: {fraud['fraud_status']}\n"
        f"Risk Level: {fraud['risk_level']}\n"
        f"Fraud Score: {fraud['fraud_score']}\n"
        f"Reason: {fraud['reason']}"
    )


# ============================================================
# AI Decision
# ============================================================

@tool
def ai_decision_information(
    config: RunnableConfig,
) -> str:
    """
    Retrieve the AI loan decision.

    Use this tool for:
    - why was my loan approved
    - why was my loan rejected
    - AI decision
    - approval reason
    - rejection reason
    - loan recommendation
    """

    context = get_context_from_config(config)

    decision = get_decision(
        context.application_id
    )

    if not decision:
        return "Loan decision not found."

    return (
        f"Decision: {decision['decision']}\n"
        f"Risk Level: {decision['risk_level']}\n\n"
        f"Explanation:\n\n"
        f"{decision['explanation']}"
    )


# ============================================================
# Loan Policy / RAG
# ============================================================

@tool
def loan_policy(
    question: str,
) -> str:
    """
    Answer general loan policy questions using
    the loan-policy RAG system.

    Use this tool for:
    - loan eligibility
    - car loan eligibility
    - home loan eligibility
    - personal loan eligibility
    - required documents
    - interest rates
    - EMI information
    - loan tenure
    - down payment
    - LTV
    - general bank loan policies

    Do NOT use this tool for customer-specific
    information.
    """

    try:

        result = ask_policy(
            question
        )

        return str(result)

    except Exception:

        logger.exception("Loan policy RAG failed")

        return (
            "Unable to retrieve loan policy "
            "information at this time."
        )


# ============================================================
# Register All Agent Tools
# ============================================================

AGENT_TOOLS = [
    customer_information,
    loan_information,
    ocr_information,
    kyc_information,
    fraud_information,
    ai_decision_information,
    loan_policy,
]
