from database.database import get_connection

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

conn.commit()

conn.close()

print("Database initialized successfully.")