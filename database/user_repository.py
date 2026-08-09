from database.database import get_connection


def create_user(
    username,
    email,
    password_hash,
    role="customer",
    customer_id=None,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password_hash,
            role,
            customer_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            email,
            password_hash,
            role,
            customer_id,
        ),
    )

    conn.commit()
    conn.close()


def get_user_by_username(username):

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


def update_last_login(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET last_login = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()