"""
Deterministic loan decision engine.

The approve / reject / manual-review outcome is computed by explicit,
auditable rules taken from the Knowledge_Base policy documents.
The LLM is only used afterwards to *explain* the outcome in plain
language - it can never change it.

Pure Python: no database, no network, fully unit-tested.
"""

from dataclasses import dataclass, field


# ============================================================
# Status constants (single source of truth)
# ============================================================

APPROVED = "APPROVED"
REJECTED = "REJECTED"
MANUAL_REVIEW = "MANUAL_REVIEW"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

_RISK_ORDER = {RISK_LOW: 0, RISK_MEDIUM: 1, RISK_HIGH: 2}


# ============================================================
# Product policy (Knowledge_Base/loan_policy.txt, eligibility.txt,
# interest_rates.txt and the per-product policy files)
# ============================================================

@dataclass(frozen=True)
class ProductPolicy:
    min_credit_score: int
    min_monthly_income: float
    annual_interest_rate: float  # reference rate used for EMI (% p.a.)
    min_tenure_months: int
    max_tenure_months: int


PRODUCT_POLICIES = {
    "Home Loan": ProductPolicy(700, 25_000, 9.25, 60, 360),
    "Car Loan": ProductPolicy(680, 25_000, 10.50, 12, 84),
    "Personal Loan": ProductPolicy(720, 20_000, 14.25, 12, 60),
    # Education loans rely on a co-applicant's income, so no
    # minimum applicant income is enforced.
    "Education Loan": ProductPolicy(650, 0, 10.50, 60, 180),
}

# Bank-wide credit bands (Knowledge_Base/credit_policy.txt)
CREDIT_SCORE_REJECT_BELOW = 650
CREDIT_SCORE_AUTO_APPROVE = 750

# Fixed Obligation to Income Ratio (FOIR): share of monthly income
# that may go to this EMI. 50% is the common Indian retail-lending
# ceiling; above 65% the EMI is treated as unaffordable.
FOIR_REVIEW_ABOVE = 0.50
FOIR_REJECT_ABOVE = 0.65

KYC_VERIFIED = "VERIFIED"


# ============================================================
# EMI maths
# ============================================================

def calculate_emi(
    principal: float,
    annual_rate_percent: float,
    tenure_months: int,
) -> float:
    """
    Standard reducing-balance EMI:

        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

    where r is the monthly interest rate and n the tenure in months.
    """

    if principal <= 0 or tenure_months <= 0:
        return 0.0

    r = annual_rate_percent / 12 / 100

    if r == 0:
        return principal / tenure_months

    growth = (1 + r) ** tenure_months

    return principal * r * growth / (growth - 1)


def max_affordable_principal(
    monthly_income: float,
    annual_rate_percent: float,
    tenure_months: int,
    foir_limit: float = FOIR_REVIEW_ABOVE,
) -> float:
    """
    Inverse of the EMI formula: the largest loan whose EMI stays
    within foir_limit of the monthly income.
    """

    max_emi = monthly_income * foir_limit

    if max_emi <= 0 or tenure_months <= 0:
        return 0.0

    r = annual_rate_percent / 12 / 100

    if r == 0:
        return max_emi * tenure_months

    growth = (1 + r) ** tenure_months

    return max_emi * (growth - 1) / (r * growth)


# ============================================================
# Result types
# ============================================================

@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class DecisionResult:
    decision: str
    risk_level: str
    reasons: list[str]
    checks: list[Check] = field(default_factory=list)
    emi: float = 0.0
    foir: float = 0.0
    tenure_months: int = 0
    interest_rate: float = 0.0
    max_eligible_amount: float = 0.0

    def summary(self) -> str:
        """
        Plain-text explanation used when no LLM is available.
        """

        lines = [
            f"Decision: {self.decision}",
            f"Risk Level: {self.risk_level}",
            "",
            "Reasons:",
            *[f"- {reason}" for reason in self.reasons],
            "",
            (
                f"Estimated EMI: Rs. {self.emi:,.0f} over {self.tenure_months} "
                f"months at {self.interest_rate:.2f}% p.a. "
                f"({self.foir:.0%} of monthly income)."
            ),
        ]

        if self.max_eligible_amount:
            lines.append(
                "Maximum amount affordable at a 50% FOIR: "
                f"Rs. {self.max_eligible_amount:,.0f}."
            )

        return "\n".join(lines)


# ============================================================
# Decision rules
# ============================================================

def _worse(a: str, b: str) -> str:
    return a if _RISK_ORDER.get(a, 0) >= _RISK_ORDER.get(b, 0) else b


def evaluate_application(
    loan_type: str,
    loan_amount: float,
    monthly_income: float,
    credit_score: int,
    kyc_status: str,
    fraud_risk: str,
    tenure_months: int | None = None,
) -> DecisionResult:
    """
    Evaluate an application against bank policy.

    Hard-stop rules produce REJECTED; soft rules produce
    MANUAL_REVIEW; an application passing every rule is APPROVED.
    """

    policy = PRODUCT_POLICIES.get(loan_type)

    if policy is None:
        return DecisionResult(
            decision=MANUAL_REVIEW,
            risk_level=RISK_MEDIUM,
            reasons=[f"Unknown loan product '{loan_type}' - needs an officer."],
        )

    tenure = tenure_months or policy.max_tenure_months
    tenure = max(policy.min_tenure_months, min(tenure, policy.max_tenure_months))

    emi = calculate_emi(loan_amount, policy.annual_interest_rate, tenure)
    foir = emi / monthly_income if monthly_income > 0 else float("inf")

    max_eligible = max_affordable_principal(
        monthly_income,
        policy.annual_interest_rate,
        tenure,
    )

    kyc_status = (kyc_status or "").upper().replace(" ", "_")
    fraud_risk = (fraud_risk or RISK_LOW).upper()

    rejections: list[str] = []
    reviews: list[str] = []
    checks: list[Check] = []

    # ---------------- Fraud ----------------
    fraud_ok = fraud_risk == RISK_LOW
    checks.append(Check("Fraud screening", fraud_ok, f"Fraud risk {fraud_risk}"))

    if fraud_risk == RISK_HIGH:
        rejections.append("High fraud risk detected during document screening.")
    elif fraud_risk == RISK_MEDIUM:
        reviews.append("Medium fraud risk - documents need officer verification.")

    # ---------------- KYC ----------------
    kyc_ok = kyc_status == KYC_VERIFIED
    checks.append(Check("KYC verification", kyc_ok, f"KYC status {kyc_status or 'NOT_COMPLETED'}"))

    if not kyc_ok:
        reviews.append(
            "KYC is not fully verified "
            f"({kyc_status or 'NOT_COMPLETED'}); approval requires verified KYC."
        )

    # ---------------- Credit score ----------------
    credit_ok = credit_score >= max(CREDIT_SCORE_AUTO_APPROVE, policy.min_credit_score)
    checks.append(Check(
        "Credit score",
        credit_ok,
        f"{credit_score} (product minimum {policy.min_credit_score}, "
        f"auto-approve {CREDIT_SCORE_AUTO_APPROVE}+)",
    ))

    if credit_score < CREDIT_SCORE_REJECT_BELOW:
        rejections.append(
            f"Credit score {credit_score} is below the bank minimum of "
            f"{CREDIT_SCORE_REJECT_BELOW}."
        )
    elif credit_score < policy.min_credit_score:
        reviews.append(
            f"Credit score {credit_score} is below the {loan_type} minimum of "
            f"{policy.min_credit_score}."
        )
    elif credit_score < CREDIT_SCORE_AUTO_APPROVE:
        reviews.append(
            f"Credit score {credit_score} is in the 650-749 band, which "
            "requires manual review."
        )

    # ---------------- Income ----------------
    income_ok = monthly_income >= policy.min_monthly_income
    checks.append(Check(
        "Minimum income",
        income_ok,
        f"Rs. {monthly_income:,.0f} vs minimum Rs. {policy.min_monthly_income:,.0f}",
    ))

    if not income_ok:
        rejections.append(
            f"Monthly income Rs. {monthly_income:,.0f} is below the {loan_type} "
            f"minimum of Rs. {policy.min_monthly_income:,.0f}."
        )

    # ---------------- Affordability (FOIR) ----------------
    foir_ok = foir <= FOIR_REVIEW_ABOVE
    checks.append(Check(
        "EMI affordability (FOIR)",
        foir_ok,
        f"EMI Rs. {emi:,.0f} = {foir:.0%} of income (limit {FOIR_REVIEW_ABOVE:.0%})",
    ))

    if foir > FOIR_REJECT_ABOVE:
        rejections.append(
            f"EMI of Rs. {emi:,.0f} would take {foir:.0%} of monthly income "
            f"(maximum {FOIR_REJECT_ABOVE:.0%})."
        )
    elif foir > FOIR_REVIEW_ABOVE:
        reviews.append(
            f"EMI of Rs. {emi:,.0f} is {foir:.0%} of monthly income, above the "
            f"{FOIR_REVIEW_ABOVE:.0%} comfort limit."
        )

    # ---------------- Outcome ----------------
    if rejections:
        decision = REJECTED
        reasons = rejections + reviews
    elif reviews:
        decision = MANUAL_REVIEW
        reasons = reviews
    else:
        decision = APPROVED
        reasons = ["All policy checks passed."]

    # ---------------- Risk level ----------------
    if credit_score >= CREDIT_SCORE_AUTO_APPROVE and foir <= 0.40:
        financial_risk = RISK_LOW
    elif credit_score >= CREDIT_SCORE_REJECT_BELOW and foir <= FOIR_REVIEW_ABOVE:
        financial_risk = RISK_MEDIUM
    else:
        financial_risk = RISK_HIGH

    risk_level = _worse(financial_risk, fraud_risk if fraud_risk in _RISK_ORDER else RISK_MEDIUM)

    return DecisionResult(
        decision=decision,
        risk_level=risk_level,
        reasons=reasons,
        checks=checks,
        emi=round(emi, 2),
        foir=round(foir, 4) if foir != float("inf") else foir,
        tenure_months=tenure,
        interest_rate=policy.annual_interest_rate,
        max_eligible_amount=round(max_eligible, -3),
    )
