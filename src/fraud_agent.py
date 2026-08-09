from database.ocr_repository import get_ocr_results
from database.loan_repository import get_loans_by_customer


def fraud_check(application_id, customer_id):

    findings = []

    risk_score = 0


    # ---------------------------------
    # OCR Document Validation
    # ---------------------------------

    ocr_results = get_ocr_results(
        application_id
    )


    for result in ocr_results:

        document_type = result["document_type"]

        confidence = result["confidence"]


        # -----------------------------
        # PAN Validation
        # -----------------------------

        if document_type == "PAN":

            missing_fields = []


            if not result["extracted_name"]:
                missing_fields.append(
                    "Name"
                )


            if not result["extracted_pan"]:
                missing_fields.append(
                    "PAN Number"
                )


            if not result["extracted_dob"]:
                missing_fields.append(
                    "DOB"
                )


            if missing_fields:

                findings.append(
                    f"Missing PAN fields: {', '.join(missing_fields)}"
                )

                risk_score += 30



        # -----------------------------
        # Aadhaar Validation
        # -----------------------------

        elif document_type == "AADHAAR":

            missing_fields = []


            if not result["extracted_name"]:
                missing_fields.append(
                    "Name"
                )


            if not result["extracted_aadhaar"]:
                missing_fields.append(
                    "Aadhaar Number"
                )


            if not result["extracted_dob"]:
                missing_fields.append(
                    "DOB"
                )


            if missing_fields:

                findings.append(
                    f"Missing Aadhaar fields: {', '.join(missing_fields)}"
                )

                risk_score += 30



        # -----------------------------
        # OCR Confidence Analysis
        # -----------------------------

        if confidence is not None:


            # Very low confidence
            if confidence < 40:

                findings.append(
                    f"Very Low OCR Confidence in {document_type} ({confidence:.2f}%)"
                )

                risk_score += 40



            # Medium confidence - only warning
            elif confidence < 55:

                # If extraction is complete, treat as warning only

                if document_type == "PAN":

                    if (
                        result["extracted_name"]
                        and result["extracted_pan"]
                        and result["extracted_dob"]
                    ):

                        findings.append(
                            f"PAN OCR confidence is low ({confidence:.2f}%) but all critical fields extracted."
                        )

                    else:

                        findings.append(
                            f"Low OCR Confidence in PAN ({confidence:.2f}%"
                    )

                    risk_score += 10


            elif document_type == "AADHAAR":

                if (
                    result["extracted_name"]
                    and result["extracted_aadhaar"]
                    and result["extracted_dob"]
                ):

                    findings.append(
                        f"Aadhaar OCR confidence is low ({confidence:.2f}%) but all critical fields extracted."
                    )

                else:

                    findings.append(
                        f"Low OCR Confidence in Aadhaar ({confidence:.2f}%"
                    )

                    risk_score += 10



    # ---------------------------------
    # Multiple Loan Application Check
    # ---------------------------------

    loans = get_loans_by_customer(
        customer_id
    )


    if len(loans) >= 3:

        findings.append(
            "Customer has multiple previous loan applications."
        )

        risk_score += 30



    # ---------------------------------
    # Final Risk Calculation
    # ---------------------------------

    if risk_score >= 70:

        risk = "HIGH"
        fraud = True


    elif risk_score >= 30:

        risk = "MEDIUM"
        fraud = True


    else:

        risk = "LOW"
        fraud = False



    # ---------------------------------
    # Default Message
    # ---------------------------------

    if not findings:

        findings.append(
            "No Fraud Detected"
        )



    return {

        "fraud": fraud,

        "risk": risk,

        "risk_score": risk_score,

        "reasons": findings

    }