"""
Masking helpers for personally identifiable information (PII).

Used anywhere PAN / Aadhaar / phone numbers are displayed or handed
to an LLM, so the full identifiers never leave the database layer.
"""


def mask_phone(phone: str | None) -> str:
    phone = (phone or "").strip()

    if len(phone) < 4:
        return "****"

    return "*" * (len(phone) - 4) + phone[-4:]


def mask_pan(pan: str | None) -> str:
    """
    ABCPE1234F -> ABCPE****F
    """

    pan = (pan or "").strip()

    if len(pan) < 6:
        return "******"

    return pan[:5] + "*" * (len(pan) - 6) + pan[-1:]


def mask_aadhaar(aadhaar: str | None) -> str:
    """
    234567890124 -> ********0124
    """

    aadhaar = (aadhaar or "").replace(" ", "")

    if len(aadhaar) < 4:
        return "********"

    return "*" * (len(aadhaar) - 4) + aadhaar[-4:]
