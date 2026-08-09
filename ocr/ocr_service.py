from src.preprocessing import preprocess_image

from src.ocr import (
    perform_ocr,
    extract_pan_details,
    extract_aadhaar_details,
)


def process_document(document_type, file_path):

    try:

        # -----------------------------
        # Image Preprocessing
        # -----------------------------

        image = preprocess_image(
            file_path,
            document_type
        )

        # -----------------------------
        # OCR
        # -----------------------------

        ocr_text, confidence = perform_ocr(
            image,
            document_type
        )

        # -----------------------------
        # Extract Required Fields
        # -----------------------------

        if document_type == "PAN":

            result = extract_pan_details(
                ocr_text
            )

        elif document_type == "AADHAAR":

            result = extract_aadhaar_details(
                ocr_text
            )

        else:

            return {
                "ERROR": "Unsupported document type"
            }

        # -----------------------------
        # Attach OCR Information
        # -----------------------------

        result["OCR_TEXT"] = ocr_text
        result["OCR_CONFIDENCE"] = round(confidence, 2)

        # -----------------------------
        # Determine OCR Status
        # -----------------------------

        status = "MANUAL_REVIEW"

        if document_type == "PAN":

            if (
                result.get("PAN")
                and result.get("NAME")
                and result.get("FATHER")
                and result.get("DOB")
            ):
                status = "SUCCESS"

        elif document_type == "AADHAAR":

            if (
                result.get("AADHAAR")
                and result.get("NAME")
                and result.get("DOB")
            ):
                status = "SUCCESS"

        # Fallback using OCR confidence
        if (
            status != "SUCCESS"
            and confidence >= 85
        ):
            status = "SUCCESS"

        result["OCR_STATUS"] = status

        # -----------------------------
        # Overall OCR Quality
        # -----------------------------

        if confidence >= 90:
            result["OCR_QUALITY"] = "Excellent"

        elif confidence >= 75:
            result["OCR_QUALITY"] = "Good"

        elif confidence >= 60:
            result["OCR_QUALITY"] = "Average"

        else:
            result["OCR_QUALITY"] = "Low"

        return result

    except Exception as ex:

        return {
            "ERROR": str(ex)
        }