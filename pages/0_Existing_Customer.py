import streamlit as st

from database.customer_repository import get_customer_by_pan
from database.loan_repository import get_loans_by_customer
from database.document_repository import get_documents_by_application


st.title("👤 Existing Customer")

pan = st.text_input("Enter PAN Number")

if st.button("Find Customer"):

    customer = get_customer_by_pan(pan)

    st.session_state["searched_customer"] = dict(customer)

customer = st.session_state.get("searched_customer")

if customer:

    st.success("Customer Found")

    st.write(f"### 👤 {customer['full_name']}")
    st.write(f"Customer ID : {customer['customer_id']}")
    st.write(f"Email : {customer['email']}")
    st.write(f"Phone : {customer['phone']}")

    st.session_state["customer_id"] = customer["customer_id"]

    loans = get_loans_by_customer(customer["customer_id"])

    st.divider()

    st.subheader("📋 Previous Loan Applications")

    if loans:

        for loan in loans:

            with st.container():

                st.info(
                    f"""
                Application ID : {loan['application_id']}

                Loan Type : {loan['loan_type']}

                Loan Amount : ₹{loan['loan_amount']:,.2f}

                Monthly Income : ₹{loan['monthly_income']:,.2f}

                Credit Score : {loan['credit_score']}

                Status : {loan['application_status']}

                Risk Level : {loan['risk_level']}
                """
                )

                col1, col2 = st.columns(2)

                with col1:

                        if st.button("Continue", key=loan["application_id"]):

                            st.session_state["customer_id"] = customer["customer_id"]
                            st.session_state["application_id"] = loan["application_id"]

                            documents = get_documents_by_application(loan["application_id"])

                            if documents:
                                st.switch_page("pages/4_OCR_Processing.py")
                            else:
                                st.switch_page("pages/3_upload_documents.py")

                with col2:

                        st.write("")

    else:

        st.warning("No previous loan applications found.")

        st.divider()

        if st.button("➕ Create New Loan Application"):

            st.session_state.pop("application_id", None)

            st.switch_page("pages/2_loan_application.py")

        else:

            st.error("Customer not found.")