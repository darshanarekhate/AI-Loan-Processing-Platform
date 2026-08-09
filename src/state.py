from typing import TypedDict


class LoanState(TypedDict):

    user_id: str

    login: bool

    documents_uploaded: bool

    ocr_completed: bool

    kyc_score: int

    kyc_status: str

    loan_status: str

    name: str

    age: int

    pan: str

    aadhaar: str

    income: int

    loan_amount: int

    credit_score: int

    decision: str

    explanation: str

    fraud: bool

    fraud_reason: str

    name_match: bool

    name_match_score: float

    registered_name: str

    pan_name: str

    aadhaar_name: str

    manual_review: bool

    review_reason: str