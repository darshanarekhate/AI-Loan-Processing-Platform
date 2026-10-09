"""
End-to-end test of the non-LLM workflow on a temporary SQLite DB:
registration -> application -> OCR rows -> KYC -> fraud -> decision.
"""

from database.customer_repository import save_customer
from database.fraud_repository import get_fraud_result
from database.kyc_result_repository import get_kyc_status
from database.loan_repository import get_loan_by_application, save_loan
from database.ocr_repository import save_ocr_result
from services.decision_engine import APPROVED, evaluate_application
from services.kyc_service import verify_kyc
from services.tracker_service import get_application_journey, record_decision
from src.fraud_agent import fraud_check
from tests.conftest import VALID_AADHAAR, VALID_PAN


CUSTOMER_ID = "CUST-TEST0001"
APPLICATION_ID = "APP-TEST0001"


def seed(pan_number=VALID_PAN):
    save_customer({
        "customer_id": CUSTOMER_ID,
        "full_name": "Ravi Kumar",
        "email": "ravi@example.com",
        "phone": "9876543210",
        "pan": VALID_PAN,
        "aadhaar": VALID_AADHAAR,
        "date_of_birth": "1990-01-01",
    })

    save_loan({
        "application_id": APPLICATION_ID,
        "customer_id": CUSTOMER_ID,
        "loan_type": "Car Loan",
        "loan_amount": 500_000,
        "monthly_income": 80_000,
        "credit_score": 790,
        "application_status": "NEW",
        "risk_level": "PENDING",
        "tenure_months": 60,
    })

    for document_type, number in (("PAN", pan_number), ("AADHAAR", VALID_AADHAAR)):
        save_ocr_result({
            "application_id": APPLICATION_ID,
            "customer_id": CUSTOMER_ID,
            "document_type": document_type,
            "extracted_name": "RAVI KUMAR",
            "extracted_number": number,
            "extracted_dob": "01/01/1990",
            "confidence": 88.0,
        })


def test_full_workflow_approves_clean_application(fresh_db):
    seed()

    kyc = verify_kyc(APPLICATION_ID)
    assert kyc["status"] == "VERIFIED"
    assert get_kyc_status(APPLICATION_ID) == "VERIFIED"

    fraud = fraud_check(APPLICATION_ID, CUSTOMER_ID)
    assert fraud["risk"] == "LOW"

    stored = get_fraud_result(APPLICATION_ID)
    assert stored["risk_level"] == "LOW"
    assert stored["customer_id"] == CUSTOMER_ID

    loan = get_loan_by_application(APPLICATION_ID)
    assert loan["tenure_months"] == 60

    result = evaluate_application(
        loan_type=loan["loan_type"],
        loan_amount=loan["loan_amount"],
        monthly_income=loan["monthly_income"],
        credit_score=loan["credit_score"],
        kyc_status=get_kyc_status(APPLICATION_ID),
        fraud_risk=fraud["risk"],
        tenure_months=loan["tenure_months"],
    )
    assert result.decision == APPROVED

    record_decision(APPLICATION_ID, result.decision, result.risk_level, "ok")

    application, stages = get_application_journey(APPLICATION_ID)
    assert application["application_status"] == APPROVED
    assert "AI Decision" in [stage["stage_name"] for stage in stages]


def test_kyc_handles_missing_ocr_number_without_crashing(fresh_db):
    # Regression: verify_kyc used to raise AttributeError on None.upper()
    seed(pan_number=None)

    kyc = verify_kyc(APPLICATION_ID)

    assert kyc["pan_match"] is False
    assert kyc["status"] == "PARTIAL"


def test_fraud_result_is_upserted(fresh_db):
    seed()

    fraud_check(APPLICATION_ID, CUSTOMER_ID)
    fraud_check(APPLICATION_ID, CUSTOMER_ID)

    assert get_fraud_result(APPLICATION_ID)["risk_level"] == "LOW"
