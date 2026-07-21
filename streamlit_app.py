import os
import streamlit as st

from src.auth import register_user, login_user
from src.upload import upload_document
from src.preprocessing import preprocess_image

from src.ocr import (
    perform_ocr,
    extract_pan_details,
    extract_aadhaar_details,
    save_ocr_result,
)

from src.kyc import calculate_kyc_score

from src.workflow import workflow

# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="AI Loan Processing System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Loan Processing System")

os.makedirs("temp", exist_ok=True)

# --------------------------------------------------------
# Tabs
# --------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Register",
        "Login",
        "Loan Processing"
    ]
)

# ========================================================
# REGISTER
# ========================================================

with tab1:

    st.header("👤 User Registration")

    name = st.text_input("Name")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=25
    )

    mobile = st.text_input("Mobile Number")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        user_id = register_user(
            name,
            age,
            mobile,
            email,
            password
        )

        st.success(f"Registration Successful\n\nUser ID : {user_id}")

# ========================================================
# LOGIN
# ========================================================

with tab2:

    st.header("🔐 Login")

    login_email = st.text_input(
        "Email",
        key="login_email"
    )

    login_password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login"):

        user = login_user(
            login_email,
            login_password
        )

        if user:

            st.success("Login Successful")

            st.session_state["user_id"] = user[0]

            st.write("User ID :", user[0])

            st.write("Name :", user[1])

        else:

            st.error("Invalid Email or Password")

# ========================================================
# LOAN PROCESSING
# ========================================================

with tab3:

    st.header("📂 Loan Processing")

    user_id = st.text_input(
        "User ID",
        value=st.session_state.get("user_id", "")
    )

    pan_file = st.file_uploader(
        "Upload PAN Card",
        type=["png", "jpg", "jpeg"]
    )

    aadhaar_file = st.file_uploader(
        "Upload Aadhaar Card",
        type=["png", "jpg", "jpeg"]
    )

    if st.button("Upload Documents"):

        if not user_id:

            st.error("Please enter User ID")

            st.stop()

        if pan_file is None:

            st.error("Please upload PAN Card")

            st.stop()

        if aadhaar_file is None:

            st.error("Please upload Aadhaar Card")

            st.stop()

        # -----------------------------------------
        # Save uploaded files temporarily
        # -----------------------------------------

        pan_temp = os.path.join(
            "temp",
            pan_file.name
        )

        with open(pan_temp, "wb") as f:

            f.write(pan_file.getbuffer())

        aadhaar_temp = os.path.join(
            "temp",
            aadhaar_file.name
        )

        with open(aadhaar_temp, "wb") as f:

            f.write(aadhaar_file.getbuffer())

        # -----------------------------------------
        # Upload to Database
        # -----------------------------------------

        pan_document_id, pan_path = upload_document(
            user_id,
            "PAN",
            pan_temp
        )

        aadhaar_document_id, aadhaar_path = upload_document(
            user_id,
            "AADHAAR",
            aadhaar_temp
        )

        st.success("✅ Documents Uploaded Successfully")

        st.session_state["pan_document_id"] = pan_document_id
        st.session_state["aadhaar_document_id"] = aadhaar_document_id

        st.session_state["pan_path"] = pan_path
        st.session_state["aadhaar_path"] = aadhaar_path

        # ---------------------------------------------------
        # PROCESS LOAN APPLICATION
        # ---------------------------------------------------

    if st.button("Process Loan Application"):

        if "pan_path" not in st.session_state:
            st.error("Please upload documents first.")
            st.stop()

        # ---------------------------------------
        # OCR
        # ---------------------------------------

        image = preprocess_image(
            st.session_state["pan_path"]
        )

        text, confidence = perform_ocr(image)

        details = extract_pan_details(text)

        save_ocr_result(
            st.session_state["pan_document_id"],
            details["PAN"],
            confidence,
            details["NAME"],
            details["FATHER"],
            details["DOB"],
        )

        st.divider()

        st.subheader("📄 OCR Result")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**PAN Number**")
            st.success(details["PAN"])

            st.write("**Name**")
            st.success(details["NAME"])

            st.write("**Father Name**")
            st.success(details["FATHER"])

        with col2:
            st.write("**Date of Birth**")
            st.success(details["DOB"])

            st.write("**OCR Confidence**")
            st.info(f"{confidence}%")

        # ---------------------------------------
        # Aadhaar OCR
        # ---------------------------------------

        aadhaar_image = preprocess_image(
            st.session_state["aadhaar_path"]
        )

        aadhaar_text, aadhaar_confidence = perform_ocr(
            aadhaar_image
        )

        st.subheader("Raw Aadhaar OCR")

        st.text(aadhaar_text)

        aadhaar_details = extract_aadhaar_details(
            aadhaar_text
        )

        save_ocr_result(
            st.session_state["aadhaar_document_id"],
            aadhaar_details["AADHAAR"],
            aadhaar_confidence,
            aadhaar_details["NAME"],
            "",
            aadhaar_details["DOB"],
        )

        st.divider()

        st.subheader("🪪 Aadhaar OCR Result")

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Aadhaar Number**")
            st.success(aadhaar_details["AADHAAR"])

            st.write("**Name**")
            st.success(aadhaar_details["NAME"])

        with col2:

            st.write("**Date of Birth**")
            st.success(aadhaar_details["DOB"])

            st.write("**OCR Confidence**")
            st.info(f"{aadhaar_confidence}%")

        # ---------------------------------------
        # KYC
        # ---------------------------------------

        score, status = calculate_kyc_score(user_id)

        print("Score from calculate_kyc_score():", score)
        print("Status from calculate_kyc_score():", status)

        st.divider()

        st.subheader("✅ KYC Score")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Score", score)

        with c2:
            st.metric("Status", status)

        # ---------------------------------------
        # LANGGRAPH
        # ---------------------------------------

        state = {
            "user_id": user_id,
            "login": True,
            "documents_uploaded": True,
            "ocr_completed": True,
            "kyc_score": score,
            "kyc_status": status,
            "loan_status": "",
            "explanation": "",
            "fraud": False,
            "fraud_reason": "",
        }

        result = workflow.invoke(state)

        st.divider()

        st.subheader("🤖 LangGraph Workflow")

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"Login : {result['login']}")
            st.success(f"Documents : {result['documents_uploaded']}")
            st.success(f"OCR : {result['ocr_completed']}")

        with col2:
            st.metric("KYC Score", result["kyc_score"])
            st.metric("Loan Status", result["loan_status"])

        # ----------------------------
        # Fraud Detection
        # ----------------------------

        st.divider()

        st.subheader("🛡 Fraud Detection")

        if result["fraud"]:
            st.error("Fraud Detected")
            st.write(result["fraud_reason"])
        else:
            st.success("No Fraud Detected")
            st.write(result["fraud_reason"])

        # ----------------------------
        # AI Decision
        # ----------------------------

        st.divider()

        st.subheader("🤖 AI Decision")

        st.write(result["explanation"])