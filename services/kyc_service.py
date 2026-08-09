from difflib import SequenceMatcher

from database.loan_repository import get_loan_by_application
from database.customer_repository import get_customer_by_id
from database.ocr_repository import get_ocr_results
from database.kyc_result_repository import save_kyc_result

from services.tracker_service import kyc_completed
from utils.date_utils import normalize_date


# -----------------------------------------
# Normalize Names
# -----------------------------------------
def normalize_name(name):

    if not name:
        return ""

    return " ".join(name.upper().split())


# -----------------------------------------
# Similarity
# -----------------------------------------
def calculate_similarity(name1, name2):

    return round(
        SequenceMatcher(
            None,
            normalize_name(name1),
            normalize_name(name2)
        ).ratio() * 100,
        2
    )


# -----------------------------------------
# Verify KYC
# -----------------------------------------
def verify_kyc(application_id):

    loan = get_loan_by_application(application_id)

    if not loan:

        return {
            "status": "FAILED",
            "message": "Loan Application Not Found"
        }

    customer = get_customer_by_id(
        loan["customer_id"]
    )

    if not customer:

        return {
            "status": "FAILED",
            "message": "Customer Not Found"
        }

    ocr_results = get_ocr_results(application_id)

    pan = None
    aadhaar = None

    for result in ocr_results:

        if result["document_type"] == "PAN":
            pan = result

        elif result["document_type"] == "AADHAAR":
            aadhaar = result

    if not pan or not aadhaar:

        return {
            "status": "FAILED",
            "message": "OCR Results Missing"
        }

    # -------------------------------------
    # Name Similarity
    # -------------------------------------

    similarity = max(
        calculate_similarity(
            customer["full_name"],
            pan["extracted_name"]
        ),
        calculate_similarity(
            customer["full_name"],
            aadhaar["extracted_name"]
        )
    )

    name_match = similarity >= 85

    # -------------------------------------
    # PAN Match
    # -------------------------------------

    pan_match = (
        customer["pan"].upper().strip()
        ==
        pan["extracted_pan"].upper().strip()
    )

    # -------------------------------------
    # Aadhaar Match
    # -------------------------------------

    aadhaar_match = (
        customer["aadhaar"].replace(" ", "")
        ==
        aadhaar["extracted_aadhaar"].replace(" ", "")
    )

    # -------------------------------------
    # DOB Match (Normalized)
    # -------------------------------------

    customer_dob = normalize_date(
        customer["date_of_birth"]
   )

    pan_dob = normalize_date(
        pan["extracted_dob"]
    )

    aadhaar_dob = normalize_date(
        aadhaar["extracted_dob"]
    )


    dob_match = (
        customer_dob == pan_dob
        and
        customer_dob == aadhaar_dob
    )

    # -------------------------------------
    # Verification Score
    # -------------------------------------

    score = 0

    if name_match:
        score += 25

    if pan_match:
        score += 25

    if aadhaar_match:
        score += 25

    if dob_match:
        score += 25

    # -------------------------------------
    # Status
    # -------------------------------------

    if score >= 90:

        status = "VERIFIED"

    elif score >= 70:

        status = "PARTIAL"

    else:

        status = "MANUAL_REVIEW"

    remarks = []

    if name_match:
        remarks.append("Name Matched")

    if pan_match:
        remarks.append("PAN Verified")

    if aadhaar_match:
        remarks.append("Aadhaar Verified")

    if dob_match:
        remarks.append("DOB Verified")

    if not remarks:
        remarks.append("Identity verification failed")

    # -------------------------------------
    # Save Result
    # -------------------------------------

    save_kyc_result({

        "application_id": application_id,

        "customer_id": customer["customer_id"],

        "name_match": int(name_match),

        "pan_match": int(pan_match),

        "aadhaar_match": int(aadhaar_match),

        "dob_match": int(dob_match),

        "similarity_score": similarity,

        "verification_status": status,

        "remarks": ", ".join(remarks)

    })

    # -------------------------------------
    # Update Tracker
    # -------------------------------------

    kyc_completed(
        application_id,
        passed=(status == "VERIFIED")
    )

    # -------------------------------------
    # Return
    # -------------------------------------

    return {

        "customer_name": customer["full_name"],

        "pan_name": pan["extracted_name"],

        "aadhaar_name": aadhaar["extracted_name"],

        "similarity": similarity,

        "pan_match": pan_match,

        "aadhaar_match": aadhaar_match,

        "dob_match": dob_match,

        "score": score,

        "status": status,

        "remarks": remarks

    }