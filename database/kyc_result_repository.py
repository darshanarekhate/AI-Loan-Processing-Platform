from database.database import get_connection


# -----------------------------------------
# Save KYC Result
# -----------------------------------------
def save_kyc_result(result):

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent duplicate records
    cursor.execute(
        """
        DELETE FROM kyc_results
        WHERE application_id = ?
        """,
        (
            result["application_id"],
        ),
    )

    cursor.execute(
        """
        INSERT INTO kyc_results
        (
            application_id,
            customer_id,
            name_match,
            pan_match,
            aadhaar_match,
            dob_match,
            similarity_score,
            verification_status,
            remarks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result["application_id"],
            result["customer_id"],
            result["name_match"],
            result["pan_match"],
            result["aadhaar_match"],
            result["dob_match"],
            result["similarity_score"],
            result["verification_status"],
            result["remarks"],
        ),
    )

    conn.commit()
    conn.close()


# -----------------------------------------
# Get KYC Result
# -----------------------------------------
def get_kyc_result(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM kyc_results
        WHERE application_id = ?
        """,
        (
            application_id,
        ),
    )

    result = cursor.fetchone()

    conn.close()

    return result


# -----------------------------------------
# Get KYC Status
# -----------------------------------------
def get_kyc_status(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT verification_status
        FROM kyc_results
        WHERE application_id = ?
        """,
        (
            application_id,
        ),
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result["verification_status"]

    return "NOT_COMPLETED"


# -----------------------------------------
# Delete KYC Result
# -----------------------------------------
def delete_kyc_result(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM kyc_results
        WHERE application_id = ?
        """,
        (
            application_id,
        ),
    )

    conn.commit()
    conn.close()