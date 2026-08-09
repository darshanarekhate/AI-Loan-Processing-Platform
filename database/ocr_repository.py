from database.database import get_connection


def save_ocr_result(result):

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent duplicate OCR records
    cursor.execute(
        """
        DELETE FROM ocr_results
        WHERE application_id = ?
        AND document_type = ?
        """,
        (
            result["application_id"],
            result["document_type"],
        ),
    )

    if result["document_type"] == "PAN":

        cursor.execute(
            """
            INSERT INTO ocr_results
            (
                application_id,
                customer_id,
                document_type,
                extracted_name,
                extracted_pan,
                extracted_aadhaar,
                extracted_dob,
                confidence,
                raw_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["application_id"],
                result["customer_id"],
                "PAN",
                result["extracted_name"],
                result["extracted_number"],
                None,
                result["extracted_dob"],
                result["confidence"],
                "",
            ),
        )

    elif result["document_type"] == "AADHAAR":

        cursor.execute(
            """
            INSERT INTO ocr_results
            (
                application_id,
                customer_id,
                document_type,
                extracted_name,
                extracted_pan,
                extracted_aadhaar,
                extracted_dob,
                confidence,
                raw_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["application_id"],
                result["customer_id"],
                "AADHAAR",
                result["extracted_name"],
                None,
                result["extracted_number"],
                result["extracted_dob"],
                result["confidence"],
                "",
            ),
        )

    conn.commit()
    conn.close()


def get_ocr_results(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM ocr_results
        WHERE application_id = ?
        ORDER BY document_type
        """,
        (application_id,),
    )

    results = cursor.fetchall()

    conn.close()

    return results