from database.database import get_connection


# -------------------------------------------------
# Add or Update Application Stage
# -------------------------------------------------
def add_stage(application_id, stage_name, stage_status, remarks=""):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stage_id
        FROM application_stages
        WHERE application_id = ?
        AND stage_name = ?
    """, (application_id, stage_name))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE application_stages
            SET
                stage_status = ?,
                remarks = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE stage_id = ?
        """, (
            stage_status,
            remarks,
            existing[0]
        ))

    else:

        cursor.execute("""
            INSERT INTO application_stages
            (
                application_id,
                stage_name,
                stage_status,
                remarks
            )
            VALUES (?, ?, ?, ?)
        """, (
            application_id,
            stage_name,
            stage_status,
            remarks
        ))

    conn.commit()
    conn.close()


# -------------------------------------------------
# Update Loan Application Status
# -------------------------------------------------
def update_application_status(application_id, status, risk_level):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE loan_applications
        SET
            application_status = ?,
            risk_level = ?
        WHERE application_id = ?
    """, (
        status,
        risk_level,
        application_id
    ))

    conn.commit()
    conn.close()


# -------------------------------------------------
# Get Complete Application Journey
# -------------------------------------------------
def get_application_journey(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            l.application_id,
            c.full_name,
            l.loan_type,
            l.loan_amount,
            l.monthly_income,
            l.credit_score,
            l.application_status,
            l.risk_level,
            l.created_at
        FROM loan_applications l
        JOIN customers c
            ON l.customer_id = c.customer_id
        WHERE l.application_id = ?
    """, (application_id,))

    application = cursor.fetchone()

    cursor.execute("""
        SELECT
            stage_name,
            stage_status,
            remarks,
            updated_at
        FROM application_stages
        WHERE application_id = ?
        ORDER BY updated_at
    """, (application_id,))

    stages = cursor.fetchall()

    conn.close()

    return application, stages


# -------------------------------------------------
# Get All Applications
# -------------------------------------------------
def get_all_applications():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            application_id,
            customer_id,
            loan_type,
            loan_amount,
            application_status,
            risk_level,
            created_at
        FROM loan_applications
        ORDER BY created_at DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -------------------------------------------------
# Loan Submitted
# -------------------------------------------------
def loan_submitted(application_id):

    add_stage(
        application_id,
        "Loan Application",
        "COMPLETED",
        "Loan application submitted successfully."
    )


# -------------------------------------------------
# Documents Uploaded
# -------------------------------------------------
def documents_uploaded(application_id, document_list):

    add_stage(
        application_id,
        "Documents Uploaded",
        "COMPLETED",
        ", ".join(document_list)
    )


# -------------------------------------------------
# OCR
# -------------------------------------------------
def ocr_completed(application_id, confidence):

    status = "COMPLETED" if confidence >= 90 else "MANUAL_REVIEW"

    remarks = (
        f"OCR completed ({confidence:.2f}% confidence)"
        if confidence >= 90
        else f"Low OCR confidence ({confidence:.2f}%)"
    )

    add_stage(
        application_id,
        "OCR",
        status,
        remarks
    )


# -------------------------------------------------
# KYC
# -------------------------------------------------
def kyc_completed(application_id, passed):

    if passed:

        add_stage(
            application_id,
            "KYC",
            "COMPLETED",
            "Identity verified successfully."
        )

    else:

        add_stage(
            application_id,
            "KYC",
            "MANUAL_REVIEW",
            "Manual verification required."
        )


# -------------------------------------------------
# Fraud Detection
# -------------------------------------------------
def fraud_completed(application_id, risk):

    risk = risk.upper()

    mapping = {
        "LOW": ("LOW_RISK", "No suspicious activity detected."),
        "MEDIUM": ("MEDIUM_RISK", "Requires manual verification."),
        "HIGH": ("HIGH_RISK", "Potential fraud detected.")
    }

    status, remarks = mapping.get(
        risk,
        ("UNKNOWN", "Risk analysis unavailable.")
    )

    add_stage(
        application_id,
        "Fraud Detection",
        status,
        remarks
    )


# -------------------------------------------------
# AI Decision
# -------------------------------------------------
def ai_decision(application_id, decision, explanation):

    decision = decision.upper()

    if decision == "APPROVED":

        update_application_status(
            application_id,
            "APPROVED",
            "LOW"
        )

        add_stage(
            application_id,
            "AI Decision",
            "APPROVED",
            explanation
        )

    else:

        update_application_status(
            application_id,
            "REJECTED",
            "HIGH"
        )

        add_stage(
            application_id,
            "AI Decision",
            "REJECTED",
            explanation
        )