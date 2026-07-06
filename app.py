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
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS - Professional Agricultural Theme
# ============================================================
def apply_custom_css():
    st.markdown("""
    <style>
        /* Import agricultural-friendly fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
        
        /* Main theme colors - Earthy agricultural palette */
        :root {
            --primary-green: #2E7D32;
            --primary-green-light: #4CAF50;
            --primary-green-dark: #1B5E20;
            --secondary-green: #66BB6A;
            --accent-gold: #F9A825;
            --accent-amber: #FFB300;
            --warm-brown: #6D4C41;
            --light-cream: #FEFCF3;
            --soft-beige: #F5F0E8;
            --dark-earth: #3E2723;
            --success-green: #43A047;
            --warning-amber: #FF8F00;
            --text-primary: #2C2C2C;
            --text-secondary: #5D4037;
        }
        
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #FEFCF3 0%, #F5F0E8 100%);
        }
        
        /* Sidebar styling - Woodland theme */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2E7D32 0%, #1B5E20 100%);
            color: white;
            padding: 2rem 1rem;
        }
        
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label {
            color: #E8F5E9 !important;
        }
        
        section[data-testid="stSidebar"] .stDateInput label {
            color: #E8F5E9 !important;
        }
        
        section[data-testid="stSidebar"] .stButton button {
            background: #F9A825 !important;
            color: #1B5E20 !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        section[data-testid="stSidebar"] .stButton button:hover {
            background: #FFB300 !important;
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(249, 168, 37, 0.3);
        }
        
        section[data-testid="stSidebar"] .stMetric {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        section[data-testid="stSidebar"] .stMetric label {
            color: #E8F5E9 !important;
            font-weight: 500;
        }
        
        section[data-testid="stSidebar"] .stMetric div {
            color: #FFFFFF !important;
            font-weight: 700;
        }
        
        /* Card styling for metrics in sidebar */
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        /* Main header styling */
        .main-header {
            background: linear-gradient(135deg, #2E7D32 0%, #43A047 50%, #66BB6A 100%);
            padding: 2rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(46, 125, 50, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: "🌾";
            position: absolute;
            right: -20px;
            top: -20px;
            font-size: 120px;
            opacity: 0.1;
        }
        
        .main-header h1 {
            color: white !important;
            font-family: 'Playfair Display', serif !important;
            font-weight: 700;
            font-size: 2.8rem !important;
            margin: 0;
            text-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .main-header p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            font-weight: 400;
        }
        
        .main-header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: white;
            margin-top: 0.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Chat message styling */
        .stChatMessage {
            border-radius: 16px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            border: 1px solid rgba(46, 125, 50, 0.1) !important;
        }
        
        .stChatMessage.user {
            background: #E8F5E9 !important;
            border-color: #A5D6A7 !important;
        }
        
        .stChatMessage.assistant {
            background: white !important;
            border-color: #E0E0E0 !important;
        }
        
        /* Input box styling */
        .stChatInput textarea {
            border-radius: 12px !important;
            border: 2px solid #A5D6A7 !important;
            padding: 12px !important;
            font-size: 1rem !important;
            background: white !important;
            transition: all 0.3s ease !important;
        }
        
        .stChatInput textarea:focus {
            border-color: #2E7D32 !important;
            box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1) !important;
        }
        
        /* Dataframe styling */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid rgba(46, 125, 50, 0.1) !important;
        }
        
        .stDataFrame thead tr th {
            background: #2E7D32 !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px !important;
        }
        
        .stDataFrame tbody tr {
            transition: all 0.2s ease !important;
        }
        
        .stDataFrame tbody tr:hover {
            background: #E8F5E9 !important;
        }
        
        /* Divider styling */
        hr {
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, #4CAF50, #A5D6A7, #4CAF50) !important;
            margin: 2rem 0 !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: #E8F5E9 !important;
            border-radius: 12px !important;
            border: 1px solid #A5D6A7 !important;
            font-weight: 600 !important;
            color: #2E7D32 !important;
        }
        
        .streamlit-expanderContent {
            background: white !important;
            border-radius: 0 0 12px 12px !important;
            border: 1px solid #A5D6A7 !important;
            border-top: none !important;
            padding: 16px !important;
        }
        
        /* Info box styling */
        .stAlert {
            border-radius: 12px !important;
            border-left: 4px solid #2E7D32 !important;
            background: #E8F5E9 !important;
        }
        
        /* Spinner styling */
        .stSpinner > div {
            border-color: #2E7D32 !important;
            border-right-color: transparent !important;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #F5F0E8;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #2E7D32;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem !important;
            }
            .main-header {
                padding: 1.5rem !important;
            }
            section[data-testid="stSidebar"] {
                padding: 1rem !important;
            }
        }
        
        /* Additional professional touches */
        .leaf-decoration {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 40px;
            opacity: 0.2;
            pointer-events: none;
        }
        
        .status-badge {
            display: inline-block;
            background: #43A047;
            color: white;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
apply_custom_css()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================
with st.spinner("🌱 Initializing database..."):
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
# SIDEBAR - DISPLAY FARM RECORDS WITH AGRICULTURAL THEME
# ============================================================
with st.sidebar:
    # Logo/Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">🌾</div>
        <h2 style="color: white; font-family: 'Playfair Display', serif; margin: 0;">
            Farm Records
        </h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0;">
            📊 Poultry Production Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Initialize farm service for data retrieval
    farm_service = FarmRecordService(DATABASE_NAME)
    
    # Get all records
    all_records = farm_service.get_all_records()
    
    if all_records:
        # Display summary stats with agricultural icons
        total_days = len(all_records)
        total_crates = sum(r["crates_collected"] for r in all_records)
        total_revenue = sum(r["revenue"] for r in all_records)
        total_expenses = sum(r["expenses"] for r in all_records)
        net_profit = total_revenue - total_expenses
        
        st.markdown("### 📈 Key Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📅 Days Recorded", f"{total_days}")
            st.metric("🥚 Total Crates", f"{total_crates:,}")
            st.metric("💰 Net Profit", f"₦{net_profit:,.2f}")
        with col2:
            st.metric("🐔 Total Revenue", f"₦{total_revenue:,.2f}")
            st.metric("💸 Total Expenses", f"₦{total_expenses:,.2f}")
            avg_crates = total_crates / total_days if total_days > 0 else 0
            st.metric("📊 Avg/Day", f"{avg_crates:.1f} crates")
        
        st.divider()
        
        # Date filter for records
        st.markdown("### 🔍 Filter Records")
        
        # Get min and max dates from records
        dates = [datetime.strptime(r["record_date"], "%Y-%m-%d").date() for r in all_records]
        min_date = min(dates)
        max_date = max(dates)
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("📅 From", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("📅 To", max_date, min_value=min_date, max_value=max_date)
        
        # Filter records by date range
        if start_date and end_date:
            filtered_records = [
                r for r in all_records
                if start_date <= datetime.strptime(r["record_date"], "%Y-%m-%d").date() <= end_date
            ]
        else:
            filtered_records = all_records
        
        # Display records count with leaf icon
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0;">
            <span style="color: rgba(255,255,255,0.7); font-size: 0.85rem;">🌿 Showing {len(filtered_records)} records</span>
        </div>
        """, unsafe_allow_html=True)
        
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
            df_display.columns = ["📅 Date", "🐔 Birds", "🥚 Crates", "🌾 Feed (kg)", "💰 Revenue", "💸 Expenses"]
            
            # Display as a table with scroll
            st.dataframe(
                df_display,
                use_container_width=True,
                height=350,
                hide_index=True
            )
            
            # Option to view full record details
            st.divider()
            st.markdown("### 📋 Record Details")
            
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
                        st.markdown(f"""
                        <div style="padding: 8px;">
                            <p><strong>📅 Date:</strong> {datetime.strptime(record['record_date'], '%Y-%m-%d').strftime('%B %d, %Y')}</p>
                            <p><strong>🐔 Bird Count:</strong> {record['bird_count']:,}</p>
                            <p><strong>🥚 Crates Collected:</strong> {record['crates_collected']:,}</p>
                            <p><strong>🌾 Feed Consumed:</strong> {record['feed_consumed_kg']:.2f} kg</p>
                            <p><strong>💰 Revenue:</strong> ₦{record['revenue']:,.2f}</p>
                            <p><strong>💸 Expenses:</strong> ₦{record['expenses']:,.2f}</p>
                            <p><strong>📊 Net:</strong> ₦{record['revenue'] - record['expenses']:,.2f}</p>
                            {f"<p><strong>📝 Notes:</strong> {record['notes']}</p>" if record.get('notes') else ""}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("🌱 No records in selected date range.")
        
        # Export option
        st.divider()
        if st.button("📥 Export to CSV", use_container_width=True):
            if all_records:
                export_df = pd.DataFrame(all_records)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"agroscan_records_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("🌱 No farm records available yet.")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                Start by adding your first record<br>
                through the chat below! 💬
            </p>
        </div>
        """, unsafe_allow_html=True)


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
# MAIN CONTENT AREA WITH AGRICULTURAL HEADER
# ============================================================
# Custom header with agricultural theme
st.markdown(f"""
<div class="main-header">
    <div style="position: relative; z-index: 1;">
        <h1>{APP_ICON} {APP_TITLE}</h1>
        <p>🌿 Your intelligent poultry farm management assistant</p>
        <span class="badge">🚀 AI-Powered • Smart Agriculture • Real-time Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("import_summary"):
    st.success(f"✅ {st.session_state.import_summary}")

st.divider()

# ============================================================
# RENDER CHAT HISTORY WITH IMPROVED STYLING
# ============================================================
if not st.session_state.chat_history:
    # Welcome message
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🌾</div>
        <h3 style="color: #2E7D32;">Welcome to AgroScan AI!</h3>
        <p style="color: #5D4037; max-width: 600px; margin: 0 auto;">
            Start a conversation to manage your poultry farm. I can help you record daily data, 
            view farm performance, and provide insights about your operations.
        </p>
        <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
            <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">📊 View records</span>
            <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">📝 Add daily data</span>
            <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">📈 Get summaries</span>
            <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">💰 Check profit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)


# ============================================================
# HANDLE NEW MESSAGE
# ============================================================
user_message = st.chat_input("💬 Ask AgroScan about your farm...")

if user_message:
    st.session_state.chat_history.append(("user", user_message))
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("🌱 AgroScan is analyzing..."):
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


# ============================================================
# FOOTER DECORATION
# ============================================================
st.markdown("""
<div style="position: fixed; bottom: 10px; right: 20px; font-size: 2rem; opacity: 0.1; pointer-events: none;">
    🌾
</div>
<div style="position: fixed; bottom: 10px; left: 20px; font-size: 2rem; opacity: 0.1; pointer-events: none;">
    🐔
</div>
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #A5D6A7; font-size: 0.75rem; opacity: 0.6;">
    AgroScan AI • Smart Poultry Farm Management • v1.0
</div>
""", unsafe_allow_html=True)
