import streamlit as st
import pandas as pd

from database.history_repository import get_customer_loan_history

st.set_page_config(
    page_title="Loan History",
    page_icon="📋",
)

st.title("📋 Customer Loan History")

customer_id = st.text_input("Customer ID")

if st.button("Search"):

    if not customer_id:
        st.warning("Enter Customer ID")
        st.stop()

    loans = get_customer_loan_history(customer_id)

    if not loans:
        st.error("No loan applications found.")
        st.stop()

    df = pd.DataFrame([dict(row) for row in loans])

    df = df.rename(
        columns={
            "application_id": "Application ID",
            "loan_type": "Loan Type",
            "loan_amount": "Loan Amount",
            "monthly_income": "Monthly Income",
            "credit_score": "Credit Score",
            "application_status": "Status",
            "risk_level": "Risk Level",
            "created_at": "Applied On",
        }
    )

    df["Loan Amount"] = df["Loan Amount"].apply(
        lambda x: f"Rs. {x:,.0f}"
    )

    df["Monthly Income"] = df["Monthly Income"].apply(
        lambda x: f"Rs. {x:,.0f}"
    )

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )