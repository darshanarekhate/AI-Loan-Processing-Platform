from database.database import get_connection


def save_document(document):
    """
    Save a new document.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents
        (
            application_id,
            customer_id,
            document_type,
            file_name,
            file_path
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            document["application_id"],
            document["customer_id"],
            document["document_type"],
            document["file_name"],
            document["file_path"],
        ),
    )

    conn.commit()
    conn.close()

def document_exists(application_id, document_type):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE application_id = ?
        AND document_type = ?
        """,
        (
            application_id,
            document_type,
        ),
    )

    document = cursor.fetchone()

    conn.close()

    return document is not None


def get_documents_by_application(application_id):
    """
    Get all uploaded documents for an application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE application_id = ?
        ORDER BY upload_time
        """,
        (application_id,),
    )

    documents = cursor.fetchall()

    conn.close()

    return documents


def get_document_by_type(application_id, document_type):
    """
    Get a specific document (PAN/AADHAAR/etc.) for an application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE application_id = ?
        AND document_type = ?
        """,
        (application_id, document_type),
    )

    document = cursor.fetchone()

    conn.close()

    return document


def update_document(document):
    """
    Update an existing document instead of creating a duplicate.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET
            file_name = ?,
            file_path = ?,
            upload_time = CURRENT_TIMESTAMP
        WHERE application_id = ?
        AND document_type = ?
        """,
        (
            document["file_name"],
            document["file_path"],
            document["application_id"],
            document["document_type"],
        ),
    )

    conn.commit()
    conn.close()