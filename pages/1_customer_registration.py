import sqlite3
from datetime import date

import streamlit as st

from utils.helpers import generate_customer_id
from database.customer_repository import save_customer
from utils.session import require_staff
from utils.validators import (
    normalize_aadhaar,
    normalize_pan,
    normalize_phone,
    validate_customer_registration,
)


st.set_page_config(
    page_title="Customer Registration",
    page_icon="🏦",
    layout="wide"
)

require_staff()

st.title("👤 Customer Registration")

with st.form("customer_registration"):

    full_name = st.text_input("Full Name")

    email = st.text_input("Email Address")

    phone = st.text_input("Phone Number", placeholder="10-digit mobile number")

    pan = st.text_input("PAN Number", placeholder="ABCPE1234F")

    aadhaar = st.text_input("Aadhaar Number", placeholder="12 digits")

    dob = st.date_input(
        "Date of Birth",
        value=date(1995, 1, 1),
        min_value=date(1940, 1, 1),
        max_value=date.today()
    )

    submitted = st.form_submit_button("Register Customer")


if submitted:

    valid, message = validate_customer_registration(
        full_name,
        phone,
        pan,
        aadhaar,
        email=email,
        date_of_birth=dob,
    )

    if not valid:
        st.error(message)
        st.stop()

    customer = {

        "customer_id": generate_customer_id(),

        "full_name": " ".join(full_name.split()),

        "email": email.strip(),

        "phone": normalize_phone(phone),

        "pan": normalize_pan(pan),

        "aadhaar": normalize_aadhaar(aadhaar),

        "date_of_birth": str(dob)

    }

    try:
        save_customer(customer)
    except sqlite3.IntegrityError:
        st.error("A customer with this PAN or Aadhaar already exists.")
        st.stop()

    st.session_state["customer_id"] = customer["customer_id"]
    st.session_state.pop("application_id", None)

    st.success("✅ Customer Registered Successfully!")

    st.success(f"Customer ID: {customer['customer_id']}")

    st.page_link(
        "pages/2_loan_application.py",
        label="Continue to Loan Application",
        icon="➡️",
    )
