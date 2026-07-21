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