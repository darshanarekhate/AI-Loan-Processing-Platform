"""
Orchestrates a loan decision for one application:

    load loan + KYC  ->  fraud screening  ->  rule engine
        ->  LLM explanation  ->  persist decision + tracker stages
"""

from database.decision_repository import save_decision
from database.kyc_result_repository import get_kyc_status
from database.loan_repository import get_loan_by_application

from services.decision_engine import evaluate_application
from services.tracker_service import fraud_completed, record_decision
from src.decision_agent import explain_decision
from src.fraud_agent import fraud_check


def run_loan_decision(application_id, customer_id):
    """
    Decide an application and store the outcome.

    Returns a dict with the DecisionResult, explanation, fraud result
    and KYC status, or {"error": ...} when the application is missing.
    """

    loan = get_loan_by_application(application_id)

    if not loan or loan["customer_id"] != customer_id:
        return {"error": "Loan application not found for this customer."}

    kyc_status = get_kyc_status(application_id)

    fraud = fraud_check(application_id, customer_id)
    fraud_completed(application_id, fraud["risk"])

    result = evaluate_application(
        loan_type=loan["loan_type"],
        loan_amount=loan["loan_amount"],
        monthly_income=loan["monthly_income"],
        credit_score=loan["credit_score"],
        kyc_status=kyc_status,
        fraud_risk=fraud["risk"],
        tenure_months=loan["tenure_months"],
    )

    explanation = explain_decision(
        result,
        loan_type=loan["loan_type"],
        loan_amount=loan["loan_amount"],
        monthly_income=loan["monthly_income"],
        credit_score=loan["credit_score"],
    )

    save_decision(
        application_id,
        customer_id,
        result.decision,
        result.risk_level,
        explanation,
    )

    record_decision(
        application_id,
        result.decision,
        result.risk_level,
        "; ".join(result.reasons),
    )

    return {
        "result": result,
        "explanation": explanation,
        "fraud": fraud,
        "kyc_status": kyc_status,
    }
