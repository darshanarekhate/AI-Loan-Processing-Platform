import streamlit as st

from utils.helpers import generate_application_id
from services.decision_engine import (
    PRODUCT_POLICIES,
    calculate_emi,
    max_affordable_principal,
)
from services.tracker_service import loan_submitted
from database.loan_repository import save_loan
from utils.session import require_staff

st.set_page_config(
    page_title="Loan Application",
    page_icon="🏦",
    layout="wide"
)

require_staff()

st.title("🏦 Loan Application")

customer_id = st.session_state.get("customer_id")

if not customer_id:
    st.error("No customer selected. Please register or look up a customer first.")
    st.stop()

st.info(f"Customer ID: {customer_id}")

loan_type = st.selectbox(
    "Loan Type",
    list(PRODUCT_POLICIES),
)

policy = PRODUCT_POLICIES[loan_type]

col1, col2 = st.columns(2)

with col1:

    loan_amount = st.number_input(
        "Loan Amount (₹)",
        min_value=10000.0,
        value=500000.0,
        step=10000.0,
    )

    monthly_income = st.number_input(
        "Monthly Income (₹)",
        min_value=1000.0,
        value=50000.0,
        step=1000.0,
    )

with col2:

    tenure_months = st.slider(
        "Tenure (months)",
        policy.min_tenure_months,
        policy.max_tenure_months,
        min(60, policy.max_tenure_months),
        step=12 if policy.max_tenure_months >= 120 else 6,
    )

    credit_score = st.slider(
        "Credit Score",
        300,
        900,
        750,
    )

# ------------------------------------------------------------
# Live EMI preview
# ------------------------------------------------------------

emi = calculate_emi(loan_amount, policy.annual_interest_rate, tenure_months)
foir = emi / monthly_income
max_amount = max_affordable_principal(
    monthly_income,
    policy.annual_interest_rate,
    tenure_months,
)

st.divider()
st.subheader("📐 EMI Preview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Reference Rate", f"{policy.annual_interest_rate:.2f}% p.a.")
m2.metric("Estimated EMI", f"₹{emi:,.0f}")
m3.metric("EMI / Income (FOIR)", f"{foir:.0%}")
m4.metric("Max at 50% FOIR", f"₹{max_amount:,.0f}")

if foir > 0.5:
    st.warning(
        "EMI exceeds 50% of monthly income - this application will need "
        "manual review or may be rejected. Consider a lower amount or a "
        "longer tenure."
    )

if st.button("Create Loan Application", type="primary"):

    application = {
        "application_id": generate_application_id(),
        "customer_id": customer_id,
        "loan_type": loan_type,
        "loan_amount": loan_amount,
        "monthly_income": monthly_income,
        "credit_score": credit_score,
        "application_status": "NEW",
        "risk_level": "PENDING",
        "tenure_months": tenure_months,
    }

    save_loan(application)

    # Add first stage to tracker
    loan_submitted(application["application_id"])

    st.session_state["application_id"] = application["application_id"]

    st.success("✅ Loan Application Created!")

    st.success(f"Application ID: {application['application_id']}")

    st.page_link(
        "pages/3_upload_documents.py",
        label="Continue to Document Upload",
        icon="➡️",
    )
