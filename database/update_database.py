from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# ---------------------------------------
# Application Stages
# ---------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS application_stages (

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

# ---------------------------------------
# KYC Results
# ---------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS kyc_results (

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

conn.commit()
conn.close()

print("✅ Database updated successfully.")
print("✅ application_stages table created.")
print("✅ kyc_results table created.")