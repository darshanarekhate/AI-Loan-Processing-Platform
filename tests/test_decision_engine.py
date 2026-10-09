import pytest

from services.decision_engine import (
    APPROVED,
    MANUAL_REVIEW,
    REJECTED,
    calculate_emi,
    evaluate_application,
    max_affordable_principal,
)


def decide(**overrides):
    params = dict(
        loan_type="Car Loan",
        loan_amount=500_000,
        monthly_income=80_000,
        credit_score=780,
        kyc_status="VERIFIED",
        fraud_risk="LOW",
        tenure_months=60,
    )
    params.update(overrides)
    return evaluate_application(**params)


def test_emi_matches_standard_formula():
    # 1,00,000 at 12% p.a. for 12 months -> 8,884.88
    assert calculate_emi(100_000, 12, 12) == pytest.approx(8884.88, abs=0.01)


def test_emi_zero_rate_is_simple_division():
    assert calculate_emi(120_000, 0, 12) == pytest.approx(10_000)


def test_max_affordable_principal_is_inverse_of_emi():
    principal = max_affordable_principal(60_000, 10.5, 60, foir_limit=0.5)
    assert calculate_emi(principal, 10.5, 60) == pytest.approx(30_000, rel=1e-6)


def test_strong_application_is_approved():
    result = decide()
    assert result.decision == APPROVED
    assert result.risk_level == "LOW"
    assert all(check.passed for check in result.checks)


def test_high_fraud_risk_is_rejected():
    result = decide(fraud_risk="HIGH")
    assert result.decision == REJECTED
    assert result.risk_level == "HIGH"


def test_medium_fraud_goes_to_manual_review():
    assert decide(fraud_risk="MEDIUM").decision == MANUAL_REVIEW


@pytest.mark.parametrize("kyc", ["PARTIAL", "MANUAL_REVIEW", "NOT_COMPLETED", None])
def test_unverified_kyc_needs_review(kyc):
    assert decide(kyc_status=kyc).decision == MANUAL_REVIEW


def test_credit_score_bands():
    assert decide(credit_score=600).decision == REJECTED
    assert decide(credit_score=700).decision == MANUAL_REVIEW
    assert decide(credit_score=760).decision == APPROVED


def test_below_product_minimum_credit_score_is_reviewed():
    # Personal loan minimum is 720
    result = decide(loan_type="Personal Loan", credit_score=700, loan_amount=200_000, tenure_months=36)
    assert result.decision == MANUAL_REVIEW
    assert any("720" in reason for reason in result.reasons)


def test_income_below_product_minimum_is_rejected():
    result = decide(monthly_income=15_000, loan_amount=50_000)
    assert result.decision == REJECTED
    assert any("minimum" in reason for reason in result.reasons)


def test_unaffordable_emi_is_rejected():
    # ~1.5 lakh EMI on 80k income
    result = decide(loan_amount=7_000_000)
    assert result.decision == REJECTED
    assert result.foir > 0.65


def test_borderline_emi_needs_review():
    # EMI ~ 55-60% of income
    result = decide(loan_amount=2_150_000, monthly_income=80_000)
    assert 0.5 < result.foir <= 0.65
    assert result.decision == MANUAL_REVIEW


def test_tenure_is_clamped_to_product_limits():
    assert decide(tenure_months=200).tenure_months == 84
    assert decide(tenure_months=1).tenure_months == 12
    assert decide(tenure_months=None).tenure_months == 84


def test_unknown_product_goes_to_officer():
    assert decide(loan_type="Gold Loan").decision == MANUAL_REVIEW


def test_rejection_reasons_include_review_reasons_too():
    result = decide(credit_score=600, kyc_status="PARTIAL")
    assert result.decision == REJECTED
    assert len(result.reasons) >= 2


def test_summary_is_human_readable():
    text = decide().summary()
    assert "Decision: APPROVED" in text
    assert "Estimated EMI" in text
