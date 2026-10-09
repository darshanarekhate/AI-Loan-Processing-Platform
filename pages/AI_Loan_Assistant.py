import streamlit as st

from database.authorization_repository import is_application_authorized
from langchain_app.agent_service import ask_agent
from utils.session import require_login


st.set_page_config(
    page_title="AI Loan Assistant",
    page_icon="🤖",
)

require_login()

st.title("🤖 AI Loan Assistant")

st.write(
    "Ask questions about your loan application."
)

application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")

if not application_id or not customer_id:
    st.error("No active loan application found.")
    st.stop()

# Defence in depth: the assistant's tools are scoped to this pair,
# so make sure the application really belongs to the customer.
if not is_application_authorized(application_id, customer_id):
    st.error("This application does not belong to the selected customer.")
    st.stop()

# Chat history belongs to one application; reset when it changes.
if st.session_state.get("chat_application_id") != application_id:
    st.session_state.messages = []
    st.session_state.chat_application_id = application_id

st.info(f"Application ID : {application_id}")

# ----------------------------------------------------
# Chat History
# ----------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------
# Chat Input
# ----------------------------------------------------

prompt = st.chat_input(
    "Ask something about your loan..."
)

if prompt:

    # Show user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Ask AI

    with st.spinner("🤖 AI is analysing your application..."):

        result = ask_agent(
            question=prompt,
            customer_id=customer_id,
            application_id=application_id,
        )

    # Display response

    if result["success"]:
        assistant_response = result["response"]
    else:
        assistant_response = result["error"]

    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )