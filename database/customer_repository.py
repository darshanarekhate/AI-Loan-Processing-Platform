from database.database import get_connection


def save_customer(customer):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO customers
        (
            customer_id,
            full_name,
            email,
            phone,
            pan,
            aadhaar,
            date_of_birth
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            customer["customer_id"],
            customer["full_name"],
            customer["email"],
            customer["phone"],
            customer["pan"],
            customer["aadhaar"],
            customer["date_of_birth"],
        ),
    )

    conn.commit()
    conn.close()


def get_customer_by_pan(pan):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE pan = ?",
        (pan,),
    )

    customer = cursor.fetchone()

    conn.close()

    return customer


def get_customer_by_id(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id=?
        """,
        (customer_id,),
    )

    customer = cursor.fetchone()

    conn.close()

    return customer

def get_customer_by_aadhaar(aadhaar):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE aadhaar = ?",
        (aadhaar,),
    )

    customer = cursor.fetchone()

    conn.close()

    return customer