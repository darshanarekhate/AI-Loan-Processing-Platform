from database.customer_repository import (
    get_customer_by_pan,
    get_customer_by_aadhaar,
)


def validate_customer_registration(
    full_name,
    phone,
    pan,
    aadhaar,
):
    # Required field validation
    if not full_name.strip():
        return False, "Full Name is required."

    if not phone.strip():
        return False, "Phone Number is required."

    if not pan.strip():
        return False, "PAN Number is required."

    if not aadhaar.strip():
        return False, "Aadhaar Number is required."

    # Duplicate validation
    if get_customer_by_pan(pan):
        return False, "PAN already registered."

    if get_customer_by_aadhaar(aadhaar):
        return False, "Aadhaar already registered."

    return True, ""