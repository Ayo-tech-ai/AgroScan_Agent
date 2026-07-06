"""
Configuration settings for AgroScan AI.
Handles API keys, model configuration, and reusable constants.
"""

import os
import streamlit as st

# -------------------------------------------------------------------
# Load API Keys
# -------------------------------------------------------------------

try:
    # Running on Streamlit Cloud
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    # Running locally
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Please add it to Streamlit Secrets or your local environment."
    )

# -------------------------------------------------------------------
# Environment Variables
# -------------------------------------------------------------------

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# -------------------------------------------------------------------
# Model Configuration
# -------------------------------------------------------------------

MODEL_NAME = "groq/meta-llama/llama-4-scout-17b-16e-instruct"

# -------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------

DATABASE_NAME = "agroscan.db"

EXCEL_FILE = "agroscan_farm_records_july2025_june2026.xlsx"
```
