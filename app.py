import streamlit as st

from langchain_app.auth import authenticate_user
from database.authorization_repository import (
    get_applications_by_customer_id,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Loan System",
    page_icon="🏦",
    layout="wide",
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "application_id" not in st.session_state:
    st.session_state.application_id = None


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

    if login_button:

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not username or not password:

            st.error(
                "Please enter both username and password."
            )

        else:

            # ------------------------------------------------
            # Authenticate user
            # ------------------------------------------------

            user = authenticate_user(
                username=username,
                password=password,
            )

            if user:

                # --------------------------------------------
                # Store authenticated user information
                # --------------------------------------------

                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.customer_id = user["customer_id"]

                # --------------------------------------------
                # Load applications belonging to this customer
                # --------------------------------------------

                applications = get_applications_by_customer_id(
                    user["customer_id"]
                )

                # --------------------------------------------
                # Authorization check
                # --------------------------------------------

                if not applications:

                    st.error(
                        "❌ No loan applications are associated "
                        "with this customer."
                    )

                    # Clear authentication state
                    st.session_state.authenticated = False
                    st.session_state.username = None
                    st.session_state.customer_id = None
                    st.session_state.application_id = None

                    st.stop()

                # --------------------------------------------
                # Select first authorized application
                # --------------------------------------------

                st.session_state.application_id = (
                    applications[0]["application_id"]
                )

                st.success(
                    "✅ Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "❌ Invalid username or password."
                )

    st.stop()


# ============================================================
# AUTHENTICATED HOME PAGE
# ============================================================

st.title("🏦 AI Loan Processing System")

st.success(
    f"Welcome, **{st.session_state.username}**!"
)

st.write(
    "You are successfully authenticated."
)


# ============================================================
# USER INFORMATION
# ============================================================

st.info(
    f"Customer ID: {st.session_state.customer_id}"
)


# ============================================================
# CURRENT AUTHORIZED APPLICATION
# ============================================================

st.info(
    f"Application ID: {st.session_state.application_id}"
)


st.markdown("---")


# ============================================================
# AVAILABLE MODULES
# ============================================================

st.subheader("Available Modules")

st.write(
    """
Use the sidebar to navigate through the available
loan-processing modules.
"""
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

st.sidebar.info(
    f"Customer ID:\n{st.session_state.customer_id}"
)

st.sidebar.info(
    f"Application ID:\n{st.session_state.application_id}"
)


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True,
):

    # Clear authentication information
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.customer_id = None
    st.session_state.application_id = None

    # Clear chat history if present
    if "messages" in st.session_state:
        st.session_state.messages = []

    st.rerun()