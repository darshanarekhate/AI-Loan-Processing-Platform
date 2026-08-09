from database.database import get_connection


def get_customer_loan_history(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            application_id,
            loan_type,
            loan_amount,
            monthly_income,
            credit_score,
            application_status,
            risk_level,
            created_at
        FROM loan_applications
        WHERE customer_id=?
        ORDER BY created_at DESC
        """,
        (customer_id,),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows