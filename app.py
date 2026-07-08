import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import uuid
import os

from datetime import date, datetime
from typing import Optional

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.skills import models
from google.adk.tools import FunctionTool
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


# ============================================================
# PAGE CONFIG — must be the first Streamlit command in the script
# ============================================================
st.set_page_config(
    page_title="AgroScan AI Farm Manager",
    page_icon="🐔",
    layout="centered"
)


# ============================================================
# CUSTOM CSS - Professional Agricultural Theme
# ============================================================
def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
        
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
        
        .main {
            background: linear-gradient(135deg, #FEFCF3 0%, #F5F0E8 100%);
        }
        
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
        
        .harvest-header {
            background: linear-gradient(135deg, #2D5A27 0%, #4A7C3F 50%, #C49A3C 100%);
            padding: 2rem 2.5rem;
            border-radius: 20px;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(45, 90, 39, 0.25);
        }

        .harvest-header::before {
            content: "🐔";
            position: absolute;
            right: -10px;
            top: -30px;
            font-size: 140px;
            opacity: 0.08;
            transform: rotate(-15deg);
        }

        .harvest-header::after {
            content: "☀️";
            position: absolute;
            right: 60px;
            bottom: -20px;
            font-size: 80px;
            opacity: 0.06;
        }

        .harvest-header h1 {
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            color: #FFFFFF;
            font-size: 2.8rem;
            margin: 0;
            text-shadow: 0 2px 12px rgba(0,0,0,0.15);
            letter-spacing: -0.5px;
        }

        .harvest-header .subtitle {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            color: rgba(255,255,255,0.92);
            font-size: 1.1rem;
            margin: 0.2rem 0 0.5rem 0;
            opacity: 0.9;
        }

        .harvest-header .badge-container {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }

        .harvest-header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.18);
            backdrop-filter: blur(10px);
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        .harvest-divider {
            height: 4px;
            background: linear-gradient(90deg, #C49A3C, #4A7C3F, #2D5A27);
            border-radius: 4px;
            margin: 0.5rem 0 1.8rem 0;
            opacity: 0.6;
        }
        
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
            font-family: 'Inter', sans-serif !important;
        }
        
        .stDataFrame tbody tr {
            transition: all 0.2s ease !important;
        }
        
        .stDataFrame tbody tr:hover {
            background: #E8F5E9 !important;
        }
        
        .stDataFrame td {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.8rem !important;
        }
        
        hr {
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, #4CAF50, #A5D6A7, #4CAF50) !important;
            margin: 2rem 0 !important;
        }
        
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
        
        .stAlert {
            border-radius: 12px !important;
            border-left: 4px solid #2E7D32 !important;
            background: #E8F5E9 !important;
        }
        
        .stSpinner > div {
            border-color: #2E7D32 !important;
            border-right-color: transparent !important;
        }
        
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
        
        @media (max-width: 768px) {
            .harvest-header h1 {
                font-size: 2rem !important;
            }
            .harvest-header {
                padding: 1.5rem !important;
            }
            section[data-testid="stSidebar"] {
                padding: 1rem !important;
            }
        }
        
        .welcome-container {
            text-align: center;
            padding: 2.5rem 1.5rem;
            background: #FFFFFF;
            border-radius: 20px;
            border: 1px solid rgba(46, 125, 50, 0.1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }
        
        .welcome-container .icon {
            font-size: 3.5rem;
            margin-bottom: 0.5rem;
        }
        
        .welcome-container h3 {
            font-family: 'Playfair Display', serif;
            color: #2D5A27;
            font-size: 1.8rem;
            margin: 0.5rem 0;
        }
        
        .welcome-container p {
            color: #5A5A5A;
            max-width: 500px;
            margin: 0.5rem auto;
        }
        
        .welcome-tags {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 1.2rem;
        }
        
        .welcome-tags span {
            background: #F8F4EA;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #2D5A27;
            font-weight: 500;
            border: 1px solid rgba(46, 125, 50, 0.1);
        }
        
        .agroscan-sidebar-footer {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 0.8rem;
            border-top: 1px dashed rgba(255,255,255,0.15);
        }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
apply_custom_css()


# ============================================================
# CONSTANTS
# ============================================================
DATABASE_NAME = "agroscan.db"
EXCEL_FILE = "agroscan_farm_records_july2025_june2026.xlsx"


# ============================================================
# FarmRecordService - MOVED TO TOP LEVEL
# ============================================================
class FarmRecordService:
    CRATE_PRICE = 3500

    def __init__(self, database_name):
        self.database_name = database_name

    def get_connection(self):
        return sqlite3.connect(self.database_name)

    def get_total_records(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM farm_records")
        total = cursor.fetchone()[0]
        connection.close()
        return total

    def record_exists(self, record_date):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM farm_records WHERE record_date=?",
            (record_date,)
        )
        exists = cursor.fetchone()[0] > 0
        connection.close()
        return exists

    def get_record_by_date(self, record_date):
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM farm_records WHERE record_date=?",
            (record_date,)
        )
        row = cursor.fetchone()
        connection.close()
        return dict(row) if row else None

    def get_previous_record(self, record_date):
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM farm_records
            WHERE record_date < ?
            ORDER BY record_date DESC
            LIMIT 1
            """,
            (record_date,)
        )
        row = cursor.fetchone()
        connection.close()
        return dict(row) if row else None

    def get_most_recent_record(self):
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM farm_records
            ORDER BY record_date DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        connection.close()
        return dict(row) if row else None

    def get_summary(self, start_date, end_date):
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS days_recorded,
                COALESCE(SUM(crates_collected), 0) AS total_crates,
                COALESCE(SUM(feed_consumed_kg), 0) AS total_feed_kg,
                COALESCE(SUM(revenue), 0) AS total_revenue,
                COALESCE(SUM(expenses), 0) AS total_expenses
            FROM farm_records
            WHERE record_date BETWEEN ? AND ?
            """,
            (start_date, end_date)
        )
        row = cursor.fetchone()
        connection.close()

        result = dict(row)
        result["net_profit"] = result["total_revenue"] - result["total_expenses"]
        result["start_date"] = start_date
        result["end_date"] = end_date
        return result

    def get_all_records(self):
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM farm_records ORDER BY record_date")
        rows = cursor.fetchall()
        connection.close()
        return [dict(row) for row in rows]

    def validate_daily_record(self, bird_count, crates_collected):
        eggs = crates_collected * 30
        maximum_eggs = bird_count * 0.95
        if eggs > maximum_eggs:
            return (
                False,
                f"{crates_collected} crates ({eggs} eggs) appears "
                f"unrealistic for {bird_count} birds."
            )
        return True, "Validation passed."

    def record_daily_farm_data(
        self, crates_collected=None, bird_count=None,
        feed_consumed_kg=None, expenses=None,
        notes=None, record_date=None
    ):
        if record_date is None:
            record_date = date.today().isoformat()

        existing_record = self.get_record_by_date(record_date)
        previous_day_record = self.get_previous_record(record_date)

        reference_record = existing_record or previous_day_record

        if reference_record:
            if crates_collected is None:
                crates_collected = reference_record["crates_collected"]
            if bird_count is None:
                bird_count = reference_record["bird_count"]
            if feed_consumed_kg is None:
                feed_consumed_kg = reference_record["feed_consumed_kg"]
            if expenses is None:
                expenses = reference_record["expenses"]
            if notes is None:
                notes = reference_record["notes"]
        else:
            if crates_collected is None:
                raise ValueError("crates_collected is required for the first record.")
            if bird_count is None:
                raise ValueError("bird_count is required for the first record.")
            if feed_consumed_kg is None:
                raise ValueError("feed_consumed_kg is required for the first record.")
            if expenses is None:
                raise ValueError("expenses is required for the first record.")

        revenue = crates_collected * self.CRATE_PRICE

        valid, message = self.validate_daily_record(bird_count, crates_collected)
        if not valid:
            return {"success": False, "message": message}

        connection = self.get_connection()
        cursor = connection.cursor()

        if existing_record:
            cursor.execute(
                """
                UPDATE farm_records
                SET bird_count=?, crates_collected=?, feed_consumed_kg=?,
                    revenue=?, expenses=?, notes=?
                WHERE record_date=?
                """,
                (bird_count, crates_collected, feed_consumed_kg,
                 revenue, expenses, notes, record_date)
            )
            action = "updated"
        else:
            cursor.execute(
                """
                INSERT INTO farm_records(
                    record_date, bird_count, crates_collected,
                    feed_consumed_kg, revenue, expenses, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (record_date, bird_count, crates_collected,
                 feed_consumed_kg, revenue, expenses, notes)
            )
            action = "recorded"

        connection.commit()
        connection.close()

        return {
            "success": True,
            "action": action,
            "record_date": record_date,
            "previous_values": existing_record,
            "bird_count": bird_count,
            "crates_collected": crates_collected,
            "feed_consumed_kg": feed_consumed_kg,
            "revenue": revenue,
            "expenses": expenses,
            "notes": notes,
            "message": f"Farm record successfully {action}."
        }


# ============================================================
# DATABASE INITIALIZATION FUNCTIONS
# ============================================================

def create_farm_records_table():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farm_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_date DATE UNIQUE NOT NULL,
        bird_count INTEGER NOT NULL,
        crates_collected INTEGER NOT NULL,
        feed_consumed_kg REAL NOT NULL,
        revenue REAL NOT NULL,
        expenses REAL NOT NULL,
        notes TEXT
    );
    """)
    connection.commit()
    connection.close()


def initialize_farm_record_book(excel_path):
    df = pd.read_excel(excel_path)
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    imported = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
            INSERT INTO farm_records (
                record_date, bird_count, crates_collected,
                feed_consumed_kg, revenue, expenses, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row["record_date"]),
                int(row["bird_count"]),
                int(row["crates_collected"]),
                float(row["feed_consumed_kg"]),
                float(row["revenue"]),
                float(row["expenses"]),
                row["notes"] if pd.notna(row["notes"]) else None
            ))
            imported += 1
        except sqlite3.IntegrityError:
            skipped += 1

    connection.commit()
    connection.close()
    return imported, skipped


def get_record_count():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM farm_records")
    count = cursor.fetchone()[0]
    connection.close()
    return count


# Run database setup on every cold start (not per-session).
create_farm_records_table()

if get_record_count() == 0:
    _imported, _skipped = initialize_farm_record_book(EXCEL_FILE)
    st.session_state.import_summary = f"Imported {_imported} historical records."
else:
    st.session_state.setdefault("import_summary", None)


# ============================================================
# ONE-TIME AGENT/RUNNER SETUP
# ============================================================

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:

    # --------------------------------------------------------
    # SKILL 1 — Farm Manager Core
    # --------------------------------------------------------
    farm_manager_core_skill = models.Skill(

        frontmatter=models.Frontmatter(
            name="farm-manager-core",
            description=(
                "Defines AgroScan AI Farm Manager's identity, "
                "communication style and overall user experience."
            ),
        ),

        instructions="""
You are AgroScan AI Farm Manager.

You are the intelligent virtual manager of a poultry farm.

Your responsibility is to coordinate AgroScan's capabilities
to help farmers manage their farms through natural conversation.

Communication Style

• Friendly
• Professional
• Practical
• Clear
• Confident

Never mention:

• Skills
• Tools
• Tool calls
• Internal reasoning
• System architecture

Remain in character as AgroScan AI Farm Manager.

For greetings:

Introduce yourself warmly and briefly explain how you can help.

For casual conversation:

Respond naturally without referring to yourself as
an AI model, language model or ChatGPT.

If the farmer requests a capability that AgroScan does not
yet support, politely explain that it will be available in
a future version.

Never invent farm records or agricultural information.
""",

        resources=models.Resources(
            references={
                "identity.md": """
# AgroScan AI Farm Manager

AgroScan is an intelligent poultry farm management system.

Its goal is to help poultry farmers through natural conversation,
while internally coordinating multiple specialised capabilities.
"""
            }
        )
    )

    # --------------------------------------------------------
    # SKILL 2 — Farm Record Management
    # --------------------------------------------------------
    farm_record_skill = models.Skill(

        frontmatter=models.Frontmatter(
            name="farm-record-management",
            description=(
                "Records and manages daily poultry farm production "
                "records and historical farm data."
            ),
        ),

        instructions="""
You are AgroScan's Farm Record Specialist.

Your responsibility is maintaining the farm record book.

RECORDING DATA

When the farmer provides daily production information, call the
record_daily_farm_data tool. Only include the fields the farmer
actually mentioned — omit anything they didn't state.

The tool's result includes an "action" field ("recorded" or
"updated") and a "previous_values" field. When reporting back:

• If action is "recorded", clearly state a new record was created.
• If action is "updated", explicitly name which field(s) changed,
  comparing "previous_values" to the new values. Do not just repeat
  the full record — call out what is actually different.

Missing values inherit from today's own existing record if one
exists, otherwise from the most recent prior record.

LOOKING UP A SINGLE RECORD

You have two distinct tools for retrieving past data:

• get_farm_record(record_date) — use this for a SPECIFIC date,
  including relative terms like "yesterday", "last Tuesday", or
  "the 3rd of July" once you have converted them into an exact
  YYYY-MM-DD date. This is an EXACT match only. If it reports
  found=False, tell the farmer honestly that no record exists for
  that exact date. Never substitute a different date's data.

• get_most_recent_farm_record() — use this when the farmer asks for
  their "last" or "most recent" record without naming a specific
  date. This always returns the latest entry that exists, whatever
  date that is.

SUMMARIZING A PERIOD

• get_farm_summary(start_date, end_date) — use this when the farmer
  asks about totals or profit/loss over a period. Convert relative
  periods (this month, last week, etc.) into exact start and end
  dates before calling this tool.

The result includes total_crates, total_feed_kg, total_revenue,
total_expenses, net_profit, and days_recorded. ALWAYS check
days_recorded first: if it is 0, no data exists for that period at
all — say so honestly rather than reporting a profit/loss of zero as
if it were real performance.

GENERAL RULES

All monetary values must be reported using the ₦ (Naira) symbol,
never $ or any other currency symbol.

Revenue is calculated automatically.

Only one record should exist for each day.

Never invent production figures.

Never invent revenue.

Never simulate tool execution.

Always wait for the tool result before responding.

If the tool reports an error, communicate that error honestly.
"""
    )

    # --------------------------------------------------------
    # STRING-COERCION HELPERS
    # --------------------------------------------------------

    def _clean_numeric_string(value):
        cleaned = value.strip().lower()
        if cleaned in ("", "null", "none"):
            return None
        for symbol in ["₦", "$", ",", "naira", "usd"]:
            cleaned = cleaned.replace(symbol, "")
        return cleaned.strip()

    def _to_int(value, field_name):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = _clean_numeric_string(value)
            if cleaned is None or cleaned == "":
                return None
            try:
                return int(float(cleaned))
            except ValueError:
                raise ValueError(f"Could not interpret '{value}' as a whole number for {field_name}.")
        return int(value)

    def _to_float(value, field_name):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = _clean_numeric_string(value)
            if cleaned is None or cleaned == "":
                return None
            try:
                return float(cleaned)
            except ValueError:
                raise ValueError(f"Could not interpret '{value}' as a number for {field_name}.")
        return float(value)

    # --------------------------------------------------------
    # AGENT ACTION 1 — Record or update daily farm data
    # --------------------------------------------------------

    def record_daily_farm_data(
        crates_collected: Optional[str] = None,
        bird_count: Optional[str] = None,
        feed_consumed_kg: Optional[str] = None,
        expenses: Optional[str] = None,
        notes: Optional[str] = None,
        record_date: Optional[str] = None,
    ):
        parsed_crates = _to_int(crates_collected, "crates_collected")
        parsed_bird_count = _to_int(bird_count, "bird_count")
        parsed_feed = _to_float(feed_consumed_kg, "feed_consumed_kg")
        parsed_expenses = _to_float(expenses, "expenses")

        farm_service = FarmRecordService(DATABASE_NAME)
        return farm_service.record_daily_farm_data(
            crates_collected=parsed_crates,
            bird_count=parsed_bird_count,
            feed_consumed_kg=parsed_feed,
            expenses=parsed_expenses,
            notes=notes,
            record_date=record_date,
        )

    # --------------------------------------------------------
    # AGENT ACTION 2 — Exact-date lookup
    # --------------------------------------------------------

    def get_farm_record(record_date: str):
        farm_service = FarmRecordService(DATABASE_NAME)
        record = farm_service.get_record_by_date(record_date)

        if record is None:
            return {
                "found": False,
                "record_date": record_date,
                "message": f"No farm record was found for {record_date}."
            }

        return {
            "found": True,
            "record_date": record_date,
            "record": record
        }

    # --------------------------------------------------------
    # AGENT ACTION 3 — Most recent record
    # --------------------------------------------------------

    def get_most_recent_farm_record():
        farm_service = FarmRecordService(DATABASE_NAME)
        record = farm_service.get_most_recent_record()

        if record is None:
            return {"found": False, "message": "No farm records exist yet."}

        return {"found": True, "record": record}

    # --------------------------------------------------------
    # AGENT ACTION 4 — Period summary
    # --------------------------------------------------------

    def get_farm_summary(start_date: str, end_date: str):
        farm_service = FarmRecordService(DATABASE_NAME)
        return farm_service.get_summary(start_date, end_date)

    # --------------------------------------------------------
    # WRAP AS ADK TOOLS
    # --------------------------------------------------------

    farm_record_tool = FunctionTool(record_daily_farm_data)
    farm_record_lookup_tool = FunctionTool(get_farm_record)
    most_recent_record_tool = FunctionTool(get_most_recent_farm_record)
    farm_summary_tool = FunctionTool(get_farm_summary)

    # --------------------------------------------------------
    # COMBINED SKILLTOOLSET
    # --------------------------------------------------------

    agroscan_toolset = SkillToolset(
        skills=[
            farm_manager_core_skill,
            farm_record_skill,
        ],
        additional_tools=[]
    )

    # --------------------------------------------------------
    # LOAD GROQ API KEY FROM STREAMLIT SECRETS
    # --------------------------------------------------------

    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

    # --------------------------------------------------------
    # AGENT
    # --------------------------------------------------------

    today_str = date.today().isoformat()

    farm_manager_agent = Agent(

        model=LiteLlm(
            model="groq/meta-llama/llama-4-scout-17b-16e-instruct"
        ),

        name="farm_manager",

        description=(
            "An intelligent poultry farm management system "
            "that assists farmers using specialized capabilities."
        ),

        instruction=f"""
You are AgroScan AI Farm Manager.

You are the single point of interaction for the farmer.

Today's date is {today_str}. Use this to resolve any relative date
or period the farmer mentions (e.g. "yesterday", "this month", "last
week", "three days ago") into exact YYYY-MM-DD date(s) BEFORE calling
any tool. Tools only accept exact dates — never pass a relative term
directly to a tool.

Your responsibility is to help manage poultry farms by
using the available Skills and Tools behind the scenes.

GENERAL RULES

• Never expose internal implementation details.

• Never mention Skills.

• Never mention Tool calls.

• Never mention FunctionTools.

• Never invent farm records.

• Never invent production figures.

• Never invent revenue.

• Treat the Farm Record Book as the single source of truth.

• To record or update daily farm data, call the
record_daily_farm_data tool directly. This tool is
always available.

• To look up a specific date's record, call get_farm_record
directly with an exact date. This tool is always available.

• To find the most recent record on file (when the farmer doesn't
name a specific date), call get_most_recent_farm_record directly.
This tool is always available.

• To summarize performance over a period (totals, profit/loss),
call get_farm_summary directly with an exact start and end date.
This tool is always available.

• All monetary values must be reported using the ₦ (Naira) symbol,
never $ or any other currency symbol.

• Load the farm-record-management skill to guide how you
interpret and communicate about farm records, lookups, and
summaries.

• Load the farm-manager-core skill to guide your identity,
tone, and communication style.

• Never simulate tool execution.

• Wait for tool results before responding.

• If required information is missing,
ask only for the missing information.

Maintain a friendly, professional and practical tone.
""",

        tools=[
            farm_record_tool,
            farm_record_lookup_tool,
            most_recent_record_tool,
            farm_summary_tool,
            agroscan_toolset,
        ]
    )

    # --------------------------------------------------------
    # SESSION SERVICE, SESSION, AND RUNNER
    # --------------------------------------------------------

    session_service = InMemorySessionService()

    unique_user_id = str(uuid.uuid4())

    agroscan_session = session_service.create_session_sync(
        app_name="agroscan_app",
        user_id=unique_user_id
    )

    runner = Runner(
        app_name="agroscan_app",
        agent=farm_manager_agent,
        session_service=session_service
    )

    # --------------------------------------------------------
    # STORE EVERYTHING IN SESSION STATE
    # --------------------------------------------------------

    st.session_state.runner = runner
    st.session_state.session_service = session_service
    st.session_state.agroscan_session = agroscan_session
    st.session_state.user_id = unique_user_id
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
# BEAUTIFUL HEADER FROM SECOND APP.PY (with 🐔 instead of 🌾)
# ============================================================

st.markdown("""
<div class="harvest-header">
    <h1>🐔 AgroScan</h1>
    <div class="subtitle">Your Farm's Record Book — Poultry Management, Made Conversational</div>
    <div class="badge-container">
        <span class="badge">🚀 AI-Powered</span>
        <span class="badge">📊 Smart Analytics</span>
        <span class="badge">🌿 Sustainable Farming</span>
    </div>
</div>
<div class="harvest-divider"></div>
""", unsafe_allow_html=True)

if st.session_state.get("import_summary"):
    st.info(f"📖 {st.session_state.import_summary}")


# ============================================================
# SIDEBAR - DISPLAY FARM RECORDS (from first app.py)
# ============================================================

_sidebar_service = FarmRecordService(DATABASE_NAME)

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
    
    # Get all records
    all_records = _sidebar_service.get_all_records()
    
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
                record = _sidebar_service.get_record_by_date(selected_date_str)
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
    
    # Sidebar footer
    st.markdown(
        '<div class="agroscan-sidebar-footer">AgroScan AI Farm Manager<br>Built by Ayoola Tobi</div>',
        unsafe_allow_html=True
    )


# ============================================================
# RENDER EXISTING CHAT HISTORY
# ============================================================

if not st.session_state.chat_history:
    # Welcome message (from first app.py)
    st.markdown("""
    <div class="welcome-container">
        <div class="icon">🌾</div>
        <h3>Welcome to AgroScan AI!</h3>
        <p>Start a conversation to manage your poultry farm. I can help you record daily data, view farm performance, and provide insights about your operations.</p>
        <div class="welcome-tags">
            <span>📊 View records</span>
            <span>📝 Add daily data</span>
            <span>📈 Get summaries</span>
            <span>💰 Check profit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)


# ============================================================
# HANDLE NEW MESSAGE
# ============================================================

user_message = st.chat_input("💬 Talk to AgroScan about your farm...")

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
