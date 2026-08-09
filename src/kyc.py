def verify_kyc(ocr_results):

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
            "reason": "Missing PAN or Aadhaar OCR results"
        }

    name_match = (
        pan["extracted_name"].strip().upper()
        ==
        aadhaar["extracted_name"].strip().upper()
    )

    dob_match = (
        pan["extracted_dob"]
        ==
        aadhaar["extracted_dob"]
    )

    return {
        "pan_name": pan["extracted_name"],
        "aadhaar_name": aadhaar["extracted_name"],
        "pan_dob": pan["extracted_dob"],
        "aadhaar_dob": aadhaar["extracted_dob"],
        "name_match": name_match,
        "dob_match": dob_match,
        "status": "PASSED" if (name_match and dob_match) else "MANUAL REVIEW",
    }