import sqlite3
import uuid

from config import DATABASE_PATH


def get_connection():
    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


def generate_user_id():
    return "USR" + str(uuid.uuid4().int)[:6]


def register_user(name, age, mobile, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    # Check whether email already exists
    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        print("User already exists.")
        return existing[0]

    user_id = generate_user_id()

    cursor.execute(
        """
        INSERT INTO users
        VALUES (?,?,?,?,?,?)
        """,
        (
            user_id,
            name,
            age,
            mobile,
            email,
            password
        )
    )

    conn.commit()
    conn.close()

    return user_id


def login_user(email, password):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, name
        FROM users
        WHERE email=? AND password=?
        """,
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user