"""
app.py

Streamlit application for AgroScan AI Farm Manager.
"""

import uuid
import streamlit as st

from database import initialize_database
from agent import (
    create_runner,
    create_session_service,
)


# ============================================================
# Streamlit Page Configuration
# ============================================================

st.set_page_config(
    page_title="AgroScan AI",
    page_icon="🐔",
    layout="wide",
)

st.title("🐔 AgroScan AI Farm Manager")

st.caption(
    "Your intelligent poultry farm management assistant."
)


# ============================================================
# One-Time Database Initialization
# ============================================================

if "database_initialized" not in st.session_state:

    initialize_database()

    st.session_state.database_initialized = True


# ============================================================
# User Identity
# ============================================================

if "user_id" not in st.session_state:

    st.session_state.user_id = str(
        uuid.uuid4()
    )


# ============================================================
# ADK Initialization
# ============================================================

if "session_service" not in st.session_state:

    session_service = create_session_service()

    session = session_service.create_session_sync(

        app_name="agroscan_app",

        user_id=st.session_state.user_id,

    )

    runner = create_runner(session_service)

    st.session_state.session_service = session_service

    st.session_state.session = session

    st.session_state.runner = runner


# ============================================================
# Chat History
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [

        {

            "role": "assistant",

            "content":
                "👋 Hello! I'm AgroScan AI Farm Manager.\n\n"
                "How can I assist you with your poultry farm today?"

        }

    ]
  
import asyncio


# ============================================================
# Agent Communication
# ============================================================

async def _ask_agent(message: str):
    """
    Send a message to the ADK runner and return
    the assistant's final response.
    """

    events = await st.session_state.runner.run_async(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session.id,
        new_message=message,
    )

    final_response = "I'm sorry, I couldn't generate a response."

    for event in events:

        if (
            event.content
            and event.content.parts
        ):

            texts = [
                part.text
                for part in event.content.parts
                if getattr(part, "text", None)
            ]

            if texts:
                final_response = " ".join(texts)

    return final_response


def ask_agent(message: str):
    """
    Synchronous wrapper around the async ADK call.
    """

    return asyncio.run(
        _ask_agent(message)
    )

# ============================================================
# Display Previous Messages
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# Chat Input
# ============================================================

prompt = st.chat_input(
    "Ask AgroScan AI about your poultry farm..."
)

if prompt:

    # --------------------------------------------
    # Display user message
    # --------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # --------------------------------------------
    # Generate assistant response
    # --------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("AgroScan AI is thinking..."):

            try:

                response = ask_agent(prompt)

            except Exception as e:

                response = (
                    "An unexpected error occurred.\n\n"
                    f"**Details:** {str(e)}"
                )

            st.markdown(response)

    # --------------------------------------------
    # Save assistant response
    # --------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )
  
# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("🐔 AgroScan AI")

    st.markdown(
        """
AgroScan AI is an intelligent poultry farm management assistant.

You can ask it to:

- Record daily farm production
- Retrieve historical records
- View the latest farm record
- Generate farm summaries
- Answer questions about your farm records
"""
    )

    st.divider()

    # --------------------------------------------
    # New Conversation
    # --------------------------------------------

    if st.button(
        "🔄 New Conversation",
        use_container_width=True,
    ):

        session_service = create_session_service()

        session = session_service.create_session_sync(
            app_name="agroscan_app",
            user_id=st.session_state.user_id,
        )

        runner = create_runner(session_service)

        st.session_state.session_service = session_service
        st.session_state.session = session
        st.session_state.runner = runner

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm AgroScan AI Farm Manager.\n\n"
                    "How can I assist you with your poultry farm today?"
                ),
            }
        ]

        st.rerun()

    st.divider()

    st.subheader("Session Information")

    st.caption(f"User ID: {st.session_state.user_id}")

    st.caption(
        f"Session ID: {st.session_state.session.id}"
    )

    st.divider()

    st.success("✅ Database Ready")

    st.success("✅ Agent Ready")

    st.success("✅ Session Active")
