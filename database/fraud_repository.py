from database.database import get_connection


def get_fraud_result(application_id):
    """
    Retrieve fraud detection result for a loan application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            fraud_status,
            risk_level,
            fraud_score,
            fraud_reason
        FROM fraud_results
        WHERE application_id = ?
        """,
        (application_id,),
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "fraud_status": row["fraud_status"],
        "risk_level": row["risk_level"],
        "fraud_score": row["fraud_score"],
        "reason": row["fraud_reason"],
    }