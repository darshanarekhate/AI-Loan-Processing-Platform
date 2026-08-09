from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS fraud_results (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    application_id TEXT UNIQUE NOT NULL,

    fraud_status TEXT NOT NULL,

    risk_level TEXT NOT NULL,

    fraud_score REAL NOT NULL,

    fraud_reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Fraud table created successfully.")