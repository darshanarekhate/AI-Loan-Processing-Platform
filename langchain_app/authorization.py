from database.database import get_connection


def is_authorized_for_application(
    customer_id: str,
    application_id: str,
) -> bool:
    """
    Verify that the authenticated customer owns the
    requested loan application.

    Returns:
        True  -> customer owns application
        False -> unauthorized
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM loan_applications
            WHERE application_id = ?
              AND customer_id = ?
            LIMIT 1
            """,
            (
                application_id,
                customer_id,
            ),
        )

        result = cursor.fetchone()

        return result is not None

    finally:
        conn.close()


def is_authorized_for_customer(
    customer_id: str,
) -> bool:
    """
    Verify that the authenticated customer exists.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM customers
            WHERE customer_id = ?
            LIMIT 1
            """,
            (customer_id,),
        )

        result = cursor.fetchone()

        return result is not None

    finally:
        conn.close()