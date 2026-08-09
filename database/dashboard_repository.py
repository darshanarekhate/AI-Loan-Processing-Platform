from database.database import get_connection


def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    # Total applications
    cursor.execute("SELECT COUNT(*) FROM loan_applications")
    total = cursor.fetchone()[0]

    # Approved
    cursor.execute("""
        SELECT COUNT(*)
        FROM loan_applications
        WHERE application_status='APPROVED'
    """)
    approved = cursor.fetchone()[0]

    # Rejected
    cursor.execute("""
        SELECT COUNT(*)
        FROM loan_applications
        WHERE application_status='REJECTED'
    """)
    rejected = cursor.fetchone()[0]

    # Manual Review
    cursor.execute("""
        SELECT COUNT(*)
        FROM loan_applications
        WHERE application_status='MANUAL REVIEW'
    """)
    manual_review = cursor.fetchone()[0]

    # Fraud
    cursor.execute("""
        SELECT COUNT(*)
        FROM loan_applications
        WHERE risk_level='HIGH'
    """)
    fraud = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "manual_review": manual_review,
        "fraud": fraud,
    }


def get_recent_applications(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            application_id,
            customer_id,
            loan_type,
            loan_amount,
            application_status,
            created_at
        FROM loan_applications
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows