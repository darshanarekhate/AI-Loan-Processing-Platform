import sqlite3

from config import DATABASE_PATH


def review_check(state):

    print("=" * 60)
    print("MANUAL REVIEW")
    print("=" * 60)

    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    cursor = conn.cursor()

    manual_review = False
    reasons = []

    cursor.execute(
        """
        SELECT
            document_type,
            ocr_confidence,
            name,
            dob
        FROM documents
        WHERE user_id=?
        """,
        (state["user_id"],)
    )

    documents = cursor.fetchall()

    conn.close()

    for doc in documents:

        document_type = doc[0]
        confidence = doc[1]
        name = doc[2]
        dob = doc[3]

        if confidence is not None and confidence < 60:

            manual_review = True

            reasons.append(
                f"{document_type} OCR confidence below 60%."
            )

        if not name:

            manual_review = True

            reasons.append(
                f"{document_type} name missing."
            )

        if document_type == "AADHAAR" and not dob:

            manual_review = True

            reasons.append(
                "AADHAAR DOB missing."
            )

    state["manual_review"] = manual_review

    if reasons:

        state["review_reason"] = "\n".join(reasons)

    else:

        state["review_reason"] = "No manual review required."

    print("Manual Review :", state["manual_review"])
    print("Reason :", state["review_reason"])

    return state