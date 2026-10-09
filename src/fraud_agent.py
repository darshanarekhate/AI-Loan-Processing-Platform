"""
Rule-based fraud screening.

evaluate_fraud() is a pure function (unit-tested); fraud_check() loads
the data from the database, runs the rules and persists the result so
the AI Loan Assistant reports real findings.
"""

from database.customer_repository import get_customer_by_id
from database.fraud_repository import save_fraud_result
from database.loan_repository import (
    get_loan_by_application,
    get_loans_by_customer,
)
from database.ocr_repository import get_ocr_results

from utils.date_utils import normalize_date
from utils.name_utils import name_similarity
from utils.validators import (
    is_valid_aadhaar,
    is_valid_pan,
    normalize_aadhaar,
    normalize_pan,
)


HIGH_RISK_SCORE = 70
MEDIUM_RISK_SCORE = 30

FRAUD_STATUS_BY_RISK = {
    "HIGH": "SUSPECTED_FRAUD",
    "MEDIUM": "REVIEW_REQUIRED",
    "LOW": "NO_FRAUD",
}

_NOT_FOUND = {"", "NOT FOUND", "NONE"}


def _value(row, key):
    try:
        value = row[key]
    except (KeyError, IndexError):
        return None

    if value is None or str(value).strip().upper() in _NOT_FOUND:
        return None

    return value


def evaluate_fraud(
    ocr_results,
    customer=None,
    loan=None,
    previous_application_count=0,
):
    """
    Score fraud risk from OCR output, the registered customer profile
    and the loan request.

    Returns {"fraud", "risk", "risk_score", "reasons"}.
    """

    findings = []
    risk_score = 0

    pan_doc = None
    aadhaar_doc = None

    for result in ocr_results:

        document_type = result["document_type"]

        if document_type == "PAN":
            pan_doc = result
            required = {
                "Name": "extracted_name",
                "PAN Number": "extracted_pan",
                "DOB": "extracted_dob",
            }
        elif document_type == "AADHAAR":
            aadhaar_doc = result
            required = {
                "Name": "extracted_name",
                "Aadhaar Number": "extracted_aadhaar",
                "DOB": "extracted_dob",
            }
        else:
            continue

        # ---------------- Missing fields ----------------
        missing = [
            label
            for label, key in required.items()
            if not _value(result, key)
        ]

        if missing:
            findings.append(
                f"Missing {document_type} fields: {', '.join(missing)}"
            )
            risk_score += 30

        # ---------------- OCR confidence ----------------
        confidence = _value(result, "confidence")

        if confidence is not None:

            if confidence < 40:
                findings.append(
                    f"Very low OCR confidence in {document_type} "
                    f"({confidence:.2f}%) - possible tampered or unclear image."
                )
                risk_score += 40

            elif confidence < 55:
                if missing:
                    findings.append(
                        f"Low OCR confidence in {document_type} ({confidence:.2f}%)."
                    )
                    risk_score += 10
                else:
                    findings.append(
                        f"{document_type} OCR confidence is low ({confidence:.2f}%) "
                        "but all critical fields were extracted."
                    )

    # ---------------- Document number integrity ----------------
    extracted_pan = _value(pan_doc, "extracted_pan") if pan_doc else None
    extracted_aadhaar = _value(aadhaar_doc, "extracted_aadhaar") if aadhaar_doc else None

    if extracted_pan and not is_valid_pan(extracted_pan):
        findings.append(f"Extracted PAN '{extracted_pan}' has an invalid format.")
        risk_score += 20

    if extracted_aadhaar and not is_valid_aadhaar(extracted_aadhaar):
        findings.append(
            "Extracted Aadhaar number fails the UIDAI Verhoeff checksum."
        )
        risk_score += 25

    # ---------------- Documents vs registered profile ----------------
    if customer:

        if extracted_pan and normalize_pan(extracted_pan) != normalize_pan(customer["pan"]):
            findings.append("PAN on the document does not match the registered PAN.")
            risk_score += 40

        if extracted_aadhaar and (
            normalize_aadhaar(extracted_aadhaar) != normalize_aadhaar(customer["aadhaar"])
        ):
            findings.append(
                "Aadhaar on the document does not match the registered Aadhaar."
            )
            risk_score += 40

    # ---------------- Cross-document consistency ----------------
    if pan_doc and aadhaar_doc:

        pan_name = _value(pan_doc, "extracted_name")
        aadhaar_name = _value(aadhaar_doc, "extracted_name")

        if pan_name and aadhaar_name and name_similarity(pan_name, aadhaar_name) < 70:
            findings.append(
                f"Name differs between PAN ('{pan_name}') and Aadhaar ('{aadhaar_name}')."
            )
            risk_score += 20

        pan_dob = _value(pan_doc, "extracted_dob")
        aadhaar_dob = _value(aadhaar_doc, "extracted_dob")

        if pan_dob and aadhaar_dob and normalize_date(pan_dob) != normalize_date(aadhaar_dob):
            findings.append("Date of birth differs between PAN and Aadhaar.")
            risk_score += 20

    # ---------------- Application behaviour ----------------
    if previous_application_count >= 3:
        findings.append(
            f"Customer has {previous_application_count} other loan applications."
        )
        risk_score += 30

    if loan:
        annual_income = (loan["monthly_income"] or 0) * 12

        if annual_income and loan["loan_amount"] > annual_income * 10:
            findings.append(
                "Requested amount is more than 10x annual income."
            )
            risk_score += 15

    # ---------------- Final risk ----------------
    if risk_score >= HIGH_RISK_SCORE:
        risk = "HIGH"
    elif risk_score >= MEDIUM_RISK_SCORE:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    if not findings:
        findings.append("No fraud indicators detected.")

    return {
        # Only HIGH risk is treated as suspected fraud; MEDIUM goes
        # to an officer for review.
        "fraud": risk == "HIGH",
        "risk": risk,
        "risk_score": risk_score,
        "reasons": findings,
    }


def fraud_check(application_id, customer_id, persist=True):
    """
    Load application data, run fraud rules and store the outcome.
    """

    ocr_results = get_ocr_results(application_id)
    customer = get_customer_by_id(customer_id)
    loan = get_loan_by_application(application_id)

    other_applications = [
        row
        for row in get_loans_by_customer(customer_id)
        if row["application_id"] != application_id
    ]

    result = evaluate_fraud(
        ocr_results,
        customer=customer,
        loan=loan,
        previous_application_count=len(other_applications),
    )

    if persist:
        save_fraud_result(
            application_id=application_id,
            customer_id=customer_id,
            fraud_status=FRAUD_STATUS_BY_RISK[result["risk"]],
            risk_level=result["risk"],
            fraud_score=result["risk_score"],
            fraud_reason="; ".join(result["reasons"]),
        )

    return result
