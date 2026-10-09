"""
Streamlit session helpers: login guard, roles and database bootstrap.

Every page calls require_login() so that pages cannot be opened
directly by URL without authenticating on the Home page first.
"""

import streamlit as st

from database.schema import init_db


STAFF_ROLES = ("admin", "officer")
CUSTOMER_ROLE = "customer"


@st.cache_resource
def ensure_database():
    """
    Create / migrate the schema once per server process.
    """

    init_db()
    return True


def is_staff() -> bool:
    return st.session_state.get("role") in STAFF_ROLES


def require_login(roles=None):
    """
    Stop the page unless a user is logged in (and, when roles is
    given, has one of those roles).
    """

    ensure_database()

    if not st.session_state.get("authenticated"):
        st.warning("🔐 Please log in to continue.")
        st.page_link("app.py", label="Go to login", icon="🏠")
        st.stop()

    if roles and st.session_state.get("role") not in roles:
        st.error("⛔ You do not have permission to view this page.")
        st.stop()

    return {
        "username": st.session_state.get("username"),
        "role": st.session_state.get("role"),
        "customer_id": st.session_state.get("customer_id"),
    }


def require_staff():
    return require_login(roles=STAFF_ROLES)


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
