from database.database import get_connection


def save_fraud_result(
    application_id,
    customer_id,
    fraud_status,
    risk_level,
    fraud_score,
    fraud_reason,
):
    """
    Insert or replace the fraud result for a loan application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO fraud_results
        (
            application_id,
            customer_id,
            fraud_status,
            risk_level,
            fraud_score,
            fraud_reason
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(application_id) DO UPDATE SET
            customer_id = excluded.customer_id,
            fraud_status = excluded.fraud_status,
            risk_level = excluded.risk_level,
            fraud_score = excluded.fraud_score,
            fraud_reason = excluded.fraud_reason,
            created_at = CURRENT_TIMESTAMP
        """,
        (
            application_id,
            customer_id,
            fraud_status,
            risk_level,
            fraud_score,
            fraud_reason,
        ),
    )

    conn.commit()
    conn.close()


def get_fraud_result(application_id):
    """
    Retrieve fraud detection result for a loan application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            customer_id,
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
        "customer_id": row["customer_id"],
        "fraud_status": row["fraud_status"],
        "risk_level": row["risk_level"],
        "fraud_score": row["fraud_score"],
        "reason": row["fraud_reason"],
    }
