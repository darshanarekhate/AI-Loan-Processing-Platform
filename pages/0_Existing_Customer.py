import streamlit as st

from database.customer_repository import get_customer_by_pan
from database.loan_repository import get_loans_by_customer
from database.document_repository import get_documents_by_application
from utils.masking import mask_aadhaar, mask_phone
from utils.session import require_staff
from utils.validators import is_valid_pan, normalize_pan


st.set_page_config(
    page_title="Existing Customer",
    page_icon="👤",
    layout="wide",
)

require_staff()

st.title("👤 Existing Customer")

pan = st.text_input("Enter PAN Number")

if st.button("Find Customer"):

    pan = normalize_pan(pan)

    if not is_valid_pan(pan):
        st.session_state.pop("searched_customer", None)
        st.error("Enter a valid PAN (e.g. ABCPE1234F).")
        st.stop()

    customer = get_customer_by_pan(pan)

    if customer is None:
        st.session_state.pop("searched_customer", None)
        st.error("Customer not found.")
        st.stop()

    st.session_state["searched_customer"] = dict(customer)

customer = st.session_state.get("searched_customer")

if customer:

    st.success("Customer Found")

    st.write(f"### 👤 {customer['full_name']}")
    st.write(f"Customer ID : {customer['customer_id']}")
    st.write(f"Email : {customer['email']}")
    st.write(f"Phone : {mask_phone(customer['phone'])}")
    st.write(f"Aadhaar : {mask_aadhaar(customer['aadhaar'])}")

    st.session_state["customer_id"] = customer["customer_id"]

    loans = get_loans_by_customer(customer["customer_id"])

    st.divider()

    st.subheader("📋 Previous Loan Applications")

    if loans:

        for loan in loans:

            with st.container(border=True):

                st.markdown(
                    f"""
**Application ID:** {loan['application_id']}
**Loan Type:** {loan['loan_type']}
**Loan Amount:** ₹{loan['loan_amount']:,.2f}
**Monthly Income:** ₹{loan['monthly_income']:,.2f}
**Credit Score:** {loan['credit_score']}
**Status:** {loan['application_status']}
**Risk Level:** {loan['risk_level']}
"""
                )

                if st.button("Continue", key=loan["application_id"]):

                    st.session_state["customer_id"] = customer["customer_id"]
                    st.session_state["application_id"] = loan["application_id"]

                    documents = get_documents_by_application(loan["application_id"])

                    if documents:
                        st.switch_page("pages/4_OCR_Processing.py")
                    else:
                        st.switch_page("pages/3_upload_documents.py")

    else:

        st.warning("No previous loan applications found.")

    st.divider()

    if st.button("➕ Create New Loan Application"):

        st.session_state.pop("application_id", None)

        st.switch_page("pages/2_loan_application.py")
