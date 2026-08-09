from database.database import get_connection


def get_user_by_username(username):
    """
    Get authenticated user by username.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,),
    )

    user = cursor.fetchone()

    conn.close()

    return user


def get_applications_by_customer_id(customer_id):
    """
    Return all loan applications belonging to the customer.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_applications
        WHERE customer_id = ?
        ORDER BY created_at DESC
        """,
        (customer_id,),
    )

    applications = cursor.fetchall()

    conn.close()

    return applications


def get_application_for_customer(
    application_id,
    customer_id,
):
    """
    Authorization check.

    Returns the application only when the application
    belongs to the authenticated customer.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM loan_applications
        WHERE application_id = ?
        AND customer_id = ?
        """,
        (
            application_id,
            customer_id,
        ),
    )

    application = cursor.fetchone()

    conn.close()

    return application


def is_application_authorized(
    application_id,
    customer_id,
):
    """
    Returns True when the application belongs
    to the authenticated customer.
    """

    application = get_application_for_customer(
        application_id=application_id,
        customer_id=customer_id,
    )

    return application is not None