import streamlit as st
from database.authorization_repository import is_application_authorized
from services.tracker_service import get_application_journey
from utils.session import is_staff, require_login

st.set_page_config(page_title="Application Tracker", layout="wide")

require_login()

st.title("📌 AI Loan Application Tracker")
st.caption("Track the complete processing journey of a loan application.")

application_id = st.text_input(
    "Enter Application ID",
    value=st.session_state.get("application_id") or "",
    placeholder="Example: APP-4FE3EF66"
).strip()

if st.button("🔍 Search", use_container_width=True):

    if not application_id:
        st.warning("Please enter an Application ID.")
        st.stop()

    # Customers may only track their own applications.
    if not is_staff() and not is_application_authorized(
        application_id,
        st.session_state.get("customer_id"),
    ):
        st.error("Application ID not found.")
        st.stop()

    application, stages = get_application_journey(application_id)

    if not application:
        st.error("Application ID not found.")
        st.stop()

    (
        app_id,
        customer_name,
        loan_type,
        loan_amount,
        monthly_income,
        credit_score,
        application_status,
        risk_level,
        created_at
    ) = application

    st.subheader("Customer Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Customer", customer_name)

    with col2:
        st.metric("Loan Type", loan_type)

    with col3:
        st.metric("Application ID", app_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Loan Amount", f"Rs. {loan_amount:,.0f}")

    with col2:
        st.metric("Monthly Income", f"Rs. {monthly_income:,.0f}")

    with col3:
        st.metric("Credit Score", credit_score)

    st.divider()

    st.subheader("Processing Journey")

    icon_map = {
        "COMPLETED": "✅",
        "APPROVED": "✅",
        "LOW_RISK": "🟢",
        "MEDIUM_RISK": "🟡",
        "HIGH_RISK": "🔴",
        "MANUAL_REVIEW": "⚠️",
        "REJECTED": "❌",
        "PENDING": "⏳"
    }

    for stage_name, stage_status, remarks, updated_at in stages:

        icon = icon_map.get(stage_status, "•")

        st.markdown(
            f"""
### {icon} {stage_name}

**Status:** {stage_status}

**Remarks:** {remarks}

**Updated:** {updated_at}
"""
        )

        st.divider()

    st.subheader("Current Status")

    if application_status == "APPROVED":
        st.success(f"✅ {application_status}")

    elif application_status == "REJECTED":
        st.error(f"❌ {application_status}")

    else:
        st.warning(application_status)

    st.info(f"Risk Level: {risk_level}")