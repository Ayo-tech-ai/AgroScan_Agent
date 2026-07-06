# tools.py
from typing import Optional
from database import FarmRecordService
from config import DATABASE_NAME


# Initialize service
_farm_service = FarmRecordService(DATABASE_NAME)


# String coercion helpers
def _clean_numeric_string(value: str) -> str:
    """Clean currency symbols and whitespace from numeric strings."""
    cleaned = value.strip().lower()
    if cleaned in ("", "null", "none"):
        return None
    for symbol in ["₦", "$", ",", "naira", "usd"]:
        cleaned = cleaned.replace(symbol, "")
    return cleaned.strip()


def _to_int(value, field_name: str) -> Optional[int]:
    """Convert string or numeric value to int."""
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


def _to_float(value, field_name: str) -> Optional[float]:
    """Convert string or numeric value to float."""
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


# Tool functions
def record_daily_farm_data(
    crates_collected: Optional[str] = None,
    bird_count: Optional[str] = None,
    feed_consumed_kg: Optional[str] = None,
    expenses: Optional[str] = None,
    notes: Optional[str] = None,
    record_date: Optional[str] = None,
) -> dict:
    """
    Record or update daily poultry farm production.

    Use this action whenever the farmer provides daily production information.

    NOTE: All numeric fields are accepted as text and converted
    internally to numbers, to tolerate models that pass numeric
    values as strings.

    Business Rules:
    - If a record already exists for the date, it is updated.
    - If no record exists yet for the date, missing fields are
      inherited from the most recent prior record.
    - Revenue is calculated automatically.
    """
    parsed_crates = _to_int(crates_collected, "crates_collected")
    parsed_bird_count = _to_int(bird_count, "bird_count")
    parsed_feed = _to_float(feed_consumed_kg, "feed_consumed_kg")
    parsed_expenses = _to_float(expenses, "expenses")

    return _farm_service.record_daily_farm_data(
        crates_collected=parsed_crates,
        bird_count=parsed_bird_count,
        feed_consumed_kg=parsed_feed,
        expenses=parsed_expenses,
        notes=notes,
        record_date=record_date,
    )


def get_farm_record(record_date: str) -> dict:
    """
    Retrieve the farm record for one exact calendar date.

    Use this when the farmer asks about a SPECIFIC date.
    Performs an EXACT match only.

    Args:
        record_date: The exact date to look up, in YYYY-MM-DD format.
    """
    record = _farm_service.get_record_by_date(record_date)

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


def get_most_recent_farm_record() -> dict:
    """
    Retrieve the single most recent farm record.

    Use this when the farmer asks for their "last" or "most recent" record.
    """
    record = _farm_service.get_most_recent_record()

    if record is None:
        return {"found": False, "message": "No farm records exist yet."}

    return {"found": True, "record": record}


def get_farm_summary(start_date: str, end_date: str) -> dict:
    """
    Get a summary of farm performance over a date range.

    Returns total crates, feed, revenue, expenses, net profit, and days_recorded.

    Args:
        start_date: Start of the range, in YYYY-MM-DD format.
        end_date: End of the range, in YYYY-MM-DD format.
    """
    return _farm_service.get_summary(start_date, end_date)
