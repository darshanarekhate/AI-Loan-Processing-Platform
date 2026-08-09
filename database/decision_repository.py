from database.database import get_connection


def save_decision(
    application_id,
    customer_id,
    decision,
    risk_level,
    explanation,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO loan_decisions
        (
            application_id,
            customer_id,
            decision,
            risk_level,
            explanation
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            application_id,
            customer_id,
            decision,
            risk_level,
            explanation,
        ),
    )

    conn.commit()
    conn.close()


def get_decision(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_decisions
        WHERE application_id=?
        ORDER BY decision_id DESC
        LIMIT 1
        """,
        (application_id,),
    )

    decision = cursor.fetchone()

    conn.close()

    return decision