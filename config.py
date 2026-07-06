# config.py
import os

# Database configuration
DATABASE_NAME = "agroscan.db"
EXCEL_FILE = "agroscan_farm_records_july2025_june2026.xlsx"

# Business rules
CRATE_PRICE = 3500  # Naira per crate

# Model configuration
MODEL_NAME = "groq/meta-llama/llama-4-scout-17b-16e-instruct"

# Environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# App configuration
APP_TITLE = "AgroScan AI Farm Manager"
APP_ICON = "🐔"
