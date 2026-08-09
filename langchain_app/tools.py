from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from database.customer_repository import get_customer_by_id
from database.loan_repository import get_loan_by_application
from database.ocr_repository import get_ocr_results
from database.kyc_result_repository import get_kyc_result
from database.fraud_repository import get_fraud_result
from database.decision_repository import get_decision

from langchain_app.rag_tool import search_loan_policy


# ============================================================
# Helper Functions
# ============================================================

def _get_authenticated_customer_id(config: RunnableConfig) -> str | None:
    """
    Get the authenticated customer ID from LangGraph runtime config.

    The customer ID comes from the authenticated application/session,
    NOT from the LLM.
    """

    configurable = config.get("configurable", {})

    return configurable.get("customer_id")


def _get_authenticated_application_id(config: RunnableConfig) -> str | None:
    """
    Get the authenticated application ID from LangGraph runtime config.

    The application ID comes from the authenticated application/session,
    NOT from the LLM.
    """

    configurable = config.get("configurable", {})

    return configurable.get("application_id")


# ============================================================
# Customer Information
# ============================================================

@tool
def get_customer_info(config: RunnableConfig) -> str:
    """
    Retrieve information for the currently authenticated customer.

    The customer ID is obtained from the authenticated runtime context.
    The LLM cannot choose another customer ID.
    """

    customer_id = _get_authenticated_customer_id(config)

    if not customer_id:
        return "Authorization error: authenticated customer not found."

    customer = get_customer_by_id(customer_id)

    if not customer:
        return "Customer not found."

    phone = customer["phone"] or ""
    pan = customer["pan"] or ""
    aadhaar = customer["aadhaar"] or ""

    # --------------------------------------------------------
    # Mask phone number
    # --------------------------------------------------------

    if len(phone) >= 4:
        masked_phone = "*" * (len(phone) - 4) + phone[-4:]
    else:
        masked_phone = "****"

    # --------------------------------------------------------
    # Mask PAN
    # --------------------------------------------------------

    if len(pan) >= 6:
        masked_pan = pan[:5] + "*" * (len(pan) - 6) + pan[-1:]
    else:
        masked_pan = "******"

    # --------------------------------------------------------
    # Mask Aadhaar
    # --------------------------------------------------------

    if len(aadhaar) >= 4:
        masked_aadhaar = "*" * (len(aadhaar) - 4) + aadhaar[-4:]
    else:
        masked_aadhaar = "********"

    return f"""
Customer ID: {customer["customer_id"]}
Name: {customer["full_name"]}
Email: {customer["email"]}
Phone: {masked_phone}
PAN: {masked_pan}
Aadhaar: {masked_aadhaar}
Date of Birth: {customer["date_of_birth"]}
""".strip()


# ============================================================
# Loan Information
# ============================================================

@tool
def get_loan_info(config: RunnableConfig) -> str:
    """
    Retrieve loan information for the currently authenticated
    loan application.

    The application ID is obtained from the authenticated runtime
    context. The LLM cannot choose another application.
    """

    application_id = _get_authenticated_application_id(config)

    if not application_id:
        return "Authorization error: authenticated application not found."

    loan = get_loan_by_application(application_id)

    if not loan:
        return "Loan application not found."

    # --------------------------------------------------------
    # Authorization check
    # --------------------------------------------------------

    customer_id = _get_authenticated_customer_id(config)

    if customer_id and loan["customer_id"] != customer_id:
        return "Authorization error: this loan application does not belong to the authenticated customer."

    return f"""
Application ID: {loan["application_id"]}
Loan Type: {loan["loan_type"]}
Loan Amount: ₹{loan["loan_amount"]:,.0f}
Monthly Income: ₹{loan["monthly_income"]:,.0f}
Credit Score: {loan["credit_score"]}
Application Status: {loan["application_status"]}
Risk Level: {loan["risk_level"]}
""".strip()


# ============================================================
# OCR Information
# ============================================================

@tool
def get_ocr_info(config: RunnableConfig) -> str:
    """
    Retrieve OCR results for the currently authenticated
    loan application.
    """

    application_id = _get_authenticated_application_id(config)
    customer_id = _get_authenticated_customer_id(config)

    if not application_id:
        return "Authorization error: authenticated application not found."

    results = get_ocr_results(application_id)

    if not results:
        return "No OCR results found."

    output = ""

    for row in results:

        # ----------------------------------------------------
        # Authorization check
        # ----------------------------------------------------

        if customer_id and row["customer_id"] != customer_id:
            continue

        output += f"""
Document Type: {row["document_type"]}
Extracted Name: {row["extracted_name"]}
PAN: {row["extracted_pan"]}
Aadhaar: {row["extracted_aadhaar"]}
DOB: {row["extracted_dob"]}
Confidence: {row["confidence"]:.2f}%

"""

    if not output.strip():
        return "No authorized OCR results found."

    return output.strip()


# ============================================================
# KYC Information
# ============================================================

@tool
def get_kyc_info(config: RunnableConfig) -> str:
    """
    Retrieve KYC verification results for the authenticated
    loan application.
    """

    application_id = _get_authenticated_application_id(config)
    customer_id = _get_authenticated_customer_id(config)

    if not application_id:
        return "Authorization error: authenticated application not found."

    kyc = get_kyc_result(application_id)

    if not kyc:
        return "KYC verification result not found."

    if customer_id and kyc["customer_id"] != customer_id:
        return "Authorization error: KYC information does not belong to the authenticated customer."

    return f"""
Verification Status: {kyc["verification_status"]}
Name Match: {bool(kyc["name_match"])}
PAN Match: {bool(kyc["pan_match"])}
Aadhaar Match: {bool(kyc["aadhaar_match"])}
DOB Match: {bool(kyc["dob_match"])}
Similarity Score: {kyc["similarity_score"]}%
Remarks: {kyc["remarks"]}
""".strip()


# ============================================================
# Fraud Information
# ============================================================

@tool
def get_fraud_info(config: RunnableConfig) -> str:
    """
    Retrieve fraud analysis for the authenticated loan application.
    """

    application_id = _get_authenticated_application_id(config)
    customer_id = _get_authenticated_customer_id(config)

    if not application_id:
        return "Authorization error: authenticated application not found."

    fraud = get_fraud_result(application_id)

    if not fraud:
        return "Fraud analysis result not found."

    if customer_id and fraud["customer_id"] != customer_id:
        return "Authorization error: fraud information does not belong to the authenticated customer."

    return f"""
Fraud Status: {fraud["fraud_status"]}
Risk Level: {fraud["risk_level"]}
Fraud Score: {fraud["fraud_score"]}
Reason: {fraud["reason"]}
""".strip()


# ============================================================
# AI Decision
# ============================================================

@tool
def get_ai_decision(config: RunnableConfig) -> str:
    """
    Retrieve AI loan decision for the authenticated application.
    """

    application_id = _get_authenticated_application_id(config)
    customer_id = _get_authenticated_customer_id(config)

    if not application_id:
        return "Authorization error: authenticated application not found."

    decision = get_decision(application_id)

    if not decision:
        return "Loan decision not found."

    if customer_id and decision["customer_id"] != customer_id:
        return "Authorization error: loan decision does not belong to the authenticated customer."

    return f"""
Decision: {decision["decision"]}
Risk Level: {decision["risk_level"]}

Explanation:

{decision["explanation"]}
""".strip()


# ============================================================
# Register All Tools
# ============================================================

TOOLS = [
    get_customer_info,
    get_loan_info,
    get_ocr_info,
    get_kyc_info,
    get_fraud_info,
    get_ai_decision,
    search_loan_policy,
]