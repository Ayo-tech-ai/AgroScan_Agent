"""
tools.py

Defines all ADK FunctionTools used by AgroScan AI.
"""

from typing import Optional

from google.adk.tools import FunctionTool

from services import (
    farm_service,
    _to_int,
    _to_float,
)


# ============================================================
# Record Daily Farm Data
# ============================================================

def record_daily_farm_data(
    crates_collected: Optional[str] = None,
    bird_count: Optional[str] = None,
    feed_consumed_kg: Optional[str] = None,
    expenses: Optional[str] = None,
    notes: Optional[str] = None,
    record_date: Optional[str] = None,
):
    """
    Record or update daily poultry farm production.
    """

    parsed_crates = _to_int(
        crates_collected,
        "crates_collected",
    )

    parsed_bird_count = _to_int(
        bird_count,
        "bird_count",
    )

    parsed_feed = _to_float(
        feed_consumed_kg,
        "feed_consumed_kg",
    )

    parsed_expenses = _to_float(
        expenses,
        "expenses",
    )

    return farm_service.record_daily_farm_data(
        crates_collected=parsed_crates,
        bird_count=parsed_bird_count,
        feed_consumed_kg=parsed_feed,
        expenses=parsed_expenses,
        notes=notes,
        record_date=record_date,
    )


# ============================================================
# Lookup One Record
# ============================================================

def get_farm_record(record_date: str):
    """
    Retrieve one exact farm record.
    """

    record = farm_service.get_record_by_date(
        record_date
    )

    if record is None:

        return {
            "found": False,
            "record_date": record_date,
            "message": (
                f"No farm record was found "
                f"for {record_date}."
            ),
        }

    return {
        "found": True,
        "record_date": record_date,
        "record": record,
    }


# ============================================================
# Most Recent Record
# ============================================================

def get_most_recent_farm_record():
    """
    Return the latest record available.
    """

    record = farm_service.get_most_recent_record()

    if record is None:

        return {
            "found": False,
            "message": "No farm records exist yet.",
        }

    return {
        "found": True,
        "record": record,
    }


# ============================================================
# Summary Tool
# ============================================================

def get_farm_summary(
    start_date: str,
    end_date: str,
):
    """
    Return farm summary over a date range.
    """

    return farm_service.get_summary(
        start_date,
        end_date,
    )


# ============================================================
# FunctionTools
# ============================================================

farm_record_tool = FunctionTool(
    record_daily_farm_data
)

farm_record_lookup_tool = FunctionTool(
    get_farm_record
)

most_recent_record_tool = FunctionTool(
    get_most_recent_farm_record
)

farm_summary_tool = FunctionTool(
    get_farm_summary
)
