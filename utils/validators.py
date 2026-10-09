import re
from datetime import date

from database.customer_repository import (
    get_customer_by_pan,
    get_customer_by_aadhaar,
)


# ============================================================
# Format rules
# ============================================================

# PAN: 5 letters, 4 digits, 1 letter. The 4th letter encodes the
# holder type (P = individual, C = company, H = HUF, ...).
PAN_PATTERN = re.compile(r"^[A-Z]{3}[ABCEFGHLJPT][A-Z][0-9]{4}[A-Z]$")

# Indian mobile numbers: 10 digits starting with 6-9,
# optionally prefixed with +91 / 91 / 0.
PHONE_PATTERN = re.compile(r"^(?:\+?91|0)?[6-9]\d{9}$")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

MIN_APPLICANT_AGE = 18


# ============================================================
# Verhoeff checksum (used by UIDAI for Aadhaar numbers)
# ============================================================

_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def verhoeff_is_valid(number: str) -> bool:
    """
    Return True when the trailing digit is a valid Verhoeff check digit.

    Catches every single-digit typo and every adjacent transposition,
    which is exactly the kind of error OCR and manual entry produce.
    """

    if not number.isdigit():
        return False

    checksum = 0

    for position, digit in enumerate(reversed(number)):
        checksum = _VERHOEFF_D[checksum][
            _VERHOEFF_P[position % 8][int(digit)]
        ]

    return checksum == 0


# ============================================================
# Normalisers
# ============================================================

def normalize_pan(pan: str | None) -> str:
    return (pan or "").strip().upper().replace(" ", "")


def normalize_aadhaar(aadhaar: str | None) -> str:
    return re.sub(r"[\s-]", "", aadhaar or "")


def normalize_phone(phone: str | None) -> str:
    return re.sub(r"[\s-]", "", phone or "")


# ============================================================
# Field validators
# ============================================================

def is_valid_pan(pan: str | None) -> bool:
    return bool(PAN_PATTERN.match(normalize_pan(pan)))


def is_valid_aadhaar(aadhaar: str | None) -> bool:
    value = normalize_aadhaar(aadhaar)

    # Aadhaar numbers are 12 digits and never start with 0 or 1.
    if not re.fullmatch(r"[2-9]\d{11}", value):
        return False

    return verhoeff_is_valid(value)


def is_valid_phone(phone: str | None) -> bool:
    return bool(PHONE_PATTERN.match(normalize_phone(phone)))


def is_valid_email(email: str | None) -> bool:
    return bool(EMAIL_PATTERN.match((email or "").strip()))


def calculate_age(date_of_birth: date, today: date | None = None) -> int:
    today = today or date.today()

    return (
        today.year
        - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )


# ============================================================
# Registration
# ============================================================

def validate_registration_fields(
    full_name,
    phone,
    pan,
    aadhaar,
    email="",
    date_of_birth=None,
):
    """
    Pure format validation (no database access).

    Returns (is_valid, error_message).
    """

    if not (full_name or "").strip():
        return False, "Full Name is required."

    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,99}", full_name.strip()):
        return False, "Full Name may only contain letters, spaces, dots, apostrophes and hyphens."

    if not (phone or "").strip():
        return False, "Phone Number is required."

    if not is_valid_phone(phone):
        return False, "Enter a valid 10-digit Indian mobile number."

    if email and not is_valid_email(email):
        return False, "Enter a valid email address."

    if not (pan or "").strip():
        return False, "PAN Number is required."

    if not is_valid_pan(pan):
        return False, "Invalid PAN format. Expected e.g. ABCPE1234F."

    if not (aadhaar or "").strip():
        return False, "Aadhaar Number is required."

    if not is_valid_aadhaar(aadhaar):
        return False, "Invalid Aadhaar number (failed 12-digit / checksum validation)."

    if date_of_birth and calculate_age(date_of_birth) < MIN_APPLICANT_AGE:
        return False, f"Applicant must be at least {MIN_APPLICANT_AGE} years old."

    return True, ""


def validate_customer_registration(
    full_name,
    phone,
    pan,
    aadhaar,
    email="",
    date_of_birth=None,
):
    valid, message = validate_registration_fields(
        full_name,
        phone,
        pan,
        aadhaar,
        email=email,
        date_of_birth=date_of_birth,
    )

    if not valid:
        return False, message

    # Duplicate validation
    if get_customer_by_pan(normalize_pan(pan)):
        return False, "PAN already registered."

    if get_customer_by_aadhaar(normalize_aadhaar(aadhaar)):
        return False, "Aadhaar already registered."

    return True, ""
