import sqlite3

from rapidfuzz import fuzz

from config import DATABASE_PATH


def name_match_node(state):

    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    cursor = conn.cursor()

    # Get registered user name
    cursor.execute(
        """
        SELECT name
        FROM users
        WHERE user_id=?
        """,
        (state["user_id"],)
    )

    row = cursor.fetchone()

    registered_name = row[0] if row else ""

    # Get PAN name
    cursor.execute(
        """
        SELECT name
        FROM documents
        WHERE user_id=?
        AND document_type='PAN'
        """
        ,
        (state["user_id"],)
    )

    row = cursor.fetchone()

    pan_name = row[0] if row else ""

    # Get Aadhaar name
    cursor.execute(
        """
        SELECT name
        FROM documents
        WHERE user_id=?
        AND document_type='AADHAAR'
        """,
        (state["user_id"],)
    )

    row = cursor.fetchone()

    aadhaar_name = row[0] if row else ""

    conn.close()

    # Compare names
    pan_score = fuzz.ratio(
        registered_name.upper(),
        pan_name.upper()
    ) if pan_name else 0

    aadhaar_score = fuzz.ratio(
        registered_name.upper(),
        aadhaar_name.upper()
    ) if aadhaar_name else 0

    overall_score = max(pan_score, aadhaar_score)

    state["registered_name"] = registered_name
    state["pan_name"] = pan_name
    state["aadhaar_name"] = aadhaar_name
    state["name_match_score"] = overall_score

    if overall_score >= 90:
        state["name_match"] = True
    else:
        state["name_match"] = False
        state["fraud"] = True

        if state["fraud_reason"]:
            state["fraud_reason"] += "\n"

        state["fraud_reason"] += "Name mismatch detected."

    return state