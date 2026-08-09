import streamlit as st

from services.kyc_service import verify_kyc

st.set_page_config(
    page_title="KYC Verification",
    page_icon="🪪",
    layout="wide"
)

st.title("🪪 AI KYC Verification")

# -------------------------------------------------------
# Get Application ID
# -------------------------------------------------------

application_id = st.session_state.get("application_id")

if not application_id:
    st.error("No Loan Application Found.")
    st.stop()

st.info(f"Application ID : {application_id}")

# -------------------------------------------------------
# Initialize Session State
# -------------------------------------------------------

if "kyc_result" not in st.session_state:
    st.session_state["kyc_result"] = None

if "kyc_status" not in st.session_state:
    st.session_state["kyc_status"] = None

# -------------------------------------------------------
# Start KYC Verification
# -------------------------------------------------------

if st.button("Start KYC Verification", use_container_width=True):

    result = verify_kyc(application_id)

    if result.get("status") == "FAILED":
        st.error(result["message"])
        st.stop()

    st.session_state["kyc_result"] = result
    st.session_state["kyc_status"] = result["status"]

# -------------------------------------------------------
# Display Saved Result
# -------------------------------------------------------

result = st.session_state.get("kyc_result")

if result:

    st.success("KYC Verification Completed")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Customer Information")

        st.write(f"**Registered Name :** {result['customer_name']}")
        st.write(f"**PAN Name :** {result['pan_name']}")
        st.write(f"**Aadhaar Name :** {result['aadhaar_name']}")

    with col2:

        st.subheader("Verification Summary")

        st.metric(
            "Name Similarity",
            f"{result['similarity']}%"
        )

        st.metric(
            "Verification Score",
            f"{result['score']}%"
        )

        st.metric(
            "Status",
            result["status"]
        )

    st.divider()

    st.subheader("Verification Checks")

    if result["pan_match"]:
        st.success("✔ PAN Verified")
    else:
        st.error("✘ PAN Mismatch")

    if result["aadhaar_match"]:
        st.success("✔ Aadhaar Verified")
    else:
        st.error("✘ Aadhaar Mismatch")

    if result["dob_match"]:
        st.success("✔ Date of Birth Verified")
    else:
        st.error("✘ Date of Birth Mismatch")

    st.divider()

    st.subheader("Remarks")

    for remark in result["remarks"]:
        st.write(f"• {remark}")

    st.divider()

    if result["status"] == "VERIFIED":
        st.success("🎉 Customer Identity Successfully Verified")

    elif result["status"] == "PARTIAL":
        st.warning("⚠️ Partial Verification Completed")

    else:
        st.error("🚨 Manual Verification Required")

    st.divider()

    # -------------------------------------------------------
    # Navigation
    # -------------------------------------------------------

    if st.button(
        "➡ Proceed to Fraud Detection",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/6_Fraud_Detection.py")