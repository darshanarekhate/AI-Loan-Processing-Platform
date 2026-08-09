import streamlit as st

from src.fraud_agent import fraud_check


st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🛡️"
)


st.title("🛡️ Fraud Detection")


application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")


if not application_id or not customer_id:
    st.error("Application not found.")
    st.stop()


result = fraud_check(
    application_id,
    customer_id
)


st.subheader("Fraud Detection Result")


if result["risk"] == "HIGH":

    st.error("🚨 High Fraud Risk")

elif result["risk"] == "MEDIUM":

    st.warning("⚠️ Medium Fraud Risk")

else:

    st.success("✅ Low Fraud Risk")


st.write(
    f"### Risk Level : {result['risk']}"
)


st.write("### Findings")


for reason in result["reasons"]:

    st.write(f"- {reason}")