import streamlit as st

from langchain_app.agent_service import ask_agent


st.set_page_config(
    page_title="AI Loan Assistant",
    page_icon="🤖",
)

st.title("🤖 AI Loan Assistant")

st.write(
    "Ask questions about your loan application."
)

application_id = st.session_state.get("application_id")
customer_id = st.session_state.get("customer_id")

if not application_id or not customer_id:
    st.error("No active loan application found.")
    st.stop()

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