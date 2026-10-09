import os

import streamlit as st

from database.customer_repository import get_customer_by_id
from database.decision_repository import get_decision
from database.fraud_repository import get_fraud_result
from database.kyc_result_repository import get_kyc_result
from database.loan_repository import get_loan_by_application
from services.report_service import generate_report
from utils.session import require_staff

st.set_page_config(
    page_title="Loan Report",
    page_icon="📄",
)

require_staff()

st.title("📄 AI Loan Assessment Report")

application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")

if not application_id or not customer_id:
    st.error("No application selected.")
    st.stop()

kyc_result = get_kyc_result(application_id)

if not kyc_result:
    st.error("Please complete KYC Verification first.")
    st.stop()

decision = get_decision(application_id)

if not decision:
    st.error("Please complete AI Loan Decision first.")
    st.stop()

st.subheader("Loan Summary")

st.write(f"**Application ID:** {application_id}")
st.write(f"**Customer ID:** {customer_id}")
st.write(f"**Decision:** {decision['decision']}")
st.write(f"**Risk Level:** {decision['risk_level']}")

st.divider()

if st.button("📄 Generate Loan Report"):

    pdf_path = generate_report(
        application_id=application_id,
        customer=get_customer_by_id(customer_id),
        loan=get_loan_by_application(application_id),
        kyc_result=kyc_result,
        fraud_result=get_fraud_result(application_id),
        decision=decision,
    )

    st.success("Loan report generated successfully.")

    with open(pdf_path, "rb") as pdf:
        st.download_button(
            label="⬇ Download Loan Report",
            data=pdf,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
        )

st.divider()

st.subheader("AI Decision")

st.write(decision["explanation"])
