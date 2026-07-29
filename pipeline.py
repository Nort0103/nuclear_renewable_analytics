import sqlite3
from datetime import datetime
import pandas as pd
import requests

DB_NAME = "energy_platform.db"


def init_db():
    """Initializes the relational database schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create generation sources time-series table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            technology TEXT NOT NULL,
            generation_mw REAL,
            market_price_eur_mwh REAL
        )
    """)

    # Create economic parameters table for LCOE/EROI baseline factors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economic_parameters (
            technology TEXT PRIMARY KEY,
            capex_per_mw REAL,
            opex_annual_per_mw REAL,
            capacity_factor REAL,
            lifespan_years INTEGER,
            eroi_baseline REAL
        )
    """)

    # Insert baseline economic parameters for comparison
    baseline_data = [
        ("nuclear", 6000000.0, 130000.0, 0.85, 60, 45.0),
        ("onshore_wind", 1300000.0, 40000.0, 0.28, 25, 16.0),
        ("solar_pv", 900000.0, 25000.0, 0.15, 25, 10.0),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO economic_parameters 
        (technology, capex_per_mw, opex_annual_per_mw, capacity_factor, lifespan_years, eroi_baseline)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        baseline_data,
    )

    conn.commit()
    conn.close()
    print("Database schema initialized successfully.")


def fetch_and_insert_data():
    """Simulates/fetches multi-technology ingestion pipeline logic."""
    init_db()

    print("Running multi-technology ingestion pipeline...")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Sample mock ingestion records for multiple technologies
    sample_records = [
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "nuclear", 8250.5, 78.4),
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "onshore_wind",
            14200.0,
            78.4,
        ),
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "solar_pv", 21500.0, 65.2),
    ]

    cursor.executemany(
        """
        INSERT INTO generation_sources (timestamp, technology, generation_mw, market_price_eur_mwh)
        VALUES (?, ?, ?, ?)
    """,
        sample_records,
    )

    conn.commit()
    conn.close()
    print("Ingestion pipeline completed: Multi-technology records saved.")


if __name__ == "__main__":
    fetch_and_insert_data()
