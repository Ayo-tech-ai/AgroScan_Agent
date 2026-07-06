# app.py
import streamlit as st
import asyncio
import pandas as pd
from datetime import date, datetime, timedelta

from config import APP_TITLE, APP_ICON, DATABASE_NAME
from database import initialize_database, FarmRecordService
from agent import create_agroscan_agent


# ============================================================
# PAGE CONFIG — must be the first Streamlit command
# ============================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"  # Changed to wide for better sidebar display
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
# SIDEBAR - DISPLAY FARM RECORDS
# ============================================================
with st.sidebar:
    st.title("📊 Farm Records")
    st.divider()
    
    # Initialize farm service for data retrieval
    farm_service = FarmRecordService(DATABASE_NAME)
    
    # Get all records
    all_records = farm_service.get_all_records()
    
    if all_records:
        # Display summary stats
        total_days = len(all_records)
        total_crates = sum(r["crates_collected"] for r in all_records)
        total_revenue = sum(r["revenue"] for r in all_records)
        total_expenses = sum(r["expenses"] for r in all_records)
        net_profit = total_revenue - total_expenses
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📅 Total Days", total_days)
            st.metric("📦 Total Crates", f"{total_crates:,}")
            st.metric("💰 Net Profit", f"₦{net_profit:,.2f}")
        with col2:
            st.metric("🐔 Total Revenue", f"₦{total_revenue:,.2f}")
            st.metric("💸 Total Expenses", f"₦{total_expenses:,.2f}")
            avg_crates = total_crates / total_days if total_days > 0 else 0
            st.metric("📊 Avg Crates/Day", f"{avg_crates:.1f}")
        
        st.divider()
        
        # Date filter for records
        st.subheader("🔍 Filter Records")
        
        # Get min and max dates from records
        dates = [datetime.strptime(r["record_date"], "%Y-%m-%d").date() for r in all_records]
        min_date = min(dates)
        max_date = max(dates)
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)
        
        # Filter records by date range
        if start_date and end_date:
            filtered_records = [
                r for r in all_records
                if start_date <= datetime.strptime(r["record_date"], "%Y-%m-%d").date() <= end_date
            ]
        else:
            filtered_records = all_records
        
        # Display records count
        st.caption(f"Showing {len(filtered_records)} records")
        
        # Convert to DataFrame for display
        if filtered_records:
            df = pd.DataFrame(filtered_records)
            df["record_date"] = pd.to_datetime(df["record_date"]).dt.strftime("%Y-%m-%d")
            
            # Select columns to display
            display_cols = ["record_date", "bird_count", "crates_collected", 
                           "feed_consumed_kg", "revenue", "expenses"]
            
            # Format currency columns
            df_display = df[display_cols].copy()
            df_display["revenue"] = df_display["revenue"].apply(lambda x: f"₦{x:,.2f}")
            df_display["expenses"] = df_display["expenses"].apply(lambda x: f"₦{x:,.2f}")
            
            # Rename columns for display
            df_display.columns = ["Date", "Birds", "Crates", "Feed (kg)", "Revenue", "Expenses"]
            
            # Display as a table with scroll
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Option to view full record details
            st.divider()
            st.subheader("📋 Record Details")
            
            # Dropdown to select a date
            selected_date_str = st.selectbox(
                "Select a date to view details",
                options=sorted([r["record_date"] for r in filtered_records], reverse=True),
                format_func=lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%B %d, %Y")
            )
            
            if selected_date_str:
                record = farm_service.get_record_by_date(selected_date_str)
                if record:
                    with st.expander("📄 Full Record Details", expanded=True):
                        st.write(f"**Date:** {datetime.strptime(record['record_date'], '%Y-%m-%d').strftime('%B %d, %Y')}")
                        st.write(f"**Bird Count:** {record['bird_count']:,}")
                        st.write(f"**Crates Collected:** {record['crates_collected']:,}")
                        st.write(f"**Feed Consumed:** {record['feed_consumed_kg']:.2f} kg")
                        st.write(f"**Revenue:** ₦{record['revenue']:,.2f}")
                        st.write(f"**Expenses:** ₦{record['expenses']:,.2f}")
                        st.write(f"**Net:** ₦{record['revenue'] - record['expenses']:,.2f}")
                        if record.get("notes"):
                            st.write(f"**Notes:** {record['notes']}")
        else:
            st.info("No records found in the selected date range.")
        
        # Export option
        st.divider()
        if st.button("📥 Export All Records to CSV", use_container_width=True):
            if all_records:
                export_df = pd.DataFrame(all_records)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"agroscan_records_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("No farm records available yet. Start by adding your first record!")


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
# MAIN CONTENT AREA
# ============================================================
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Your intelligent poultry farm management assistant")

if st.session_state.get("import_summary"):
    st.info(st.session_state.import_summary)

st.divider()

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
    st.rerun()
