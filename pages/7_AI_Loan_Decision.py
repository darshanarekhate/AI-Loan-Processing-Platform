import streamlit as st

from database.kyc_result_repository import get_kyc_status
from database.loan_repository import get_loan_by_application
from services.decision_service import run_loan_decision
from utils.session import require_staff


st.set_page_config(
    page_title="AI Loan Decision",
    page_icon="🤖"
)

require_staff()

st.title("🤖 AI Loan Decision")

st.caption(
    "The decision is made by transparent policy rules (credit score, "
    "KYC, fraud risk, minimum income and EMI affordability). "
    "The AI model only writes the explanation."
)


application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")


if not application_id or not customer_id:

    st.error("Application not found.")

    st.stop()


loan = get_loan_by_application(application_id)


if not loan:

    st.error("Loan application not found.")

    st.stop()


# ---------------------------------
# Application Summary
# ---------------------------------

st.subheader("Application Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Loan Type", loan["loan_type"])
c2.metric("Loan Amount", f"₹{loan['loan_amount']:,.0f}")
c3.metric("Monthly Income", f"₹{loan['monthly_income']:,.0f}")

c1, c2, c3 = st.columns(3)

c1.metric("Credit Score", loan["credit_score"])
c2.metric("Tenure", f"{loan['tenure_months'] or '-'} months")
c3.metric("KYC Status", get_kyc_status(application_id))

st.divider()


# ---------------------------------
# Run Decision
# ---------------------------------

if st.button("Run AI Decision", type="primary", use_container_width=True):

    with st.spinner("Evaluating the application..."):

        outcome = run_loan_decision(
            application_id,
            customer_id,
        )

    if "error" in outcome:
        st.error(outcome["error"])
        st.stop()

    result = outcome["result"]

    decision_style = {
        "APPROVED": st.success,
        "REJECTED": st.error,
    }.get(result.decision, st.warning)

    decision_style(f"Decision: **{result.decision}**  |  Risk: **{result.risk_level}**")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Estimated EMI", f"₹{result.emi:,.0f}")
    m2.metric("FOIR", f"{result.foir:.0%}")
    m3.metric("Rate (ref.)", f"{result.interest_rate:.2f}%")
    m4.metric("Max at 50% FOIR", f"₹{result.max_eligible_amount:,.0f}")

    st.subheader("Policy Checks")

    for check in result.checks:
        icon = "✅" if check.passed else "⚠️"
        st.write(f"{icon} **{check.name}** - {check.detail}")

    st.subheader("Explanation")

    st.write(outcome["explanation"])

    st.page_link(
        "pages/8_Loan_Report.py",
        label="Generate Loan Report",
        icon="📄",
    )
