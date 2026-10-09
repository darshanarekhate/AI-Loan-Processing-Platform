import os
import sys
import tempfile
from pathlib import Path

# Point the app at throw-away storage BEFORE config.py is imported.
_TMP = Path(tempfile.mkdtemp(prefix="loan_tests_"))

os.environ["DATABASE_PATH"] = str(_TMP / "test.db")
os.environ["UPLOAD_FOLDER"] = str(_TMP / "uploads")
os.environ["REPORT_FOLDER"] = str(_TMP / "reports")
os.environ.pop("GROQ_API_KEY", None)
os.environ.pop("GOOGLE_API_KEY", None)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402


# Synthetic identities (Verhoeff-valid, not real people).
VALID_PAN = "ABCPE1234F"
VALID_AADHAAR = "234567890124"
OTHER_AADHAAR = "498765432102"


@pytest.fixture
def fresh_db():
    """
    Recreate an empty schema for each database test.
    """

    from config import DATABASE_PATH
    from database.schema import init_db

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    init_db()

    yield DATABASE_PATH
