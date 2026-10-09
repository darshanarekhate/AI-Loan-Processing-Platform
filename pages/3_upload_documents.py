import streamlit as st

from utils.file_handler import UploadError, save_uploaded_file
from utils.session import require_staff

from database.document_repository import (
    save_document,
    document_exists,
)

from services.tracker_service import documents_uploaded


st.set_page_config(
    page_title="Upload Documents",
    page_icon="📄",
    layout="wide"
)

require_staff()

st.title("📄 Upload Loan Documents")
st.caption("Upload all mandatory documents for loan verification.")

# ---------------------------------------------------
# Session Validation
# ---------------------------------------------------

customer_id = st.session_state.get("customer_id")
application_id = st.session_state.get("application_id")

if not customer_id or not application_id:
    st.error("Please complete Customer Registration and Loan Application first.")
    st.stop()

st.success(f"👤 Customer ID : {customer_id}")
st.success(f"📄 Application ID : {application_id}")

st.divider()

# ---------------------------------------------------
# Upload Controls
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    pan = st.file_uploader(
        "PAN Card",
        # OCR reads images only
        type=["jpg", "jpeg", "png"],
        help="Upload PAN Card"
    )

    salary = st.file_uploader(
        "Salary Slip",
        type=["pdf"],
        help="Latest salary slip"
    )

with col2:

    aadhaar = st.file_uploader(
        "Aadhaar Card",
        # OCR reads images only
        type=["jpg", "jpeg", "png"],
        help="Upload Aadhaar Card"
    )

    bank = st.file_uploader(
        "Bank Statement",
        type=["pdf"],
        help="Latest 6 months bank statement"
    )

# ---------------------------------------------------
# Upload Button
# ---------------------------------------------------

if st.button("📤 Upload Documents", use_container_width=True):

    uploads = {
        "PAN": pan,
        "AADHAAR": aadhaar,
        "SALARY_SLIP": salary,
        "BANK_STATEMENT": bank,
    }

    uploaded_documents = []

    uploaded_count = 0

    progress = st.progress(0)

    total = len(uploads)

    processed = 0

    for doc_type, uploaded_file in uploads.items():

        processed += 1

        progress.progress(processed / total)

        if uploaded_file is None:
            continue

        if document_exists(application_id, doc_type):

            st.warning(f"⚠ {doc_type} already uploaded.")
            continue

        try:
            file_path = save_uploaded_file(
                uploaded_file,
                customer_id,
                application_id,
                doc_type,
            )
        except UploadError as exc:
            st.error(f"❌ {doc_type}: {exc}")
            continue

        save_document(
            {
                "application_id": application_id,
                "customer_id": customer_id,
                "document_type": doc_type,
                "file_name": uploaded_file.name,
                "file_path": file_path,
            }
        )

        uploaded_documents.append(doc_type)

        uploaded_count += 1

    progress.empty()

    if uploaded_count == 0:

        st.info("No new documents were uploaded.")

        st.stop()

    # ------------------------------------------
    # Update Application Tracker
    # ------------------------------------------

    documents_uploaded(
        application_id,
        uploaded_documents
    )

    st.success("✅ Documents Uploaded Successfully!")

    st.metric(
        "Documents Uploaded",
        uploaded_count
    )

    st.success(
        "Uploaded Documents: "
        + ", ".join(uploaded_documents)
    )

    st.switch_page("pages/4_OCR_Processing.py")