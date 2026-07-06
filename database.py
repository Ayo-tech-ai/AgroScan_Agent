```python
"""
database.py

Handles database creation, table initialization,
and importing the initial farm records from Excel.
"""

import sqlite3
import pandas as pd

from config import DATABASE_NAME, EXCEL_FILE


def get_connection():
    """
    Create and return a SQLite connection.
    """
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """
    Create all required database tables if they do not already exist.
    """

    connection = get_connection()
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


def import_excel_data():
    """
    Import historical farm records from the Excel workbook.

    Duplicate dates are skipped automatically.
    """

    df = pd.read_excel(EXCEL_FILE)

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        try:

            cursor.execute(
                """
                INSERT INTO farm_records (
                    record_date,
                    bird_count,
                    crates_collected,
                    feed_consumed_kg,
                    revenue,
                    expenses,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(row["record_date"]),
                    int(row["bird_count"]),
                    int(row["crates_collected"]),
                    float(row["feed_consumed_kg"]),
                    float(row["revenue"]),
                    float(row["expenses"]),
                    row["notes"] if pd.notna(row["notes"]) else None,
                ),
            )

        except sqlite3.IntegrityError:
            # Record already exists.
            continue

    connection.commit()
    connection.close()


def database_has_records():
    """
    Returns True if the farm_records table already
    contains data.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM farm_records"
    )

    total = cursor.fetchone()[0]

    connection.close()

    return total > 0


def initialize_database():
    """
    Prepare the application's database.

    This function:

    1. Creates the database if needed.
    2. Creates all tables.
    3. Imports the historical Excel records only if
       the table is currently empty.
    """

    create_tables()

    if not database_has_records():
        import_excel_data()
```
