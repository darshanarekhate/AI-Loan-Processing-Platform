from src.fraud_agent import evaluate_fraud
from tests.conftest import OTHER_AADHAAR, VALID_AADHAAR, VALID_PAN


CUSTOMER = {"pan": VALID_PAN, "aadhaar": VALID_AADHAAR}


def pan_doc(**overrides):
    row = {
        "document_type": "PAN",
        "extracted_name": "RAVI KUMAR",
        "extracted_pan": VALID_PAN,
        "extracted_aadhaar": None,
        "extracted_dob": "01/01/1990",
        "confidence": 85.0,
    }
    row.update(overrides)
    return row


def aadhaar_doc(**overrides):
    row = {
        "document_type": "AADHAAR",
        "extracted_name": "Ravi Kumar",
        "extracted_pan": None,
        "extracted_aadhaar": VALID_AADHAAR,
        "extracted_dob": "01/01/1990",
        "confidence": 80.0,
    }
    row.update(overrides)
    return row


def test_clean_documents_are_low_risk():
    result = evaluate_fraud([pan_doc(), aadhaar_doc()], customer=CUSTOMER)

    assert result["risk"] == "LOW"
    assert result["fraud"] is False
    assert result["risk_score"] == 0


def test_high_confidence_aadhaar_is_not_flagged():
    # Regression: the original code flagged Aadhaar as "low confidence"
    # whenever confidence was >= 55 because of an indentation bug.
    result = evaluate_fraud([aadhaar_doc(confidence=95.0)], customer=CUSTOMER)

    assert not any("confidence" in reason.lower() for reason in result["reasons"])


def test_missing_fields_and_low_confidence_raise_risk():
    result = evaluate_fraud(
        [pan_doc(extracted_pan=None, confidence=30.0), aadhaar_doc()],
        customer=CUSTOMER,
    )

    assert result["risk"] == "HIGH"
    assert result["fraud"] is True


def test_not_found_placeholder_counts_as_missing():
    result = evaluate_fraud([aadhaar_doc(extracted_name="Not Found")])

    assert any("Missing AADHAAR fields: Name" in r for r in result["reasons"])


def test_document_number_mismatch_with_profile():
    result = evaluate_fraud(
        [pan_doc(), aadhaar_doc(extracted_aadhaar=OTHER_AADHAAR)],
        customer=CUSTOMER,
    )

    assert result["risk"] in ("MEDIUM", "HIGH")
    assert any("does not match the registered Aadhaar" in r for r in result["reasons"])


def test_invalid_aadhaar_checksum_is_flagged():
    result = evaluate_fraud([aadhaar_doc(extracted_aadhaar="234567890123")])

    assert any("Verhoeff" in r for r in result["reasons"])


def test_cross_document_name_and_dob_mismatch():
    result = evaluate_fraud(
        [pan_doc(), aadhaar_doc(extracted_name="Suresh Iyer", extracted_dob="05/06/1985")],
        customer=CUSTOMER,
    )

    reasons = " ".join(result["reasons"])
    assert "Name differs" in reasons
    assert "Date of birth differs" in reasons


def test_medium_risk_is_not_labelled_fraud():
    result = evaluate_fraud(
        [pan_doc(), aadhaar_doc()],
        customer=CUSTOMER,
        previous_application_count=3,
    )

    assert result["risk"] == "MEDIUM"
    assert result["fraud"] is False


def test_loan_far_above_income_is_flagged():
    loan = {"monthly_income": 20_000, "loan_amount": 5_000_000}

    result = evaluate_fraud([pan_doc(), aadhaar_doc()], customer=CUSTOMER, loan=loan)

    assert any("10x annual income" in r for r in result["reasons"])
