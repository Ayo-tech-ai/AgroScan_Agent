# app.py
import streamlit as st
import asyncio
from datetime import date

from config import APP_TITLE, APP_ICON
from database import initialize_database
from agent import create_agroscan_agent


# ============================================================
# PAGE CONFIG — must be the first Streamlit command
# ============================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================
with st.spinner("Initializing database..."):
    import_summary = initialize_database()
    if import_summary:
        st.session_state.import_summary = import_summary
    else:
        st.session_state.setdefault("import_summary", None)


# ============================================================
# ONE-TIME AGENT/RUNNER SETUP
# ============================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    # Load API key from secrets
    groq_api_key = st.secrets["GROQ_API_KEY"]
    
    # Create agent and runner
    _, runner, session_service, user_id, agroscan_session = create_agroscan_agent(groq_api_key)
    
    # Store in session state
    st.session_state.runner = runner
    st.session_state.session_service = session_service
    st.session_state.agroscan_session = agroscan_session
    st.session_state.user_id = user_id
    st.session_state.chat_history = []
    st.session_state.initialized = True


# ============================================================
# ASYNC BRIDGE
# ============================================================
def run_agent_turn(message: str):
    return asyncio.run(
        st.session_state.runner.run_debug(
            message,
            user_id=st.session_state.user_id,
            session_id=st.session_state.agroscan_session.id,
            quiet=True
        )
    )


# ============================================================
# PAGE HEADER
# ============================================================
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Your intelligent poultry farm management assistant")

if st.session_state.get("import_summary"):
    st.info(st.session_state.import_summary)


# ============================================================
# RENDER CHAT HISTORY
# ============================================================
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)


# ============================================================
# HANDLE NEW MESSAGE
# ============================================================
user_message = st.chat_input("Talk to AgroScan about your farm...")

if user_message:
    st.session_state.chat_history.append(("user", user_message))
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("AgroScan is thinking..."):
            try:
                events = run_agent_turn(user_message)
                final_event = events[-1]

                if final_event.content and final_event.content.parts:
                    response = " ".join(
                        part.text
                        for part in final_event.content.parts
                        if part.text
                    )
                else:
                    response = "No response was generated."

            except Exception as e:
                response = (
                    "I ran into an issue processing that. "
                    "Could you try rephrasing, or ask again?"
                )
                st.session_state.setdefault("last_error", str(e))

            st.markdown(response)

    st.session_state.chat_history.append(("assistant", response))
