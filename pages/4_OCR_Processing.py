import streamlit as st

from database.document_repository import get_documents_by_application
from database.ocr_repository import save_ocr_result
from ocr.ocr_service import process_document

st.set_page_config(
    page_title="OCR Processing",
    page_icon="📄"
)

st.title("📄 OCR Processing")

customer_id = st.session_state.get("customer_id")
application_id = st.session_state.get("application_id")

if not customer_id or not application_id:
    st.error("No Application Found")
    st.stop()

documents = get_documents_by_application(application_id)

if not documents:
    st.warning("No uploaded documents found.")
    st.stop()

st.subheader("Uploaded Documents")

for doc in documents:

    st.write(f"📄 {doc['document_type']} : {doc['file_name']}")

st.divider()

st.subheader("OCR Results")

for doc in documents:

    if doc["document_type"] not in ["PAN", "AADHAAR"]:
        continue

    result = process_document(
        doc["document_type"],
        doc["file_path"]
    )

    if doc["document_type"] == "PAN":

        save_ocr_result(
            {
                "application_id": application_id,
                "customer_id": customer_id,
                "document_type": "PAN",
                "extracted_number": result["PAN"],
                "extracted_name": result["NAME"],
                "extracted_dob": result["DOB"],
                "confidence": result["OCR_CONFIDENCE"],
            }
        )

    elif doc["document_type"] == "AADHAAR":

        save_ocr_result(
            {
                "application_id": application_id,
                "customer_id": customer_id,
                "document_type": "AADHAAR",
                "extracted_number": result["AADHAAR"],
                "extracted_name": result["NAME"],
                "extracted_dob": result["DOB"],
                "confidence": result["OCR_CONFIDENCE"],
            }
        )

    st.write(f"### {doc['document_type']}")
    st.json(result)

st.success("✅ OCR Processing Completed")