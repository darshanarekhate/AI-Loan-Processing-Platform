import streamlit as st
import pandas as pd

from database.loan_repository import (
    get_all_loans,
    get_loan_status_count,
    get_risk_level_count
)


st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("📊 AI Loan Admin Dashboard")



# --------------------------------
# Statistics
# --------------------------------

loans = get_all_loans()


total_loans = len(loans)


approved = 0
rejected = 0
pending = 0


for loan in loans:

    if loan["application_status"] == "APPROVED":
        approved += 1

    elif loan["application_status"] == "REJECTED":
        rejected += 1

    else:
        pending += 1



col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Applications",
        total_loans
    )


with col2:
    st.metric(
        "Approved",
        approved
    )


with col3:
    st.metric(
        "Rejected",
        rejected
    )


with col4:
    st.metric(
        "Pending",
        pending
    )



st.divider()



# --------------------------------
# Status Analytics
# --------------------------------

st.subheader(
    "📈 Loan Status Analysis"
)


status_data = get_loan_status_count()


if status_data:

    df_status = pd.DataFrame(
        status_data,
        columns=[
            "Status",
            "Count"
        ]
    )

    st.bar_chart(
        df_status.set_index("Status")
    )



# --------------------------------
# Risk Analytics
# --------------------------------

st.subheader(
    "🛡️ Risk Distribution"
)


risk_data = get_risk_level_count()


if risk_data:

    df_risk = pd.DataFrame(
        risk_data,
        columns=[
            "Risk",
            "Count"
        ]
    )

    st.bar_chart(
        df_risk.set_index("Risk")
    )



st.divider()



# --------------------------------
# Loan Applications Table
# --------------------------------

st.subheader(
    "📋 Recent Loan Applications"
)



if loans:

    table = []


    for loan in loans:

        table.append(
            {
                "Application ID":
                    loan["application_id"],

                "Customer ID":
                    loan["customer_id"],

                "Loan Type":
                    loan["loan_type"],

                "Amount":
                    f"₹ {loan['loan_amount']:,.0f}",

                "Income":
                    f"₹ {loan['monthly_income']:,.0f}",

                "Credit Score":
                    loan["credit_score"],

                "Status":
                    loan["application_status"],

                "Risk":
                    loan["risk_level"]
            }
        )


    df = pd.DataFrame(table)

    st.dataframe(
        df,
        use_container_width=True
    )


else:

    st.info(
        "No loan applications found."
    )