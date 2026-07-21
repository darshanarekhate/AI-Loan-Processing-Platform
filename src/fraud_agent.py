import sqlite3

from streamlit import cursor

from config import DATABASE_PATH


def fraud_check(state):

    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    cursor = conn.cursor()

    fraud = False
    reasons = []

    # ----------------------------------------
    # Get current user's PAN number
    # ----------------------------------------

    cursor.execute(
        """
        SELECT extracted_number
        FROM documents
        WHERE user_id=?
        AND document_type='PAN'
        """,
        (state["user_id"],)
    )

    row = cursor.fetchone()

    pan = row[0] if row else None

    # ----------------------------------------
    # Duplicate PAN Check
    # ----------------------------------------

    if pan:

        cursor.execute(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM documents
            WHERE extracted_number=?
            AND user_id<>?
            """,
            (
                pan,
                state["user_id"]
            )
        )

        count = cursor.fetchone()[0]

        if count > 0:

            fraud = True

            reasons.append(
                "Duplicate PAN detected for another user."
            )

    # ----------------------------------------
    # Get current user's Aadhaar number
    # ----------------------------------------

    cursor.execute(
      """
      SELECT extracted_number
      FROM documents
      WHERE user_id=?
      AND document_type='AADHAAR'
      """,
      (state["user_id"],)
    )

    row = cursor.fetchone()

    aadhaar = row[0] if row else None

    # ----------------------------------------
    # Duplicate Aadhaar Check
    # ----------------------------------------

    if aadhaar:

        cursor.execute(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM documents
            WHERE extracted_number=?
            AND user_id<>?
            """,
            (
                aadhaar,
                state["user_id"]
            )
        )

        count = cursor.fetchone()[0]

        if count > 0:

            fraud = True

            reasons.append(
            "Duplicate Aadhaar detected for another user."
            )

    # ----------------------------------------
    # OCR Confidence Check
    # ----------------------------------------

    cursor.execute(
        """
        SELECT
        document_type,
        ocr_confidence
        FROM documents
        WHERE user_id=?
        """,
        (state["user_id"],)
    )

    rows = cursor.fetchall()

    for doc_type, confidence in rows:

        if confidence is not None and confidence < 70:

            fraud = True

            reasons.append(
                f"Low OCR confidence in {doc_type} ({confidence}%)."
            )

    conn.close()

    state["fraud"] = fraud

    if reasons:
        state["fraud_reason"] = "\n".join(reasons)
    else:
        state["fraud_reason"] = "No fraud detected."

    return state