from langchain_core.tools import tool

from langchain_app.chains import ask_policy


@tool
def search_loan_policy(question: str) -> str:
    """
    Search the loan policy knowledge base to answer
    banking, loan, EMI, eligibility, OCR, KYC,
    fraud policy and FAQ related questions.
    """

    return ask_policy(question)