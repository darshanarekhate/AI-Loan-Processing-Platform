import streamlit as st

from database.document_repository import get_documents_by_application
from database.ocr_repository import get_ocr_results, save_ocr_result
from ocr.ocr_service import process_document
from services.tracker_service import ocr_completed
from utils.masking import mask_aadhaar, mask_pan
from utils.session import require_staff

st.set_page_config(
    page_title="OCR Processing",
    page_icon="📄"
)

require_staff()

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

identity_documents = [
    doc for doc in documents
    if doc["document_type"] in ("PAN", "AADHAAR")
]

if not identity_documents:
    st.warning("Upload a PAN and an Aadhaar card to run OCR.")
    st.stop()

# OCR is CPU-heavy, so it only runs when requested instead of on
# every Streamlit rerun.
if st.button("🔍 Run OCR", type="primary", use_container_width=True):

    confidences = []

    for doc in identity_documents:

        with st.spinner(f"Reading {doc['document_type']}..."):
            result = process_document(
                doc["document_type"],
                doc["file_path"]
            )

        if "ERROR" in result:
            st.error(f"{doc['document_type']}: OCR failed - {result['ERROR']}")
            continue

        number_key = "PAN" if doc["document_type"] == "PAN" else "AADHAAR"

        save_ocr_result(
            {
                "application_id": application_id,
                "customer_id": customer_id,
                "document_type": doc["document_type"],
                "extracted_number": result[number_key],
                "extracted_name": result["NAME"],
                "extracted_dob": result["DOB"],
                "confidence": result["OCR_CONFIDENCE"],
            }
        )

        confidences.append(result["OCR_CONFIDENCE"])

    if confidences:
        ocr_completed(application_id, min(confidences))
        st.success("✅ OCR Processing Completed")

# ------------------------------------------------------------
# Stored results
# ------------------------------------------------------------

results = get_ocr_results(application_id)

if results:

    st.subheader("OCR Results")

    for row in results:

        number = (
            mask_pan(row["extracted_pan"])
            if row["document_type"] == "PAN"
            else mask_aadhaar(row["extracted_aadhaar"])
        )

        with st.container(border=True):
            st.markdown(f"### {row['document_type']}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Name", row["extracted_name"] or "Not Found")
            c2.metric("Number", number)
            c3.metric("DOB", row["extracted_dob"] or "Not Found")
            c4.metric("Confidence", f"{row['confidence'] or 0:.1f}%")

    st.page_link(
        "pages/5_KYC_Verification.py",
        label="Continue to KYC Verification",
        icon="➡️",
    )
