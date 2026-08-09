from enum import Enum


class QuestionType(str, Enum):
    CUSTOMER = "customer"
    LOAN = "loan"
    KYC = "kyc"
    FRAUD = "fraud"
    DECISION = "decision"
    OCR = "ocr"
    POLICY = "policy"
    GENERAL = "general"


def classify_question(question: str) -> QuestionType:
    """
    Classify common loan-assistant questions without using an LLM.

    This deterministic router is intentionally simple and predictable.
    Customer/application-specific queries should not consume Gemini quota.
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # Customer information
    # ---------------------------------------------------------

    customer_keywords = [
        "customer information",
        "customer details",
        "customer profile",
        "my profile",
        "my details",
        "my name",
        "my email",
        "my phone",
        "my pan",
        "my aadhaar",
        "my address",
        "date of birth",
        "dob",
    ]

    if any(keyword in q for keyword in customer_keywords):
        return QuestionType.CUSTOMER

    # ---------------------------------------------------------
    # KYC
    # ---------------------------------------------------------

    kyc_keywords = [
        "kyc",
        "kyc status",
        "kyc verification",
        "identity verification",
        "identity verified",
        "pan verification",
        "aadhaar verification",
        "verification status",
        "is my identity verified",
    ]

    if any(keyword in q for keyword in kyc_keywords):
        return QuestionType.KYC

    # ---------------------------------------------------------
    # Fraud
    # ---------------------------------------------------------

    fraud_keywords = [
        "fraud",
        "fraud status",
        "fraud score",
        "fraud risk",
        "fraud detection",
        "fraud analysis",
        "suspicious activity",
    ]

    if any(keyword in q for keyword in fraud_keywords):
        return QuestionType.FRAUD

    # ---------------------------------------------------------
    # AI loan decision
    # ---------------------------------------------------------

    decision_keywords = [
        "why was my loan approved",
        "why was my loan rejected",
        "why is my loan approved",
        "why is my loan rejected",
        "approval reason",
        "rejection reason",
        "loan decision",
        "ai decision",
        "decision reason",
        "why approved",
        "why rejected",
    ]

    if any(keyword in q for keyword in decision_keywords):
        return QuestionType.DECISION

    # ---------------------------------------------------------
    # OCR
    # ---------------------------------------------------------

    ocr_keywords = [
        "ocr",
        "ocr result",
        "ocr results",
        "extracted document",
        "extracted data",
        "document extraction",
        "scanned document",
        "what was extracted",
    ]

    if any(keyword in q for keyword in ocr_keywords):
        return QuestionType.OCR

    # ---------------------------------------------------------
    # Loan information
    # ---------------------------------------------------------

    loan_keywords = [
        "loan amount",
        "loan type",
        "loan status",
        "loan application",
        "application status",
        "credit score",
        "monthly income",
        "risk level",
        "my loan",
        "complete loan details",
        "loan details",
    ]

    if any(keyword in q for keyword in loan_keywords):
        return QuestionType.LOAN

    # ---------------------------------------------------------
    # General loan policy
    # ---------------------------------------------------------

    policy_keywords = [
        "eligibility",
        "eligible",
        "interest rate",
        "interest rates",
        "emi",
        "tenure",
        "loan tenure",
        "down payment",
        "ltv",
        "loan to value",
        "required documents",
        "documents required",
        "loan requirements",
        "minimum income",
        "car loan eligibility",
        "home loan eligibility",
        "personal loan eligibility",
    ]

    if any(keyword in q for keyword in policy_keywords):
        return QuestionType.POLICY

    # ---------------------------------------------------------
    # Default
    # ---------------------------------------------------------

    return QuestionType.GENERAL