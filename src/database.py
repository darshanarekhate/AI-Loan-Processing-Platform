import sqlite3
from pathlib import Path

from config import DATABASE_PATH


def initialize_database():

    Path("database").mkdir(exist_ok=True)

    conn = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        mobile TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        document_type TEXT,
        document_path TEXT,
        extracted_number TEXT,
        name TEXT,
        father_name TEXT,
        dob TEXT,
        ocr_confidence REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_decisions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        loan_amount REAL,
        credit_score INTEGER,
        kyc_score INTEGER,
        decision TEXT,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")