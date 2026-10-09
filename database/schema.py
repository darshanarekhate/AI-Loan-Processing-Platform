from database.database import get_connection


def init_db():
    """
    Create every table and index used by the application.

    Safe to run repeatedly (CREATE ... IF NOT EXISTS).
    """

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Customers Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers(

    customer_id TEXT PRIMARY KEY,

    full_name TEXT NOT NULL,

    email TEXT,

    phone TEXT,

    pan TEXT UNIQUE,

    aadhaar TEXT UNIQUE,

    date_of_birth TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # -----------------------------
    # Loan Applications Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications(

    application_id TEXT PRIMARY KEY,

    customer_id TEXT,

    loan_type TEXT,

    loan_amount REAL,

    monthly_income REAL,

    credit_score INTEGER,

    application_status TEXT,

    risk_level TEXT,

    tenure_months INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)

    )
    """)

    # -----------------------------
    # Documents Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(

    document_id INTEGER PRIMARY KEY AUTOINCREMENT,

    application_id TEXT,

    customer_id TEXT,

    document_type TEXT,

    file_name TEXT,

    file_path TEXT,

    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(application_id)
    REFERENCES loan_applications(application_id)
    ON DELETE CASCADE,

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)
    ON DELETE CASCADE

    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ocr_results(

        ocr_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT,

        customer_id TEXT,

        document_type TEXT,

        extracted_name TEXT,

        extracted_pan TEXT,

        extracted_aadhaar TEXT,

        extracted_dob TEXT,

        confidence REAL,

        raw_text TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE,

        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE

    )
    """)

    # -----------------------------
    # Loan Decisions Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_decisions(

        decision_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT,

        customer_id TEXT,

        decision TEXT,

        risk_level TEXT,

        explanation TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE,

        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE

    )
    """)

    # -----------------------------
    # KYC Verification Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kyc_results(

        kyc_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT,

        customer_id TEXT,

        name_match INTEGER,

        pan_match INTEGER,

        aadhaar_match INTEGER,

        dob_match INTEGER,

        similarity_score REAL,

        verification_status TEXT,

        remarks TEXT,

        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE,

        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE
    )
    """)

    # -----------------------------
    # Application Stages Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS application_stages(

        stage_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT NOT NULL,

        stage_name TEXT NOT NULL,

        stage_status TEXT NOT NULL,

        remarks TEXT,

        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE

    )
    """)

    # -----------------------------
    # Users Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer',
        customer_id TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,

        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id)

    )
    """)

    # -----------------------------
    # Fraud Results Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fraud_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT UNIQUE NOT NULL,

        customer_id TEXT,

        fraud_status TEXT NOT NULL,

        risk_level TEXT NOT NULL,

        fraud_score REAL NOT NULL,

        fraud_reason TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(application_id)
        REFERENCES loan_applications(application_id)
        ON DELETE CASCADE
    )
    """)

    # Loan tenure (months) was added after the first release.
    loan_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(loan_applications)")
    }

    if "tenure_months" not in loan_columns:
        cursor.execute(
            "ALTER TABLE loan_applications ADD COLUMN tenure_months INTEGER"
        )

    # Older databases created fraud_results without customer_id.
    fraud_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(fraud_results)")
    }

    if "customer_id" not in fraud_columns:
        cursor.execute(
            "ALTER TABLE fraud_results ADD COLUMN customer_id TEXT"
        )

    # -----------------------------
    # Indexes for the hot lookups
    # -----------------------------
    for statement in [
        "CREATE INDEX IF NOT EXISTS idx_loans_customer ON loan_applications(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_documents_application ON documents(application_id)",
        "CREATE INDEX IF NOT EXISTS idx_ocr_application ON ocr_results(application_id)",
        "CREATE INDEX IF NOT EXISTS idx_kyc_application ON kyc_results(application_id)",
        "CREATE INDEX IF NOT EXISTS idx_decisions_application ON loan_decisions(application_id)",
        "CREATE INDEX IF NOT EXISTS idx_stages_application ON application_stages(application_id)",
    ]:
        cursor.execute(statement)

    conn.commit()

    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
