import streamlit as st
import pandas as pd

from utils.session import require_staff

from database.dashboard_repository import (
    get_dashboard_stats,
    get_recent_applications,
)

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)

require_staff()

st.title("📊 AI Loan Management Dashboard")

stats = get_dashboard_stats()

# ---------------------------
# KPI Cards
# ---------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Applications", stats["total"])
col2.metric("Approved", stats["approved"])
col3.metric("Rejected", stats["rejected"])
col4.metric("Manual Review", stats["manual_review"])
col5.metric("Fraud Cases", stats["fraud"])

st.divider()

# ======================================
# ADD THE CHART HERE
# ======================================

st.subheader("📈 Loan Status Overview")

chart_data = pd.DataFrame(
    {
        "Status": [
            "Approved",
            "Rejected",
            "Manual Review",
        ],
        "Count": [
            stats["approved"],
            stats["rejected"],
            stats["manual_review"],
        ],
    }
)

st.bar_chart(
    chart_data.set_index("Status")
)

st.divider()

# ======================================
# RECENT APPLICATIONS
# ======================================

st.subheader("Recent Applications")

rows = get_recent_applications()

if rows:

    df = pd.DataFrame([dict(row) for row in rows])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("No applications available.")