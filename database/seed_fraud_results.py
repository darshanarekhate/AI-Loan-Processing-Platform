from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Remove existing records (optional, useful while testing)
cursor.execute("DELETE FROM fraud_results")

# Get all application IDs
applications = cursor.execute("""
SELECT application_id
FROM loan_applications
""").fetchall()

for row in applications:

    application_id = row["application_id"]

    cursor.execute("""
    INSERT INTO fraud_results (
        application_id,
        fraud_status,
        risk_level,
        fraud_score,
        fraud_reason
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        application_id,
        "NO_FRAUD",
        "LOW",
        8.5,
        "No suspicious activity detected."
    ))

conn.commit()
conn.close()

print("Fraud results inserted successfully.")