import streamlit as st

from utils.helpers import generate_application_id
from services.tracker_service import loan_submitted
from database.loan_repository import save_loan

st.set_page_config(
    page_title="Loan Application",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Loan Application")

customer_id = st.session_state.get("customer_id")

if not customer_id:
    st.error("No customer selected. Please register a customer first.")
    st.stop()

st.info(f"Customer ID: {customer_id}")

loan_type = st.selectbox(
    "Loan Type",
    [
        "Home Loan",
        "Car Loan",
        "Personal Loan",
        "Education Loan",
    ],
)

loan_amount = st.number_input(
    "Loan Amount",
    min_value=10000.0,
)

monthly_income = st.number_input(
    "Monthly Income",
    min_value=1000.0,
)

credit_score = st.slider(
    "Credit Score",
    300,
    900,
    750,
)

if st.button("Create Loan Application"):

    application = {
        "application_id": generate_application_id(),
        "customer_id": customer_id,
        "loan_type": loan_type,
        "loan_amount": loan_amount,
        "monthly_income": monthly_income,
        "credit_score": credit_score,
        "application_status": "NEW",
        "risk_level": "Pending",
    }

    save_loan(application)

    # Add first stage to tracker
    loan_submitted(application["application_id"])

    st.session_state["application_id"] = application["application_id"]

    st.success("✅ Loan Application Created!")

    st.success(f"Application ID: {application['application_id']}")