import pytest

from langchain_app.question_router import detect_route


@pytest.mark.parametrize(
    "question, route",
    [
        ("What is my name?", "customer"),
        ("Show my customer information.", "customer"),
        ("What is my loan amount?", "loan"),
        ("What is my credit score?", "loan"),
        ("What is my KYC status?", "kyc"),
        ("What is my fraud risk?", "fraud"),
        ("Show my OCR results", "ocr"),
        ("Show the AI decision", "ai_decision"),
        ("What is the maximum LTV for a car loan?", "policy"),
        ("What is the maximum tenure for a car loan?", "policy"),
        # Regression: used to return the customer's KYC status.
        ("What documents are required for KYC?", "policy"),
    ],
)
def test_direct_routes(question, route):
    assert detect_route(question) == route


@pytest.mark.parametrize(
    "question",
    [
        "Why was my loan approved?",
        "Based on my credit score, should I apply for a home loan?",
        "Explain my fraud risk",
        "",
    ],
)
def test_reasoning_questions_go_to_llm(question):
    assert detect_route(question) is None


def test_short_keywords_match_whole_words_only():
    # "emi" must not match inside "remind"
    assert detect_route("Can you remind me later?") is None
    assert detect_route("How is EMI calculated?") == "policy"
