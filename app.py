from src.workflow import workflow
from src.state import LoanState
from src.llm import analyze_loan

from src.database import initialize_database
from src.auth import register_user, login_user
from src.upload import upload_document
from src.kyc import calculate_kyc_score

from src.preprocessing import preprocess_image
from src.ocr import (
    perform_ocr,
    extract_pan_details,
    save_ocr_result,
)


def main():

    print("=" * 60)
    print("AI LOAN PROCESSING SYSTEM")
    print("=" * 60)

    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    initialize_database()

    # =====================================================
    # USER REGISTRATION
    # =====================================================

    user_id = register_user(
        "Mohamed Faiz",
        33,
        "9876543210",
        "faiz@gmail.com",
        "1234"
    )

    print("User ID :", user_id)

    # =====================================================
    # LOGIN
    # =====================================================

    user = login_user(
        "faiz@gmail.com",
        "1234"
    )

    if not user:
        print("Login Failed")
        return

    print("Login Successful")

    # =====================================================
    # DOCUMENT UPLOAD
    # =====================================================

    print("\nUploading Documents...\n")

    pan_document_id, pan_path = upload_document(
        user_id,
        "PAN",
        "Pan.png"
    )

    aadhaar_document_id, aadhaar_path = upload_document(
        user_id,
        "AADHAAR",
        "aadhar.png"
    )

    # =====================================================
    # PAN OCR
    # =====================================================

    print("\n" + "=" * 60)
    print("OCR - PAN")
    print("=" * 60)

    image = preprocess_image(pan_path)

    text, confidence = perform_ocr(image)

    details = extract_pan_details(text)

    pan = details["PAN"]
    name = details["NAME"]
    father = details["FATHER"]
    dob = details["DOB"]

    save_ocr_result(
        pan_document_id,
        pan,
        confidence,
        name,
        father,
        dob
    )

    print("PAN Number :", pan)
    print("Name       :", name)
    print("Father     :", father)
    print("DOB        :", dob)
    print("Confidence :", confidence)

    # =====================================================
    # AADHAAR OCR
    # =====================================================

    print("\n" + "=" * 60)
    print("AADHAAR OCR")
    print("=" * 60)

    print("To be implemented in next phase.")

    print("\nOCR completed successfully.")

    # =====================================================
    # KYC SCORE
    # =====================================================

    print("\n" + "=" * 60)
    print("KYC SCORE")
    print("=" * 60)

    score, status = calculate_kyc_score(user_id)

    print("Score  :", score)
    print("Status :", status)

    # =====================================================
    # LANGGRAPH WORKFLOW
    # =====================================================

    print("\n" + "=" * 60)
    print("LANGGRAPH WORKFLOW")
    print("=" * 60)

    state: LoanState = {
        "user_id": user_id,
        "login": False,
        "documents_uploaded": False,
        "ocr_completed": False,
        "kyc_score": score,
        "kyc_status": status,
        "loan_status": "",
    }

        # Run LangGraph Workflow

    result = workflow.invoke(state)

    print("\n" + "=" * 60)
    print("FINAL STATE")
    print("=" * 60)

    print(result)

    # =====================================================
    # LLM LOAN ANALYSIS
    # =====================================================

    state.update(
        {
            "name": "Mohamed Faiz",
            "age": 33,
            "pan": pan,
            "aadhaar": "834688652621",
            "income": 100000,
            "loan_amount": 500000,
            "credit_score": 780,
            "decision": "",
            "explanation": "",
        }
    )

    result = analyze_loan(state)

    print("\n" + "=" * 60)
    print("LLM LOAN ANALYSIS")
    print("=" * 60)

    print("Decision    :", result["decision"])
    print("Explanation :", result["explanation"])


if __name__ == "__main__":
    main()