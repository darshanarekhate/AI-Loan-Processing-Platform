import sqlite3

from config import DATABASE_PATH

print(">>> NEW KYC.PY LOADED <<<")


def calculate_kyc_score(user_id):
    """
    Calculate KYC score using only the latest PAN and Aadhaar
    records for the user.
    """

    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    cursor = conn.cursor()

    # --------------------------------------------------
    # Fetch only the latest PAN and latest Aadhaar
    # --------------------------------------------------

    cursor.execute(
        """
        SELECT
            document_type,
            extracted_number,
            name,
            father_name,
            dob,
            ocr_confidence
        FROM documents
        WHERE id IN (
            SELECT MAX(id)
            FROM documents
            WHERE user_id=?
            GROUP BY document_type
        )
        """,
        (user_id,)
    )

    documents = cursor.fetchall()

    print("\n===== DOCUMENTS USED FOR KYC =====")
    for doc in documents:
        print(doc)
    print("==================================\n")

    conn.close()

    score = 0

    pan_found = False
    aadhaar_found = False

    # --------------------------------------------------
    # Calculate Score
    # --------------------------------------------------

    for (
        document_type,
        extracted_number,
        name,
        father_name,
        dob,
        confidence
    ) in documents:

        # -----------------------------
        # PAN
        # -----------------------------

        if document_type == "PAN":

            pan_found = True

            if extracted_number:
                score += 25

            if name:
                score += 15

            if father_name:
                score += 10

            if dob:
                score += 10

            if confidence is not None:

                if confidence >= 80:
                    score += 15

                elif confidence >= 60:
                    score += 10

                elif confidence >= 40:
                    score += 5

        # -----------------------------
        # Aadhaar
        # -----------------------------

        elif document_type == "AADHAAR":

            aadhaar_found = True

            if extracted_number:
                score += 15

            if name:
                score += 10

            if dob:
                score += 10

            if confidence is not None:

                if confidence >= 80:
                    score += 15

                elif confidence >= 60:
                    score += 10

                elif confidence >= 40:
                    score += 5

    # --------------------------------------------------
    # Missing Document Penalty
    # --------------------------------------------------

    if not pan_found:
        score -= 20

    if not aadhaar_found:
        score -= 20

    # --------------------------------------------------
    # Keep score between 0 and 100
    # --------------------------------------------------

    score = max(0, min(score, 100))

    # --------------------------------------------------
    # KYC Status
    # --------------------------------------------------

    if score >= 90:
        status = "Excellent"

    elif score >= 75:
        status = "Good"

    elif score >= 60:
        status = "Average"

    else:
        status = "Poor"

    print("Final KYC Score :", score)
    print("Final KYC Status:", status)

    return score, status