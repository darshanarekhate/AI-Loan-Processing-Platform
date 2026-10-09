import streamlit as st

from langchain_app.auth import authenticate_user
from database.authorization_repository import (
    get_applications_by_customer_id,
)
from utils.session import (
    STAFF_ROLES,
    ensure_database,
    logout,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Loan System",
    page_icon="🏦",
    layout="wide",
)

ensure_database()


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

for key, default in {
    "authenticated": False,
    "username": None,
    "role": None,
    "customer_id": None,
    "application_id": None,
}.items():
    st.session_state.setdefault(key, default)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.authenticated:

    st.title("🏦 AI Loan Processing System")

    st.subheader("🔐 Login")

    with st.form("login_form"):

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    st.caption(
        "No account yet? Create one with "
        "`python -m scripts.create_user --role admin`."
    )

    if login_button:

        if not username or not password:

            st.error(
                "Please enter both username and password."
            )
            st.stop()

        user = authenticate_user(
            username=username.strip(),
            password=password,
        )

        if not user:

            # Same message for unknown user and wrong password so
            # usernames cannot be enumerated.
            st.error(
                "❌ Invalid username or password."
            )
            st.stop()

        application_id = None

        # ----------------------------------------------------
        # Customers are bound to their own applications;
        # staff (admin / officer) can work on any application.
        # ----------------------------------------------------

        if user["role"] not in STAFF_ROLES:

            applications = get_applications_by_customer_id(
                user["customer_id"]
            )

            if not applications:

                st.error(
                    "❌ No loan applications are associated "
                    "with this customer."
                )
                st.stop()

            application_id = applications[0]["application_id"]

        st.session_state.authenticated = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.session_state.customer_id = user["customer_id"]
        st.session_state.application_id = application_id

        st.rerun()

    st.stop()


# ============================================================
# AUTHENTICATED HOME PAGE
# ============================================================

st.title("🏦 AI Loan Processing System")

st.success(
    f"Welcome, **{st.session_state.username}**!"
)

if st.session_state.role in STAFF_ROLES:

    st.info(f"Role: {st.session_state.role.title()}")

    st.markdown(
        """
### Loan processing workflow

1. **Customer Registration** or **Existing Customer** lookup
2. **Loan Application** (amount, income, tenure, credit score)
3. **Upload Documents** → **OCR Processing**
4. **KYC Verification** → **Fraud Detection**
5. **AI Loan Decision** → **Loan Report**

Use the sidebar to open each step, and the dashboards for analytics.
"""
    )

else:

    st.info(
        f"Customer ID: {st.session_state.customer_id}"
    )

    st.info(
        f"Application ID: {st.session_state.application_id}"
    )

    st.markdown(
        "Open **AI Loan Assistant** in the sidebar to ask about your "
        "application, or **Application Tracker** to follow its progress."
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True,
):

    logout()

    st.rerun()
