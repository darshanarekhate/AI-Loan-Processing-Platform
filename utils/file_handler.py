import re
from pathlib import Path

from config import (
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_SIZE_MB,
    UPLOAD_FOLDER,
)


# Leading bytes of the file formats we accept.
_MAGIC_BYTES = {
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".pdf": [b"%PDF-"],
}

_SAFE_ID = re.compile(r"^[A-Za-z0-9-]+$")


class UploadError(ValueError):
    """Raised when an uploaded file fails validation."""


def validate_upload(file_name: str, content: bytes) -> str:
    """
    Check extension, size and file signature.

    Returns the normalised extension.
    """

    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise UploadError(f"Unsupported file type '{extension}'.")

    if len(content) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise UploadError(f"File is larger than {MAX_UPLOAD_SIZE_MB} MB.")

    if not any(content.startswith(magic) for magic in _MAGIC_BYTES[extension]):
        raise UploadError(
            "File content does not match its extension."
        )

    return extension


def save_uploaded_file(
    uploaded_file,
    customer_id,
    application_id,
    document_type,
):
    """
    Store an uploaded document as
    uploads/<customer_id>/<application_id>/<DOCUMENT_TYPE><ext>.

    The client-supplied file name is never used as a path, which
    prevents path traversal (e.g. "../../app.py").
    """

    for value in (customer_id, application_id, document_type):
        if not _SAFE_ID.match(str(value).replace("_", "-")):
            raise UploadError("Invalid identifier.")

    content = uploaded_file.getvalue()
    extension = validate_upload(uploaded_file.name, content)

    folder = Path(UPLOAD_FOLDER) / customer_id / application_id
    folder.mkdir(parents=True, exist_ok=True)

    destination = folder / f"{document_type}{extension}"

    with open(destination, "wb") as f:
        f.write(content)

    return str(destination)

