import streamlit as st

from database.loan_repository import (
    get_loan_by_application,
    update_loan_status,
    update_risk_level,
)

from database.kyc_result_repository import get_kyc_status

from database.decision_repository import save_decision

from src.fraud_agent import fraud_check
from src.decision_agent import ai_decision


st.set_page_config(
    page_title="AI Loan Decision",
    page_icon="🤖"
)


st.title("🤖 AI Loan Decision")


application_id = st.session_state.get(
    "application_id"
)

customer_id = st.session_state.get(
    "customer_id"
)


if not application_id or not customer_id:

    st.error(
        "Application not found."
    )

    st.stop()



loan = get_loan_by_application(
    application_id
)


if not loan:

    st.error(
        "Loan application not found."
    )

    st.stop()



# ---------------------------------
# Get KYC Status from Database
# ---------------------------------

kyc_status = get_kyc_status(
    application_id
)



# ---------------------------------
# Fraud Check
# ---------------------------------

fraud = fraud_check(
    application_id,
    customer_id
)


fraud_status = fraud["risk"]

fraud_reason = ", ".join(
    fraud["reasons"]
)



# ---------------------------------
# Application Summary
# ---------------------------------

st.subheader(
    "Application Summary"
)


st.write(
    f"**Application ID:** {application_id}"
)

st.write(
    f"**Customer ID:** {customer_id}"
)

st.write(
    f"**Credit Score:** {loan['credit_score']}"
)

st.write(
    f"**Monthly Income:** ₹{loan['monthly_income']:,.0f}"
)

st.write(
    f"**Loan Amount:** ₹{loan['loan_amount']:,.0f}"
)

st.write(
    f"**KYC Status:** {kyc_status}"
)

st.write(
    f"**Fraud Risk:** {fraud_status}"
)



st.divider()



# ---------------------------------
# Run AI Decision
# ---------------------------------

if st.button(
    "Run AI Decision"
):

    with st.spinner(
        "AI is analysing the loan application..."
    ):


        response = ai_decision(

            customer_id=customer_id,

            application_id=application_id,

            kyc_status=kyc_status,

            fraud_status=fraud_status,

            fraud_reason=fraud_reason,

            credit_score=loan["credit_score"],

            monthly_income=loan["monthly_income"],

            loan_amount=loan["loan_amount"],

        )


    # ---------------------------------
    # Extract Decision
    # ---------------------------------

    decision = "MANUAL REVIEW"


    if "APPROVED" in response.upper():

        decision = "APPROVED"


    elif "REJECTED" in response.upper():

        decision = "REJECTED"



    # ---------------------------------
    # Save Decision
    # ---------------------------------

    save_decision(

        application_id,

        customer_id,

        decision,

        fraud_status,

        response,

    )



    # ---------------------------------
    # Update Loan Application
    # ---------------------------------

    update_loan_status(

        application_id,

        decision

    )


    update_risk_level(

        application_id,

        fraud_status

    )



    st.success(
        "Analysis Completed"
    )


    st.subheader(
        "AI Recommendation"
    )


    st.write(
        response
    )


    st.success(
        f"Loan Status Updated : {decision}"
    )