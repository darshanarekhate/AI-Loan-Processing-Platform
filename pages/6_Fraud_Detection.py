import streamlit as st

from services.tracker_service import fraud_completed
from src.fraud_agent import fraud_check
from utils.session import require_staff


st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🛡️"
)

require_staff()

st.title("🛡️ Fraud Detection")


application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")


if not application_id or not customer_id:
    st.error("Application not found.")
    st.stop()


if st.button("Run Fraud Screening", type="primary", use_container_width=True):

    result = fraud_check(
        application_id,
        customer_id
    )

    fraud_completed(application_id, result["risk"])

    st.session_state["fraud_result"] = {
        "application_id": application_id,
        **result,
    }


result = st.session_state.get("fraud_result")

if not result or result["application_id"] != application_id:
    st.info("Run fraud screening to analyse the uploaded documents.")
    st.stop()


st.subheader("Fraud Detection Result")


if result["risk"] == "HIGH":

    st.error("🚨 High Fraud Risk")

elif result["risk"] == "MEDIUM":

    st.warning("⚠️ Medium Fraud Risk - officer review required")

else:

    st.success("✅ Low Fraud Risk")


c1, c2 = st.columns(2)

c1.metric("Risk Level", result["risk"])
c2.metric("Risk Score", result["risk_score"])


st.write("### Findings")


for reason in result["reasons"]:

    st.write(f"- {reason}")


st.page_link(
    "pages/7_AI_Loan_Decision.py",
    label="Continue to AI Loan Decision",
    icon="➡️",
)
