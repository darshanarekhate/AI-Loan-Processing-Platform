"""
Central configuration.

Every path and secret is read from the environment (or a local .env file)
so the project runs on any machine without editing source code.
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", PROJECT_ROOT / "database" / "loan_system.db")
)

UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", PROJECT_ROOT / "uploads"))
REPORT_FOLDER = Path(os.getenv("REPORT_FOLDER", PROJECT_ROOT / "reports"))

KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "Knowledge_Base"
VECTOR_DB_PATH = PROJECT_ROOT / "faiss_index"


# ============================================================
# API keys
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ============================================================
# OCR
# ============================================================

def _find_tesseract() -> str | None:
    """
    Resolve the Tesseract binary: TESSERACT_PATH env var first,
    then PATH, then the default Windows install location.
    """

    configured = os.getenv("TESSERACT_PATH")

    if configured:
        return configured

    on_path = shutil.which("tesseract")

    if on_path:
        return on_path

    windows_default = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_default.exists():
        return str(windows_default)

    return None


TESSERACT_PATH = _find_tesseract()


# ============================================================
# Uploads
# ============================================================

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
ALLOWED_UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
