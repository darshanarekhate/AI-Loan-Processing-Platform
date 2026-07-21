import sqlite3
import shutil
from pathlib import Path

from config import DATABASE_PATH, UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}


def get_connection():
    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


def upload_document(user_id, document_type, source_path):

    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(source_path)

    extension = source.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise Exception("Unsupported file type.")

    upload_dir = Path(UPLOAD_FOLDER)
    upload_dir.mkdir(exist_ok=True)

    destination = upload_dir / f"{user_id}_{document_type}{extension}"

    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------------------------------
    # Check if this user already uploaded
    # this document type
    # ---------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE user_id=?
        AND document_type=?
        """,
        (
            user_id,
            document_type
        )
    )

    existing = cursor.fetchone()

    if existing:

        document_id = existing[0]

        cursor.execute(
            """
            UPDATE documents
            SET document_path=?,
                extracted_number=NULL,
                name=NULL,
                father_name=NULL,
                dob=NULL,
                ocr_confidence=NULL
            WHERE id=?
            """,
            (
                str(destination),
                document_id
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO documents
            (
                user_id,
                document_type,
                document_path
            )
            VALUES (?,?,?)
            """,
            (
                user_id,
                document_type,
                str(destination)
            )
        )

        document_id = cursor.lastrowid

    conn.commit()
    conn.close()

    print(f"{document_type} uploaded successfully.")

    return document_id, str(destination)