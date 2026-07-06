# database.py
import sqlite3
import pandas as pd
from datetime import date
from typing import Optional, Dict, List, Any
from config import DATABASE_NAME, EXCEL_FILE, CRATE_PRICE


class FarmRecordService:
    """Service class for managing farm records in SQLite database."""

    def __init__(self, database_name: str = DATABASE_NAME):
        self.database_name = database_name
        self.CRATE_PRICE = CRATE_PRICE

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.database_name)

    def create_table(self) -> None:
        """Create the farm_records table if it doesn't exist."""
        connection = self.get_connection()
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

    def initialize_from_excel(self, excel_path: str) -> tuple[int, int]:
        """Import records from Excel file into database."""
        df = pd.read_excel(excel_path)
        connection = self.get_connection()
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

    def get_record_count(self) -> int:
        """Get total number of records in database."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM farm_records")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    def record_exists(self, record_date: str) -> bool:
        """Check if a record exists for a specific date."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM farm_records WHERE record_date=?",
            (record_date,)
        )
        exists = cursor.fetchone()[0] > 0
        connection.close()
        return exists

    def get_record_by_date(self, record_date: str) -> Optional[Dict[str, Any]]:
        """Get a single record by exact date."""
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

    def get_previous_record(self, record_date: str) -> Optional[Dict[str, Any]]:
        """Get the most recent record before a given date."""
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

    def get_most_recent_record(self) -> Optional[Dict[str, Any]]:
        """Get the single most recent record in the entire database."""
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

    def get_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get summary statistics for a date range."""
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

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records ordered by date."""
        connection = self.get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM farm_records ORDER BY record_date")
        rows = cursor.fetchall()
        connection.close()
        return [dict(row) for row in rows]

    def validate_daily_record(self, bird_count: int, crates_collected: int) -> tuple[bool, str]:
        """Validate daily production data."""
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
        self,
        crates_collected: Optional[int] = None,
        bird_count: Optional[int] = None,
        feed_consumed_kg: Optional[float] = None,
        expenses: Optional[float] = None,
        notes: Optional[str] = None,
        record_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record or update daily farm data."""
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


def initialize_database():
    """Initialize the database and import Excel data if empty."""
    service = FarmRecordService()
    service.create_table()
    
    if service.get_record_count() == 0:
        imported, skipped = service.initialize_from_excel(EXCEL_FILE)
        return f"Imported {imported} historical records."
    return None
