import streamlit as st

from utils.helpers import generate_customer_id
from database.customer_repository import save_customer
from utils.validators import validate_customer_registration
from datetime import date

st.title("👤 Customer Registration")

st.set_page_config(
    page_title="AI Loan System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Loan System")

st.subheader("Customer Registration")

full_name = st.text_input("Full Name")

email = st.text_input("Email Address")

phone = st.text_input("Phone Number")

pan = st.text_input("PAN Number")

aadhaar = st.text_input("Aadhaar Number")

dob = st.date_input(
    "Date of Birth",
    value=date(1993, 5, 18),
    min_value=date(1950, 1, 1),
    max_value=date.today()
)


if st.button("Register Customer"):

    valid, message = validate_customer_registration(
        full_name,
        phone,
        pan,
        aadhaar
    )

    if not valid:
        st.error(message)

    else:

        customer = {

            "customer_id": generate_customer_id(),

            "full_name": full_name,

            "email": email,

            "phone": phone,

            "pan": pan,

            "aadhaar": aadhaar,

            "date_of_birth": str(dob)

        }

        save_customer(customer)

        st.session_state["customer_id"] = customer["customer_id"]

        st.success("✅ Customer Registered Successfully!")

        st.success(f"Customer ID: {customer['customer_id']}")

        st.json(customer)