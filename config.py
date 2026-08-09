from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Read the API key from the .env file
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Database
DATABASE_PATH = "database/loan_kyc.db"

# Folders
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

# Tesseract OCR Path
TESSERACT_PATH = r"C:\Users\Dell\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"