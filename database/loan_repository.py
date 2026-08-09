from database.database import get_connection


def save_loan(loan):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO loan_applications
        (
            application_id,
            customer_id,
            loan_type,
            loan_amount,
            monthly_income,
            credit_score,
            application_status,
            risk_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            loan["application_id"],
            loan["customer_id"],
            loan["loan_type"],
            loan["loan_amount"],
            loan["monthly_income"],
            loan["credit_score"],
            loan["application_status"],
            loan["risk_level"],
        ),
    )

    conn.commit()
    conn.close()


def get_loan_by_application(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_applications
        WHERE application_id=?
        """,
        (application_id,),
    )

    loan = cursor.fetchone()

    conn.close()

    return loan


def get_loans_by_customer(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_applications
        WHERE customer_id=?
        ORDER BY created_at DESC
        """,
        (customer_id,),
    )

    loans = cursor.fetchall()

    conn.close()

    return loans


def update_loan_status(application_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE loan_applications
        SET application_status=?
        WHERE application_id=?
        """,
        (
            status,
            application_id,
        ),
    )

    conn.commit()
    conn.close()


def update_risk_level(application_id, risk_level):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE loan_applications
        SET risk_level=?
        WHERE application_id=?
        """,
        (
            risk_level,
            application_id,
        ),
    )

    conn.commit()
    conn.close()

def get_all_loans():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_applications
        ORDER BY created_at DESC
        """
    )

    loans = cursor.fetchall()

    conn.close()

    return loans



def get_loan_status_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            application_status,
            COUNT(*) as count
        FROM loan_applications
        GROUP BY application_status
        """
    )

    result = cursor.fetchall()

    conn.close()

    return result



def get_risk_level_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            risk_level,
            COUNT(*) as count
        FROM loan_applications
        GROUP BY risk_level
        """
    )

    result = cursor.fetchall()

    conn.close()

    return result