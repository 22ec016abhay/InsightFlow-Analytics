"""
config.py
=========
Central configuration for the InsightFlow Analytics project.
Every other module imports settings FROM HERE instead of hardcoding
paths or passwords directly. Change something once, here, and it
updates everywhere.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

# ---- BASE PROJECT PATH ----
BASE_DIR = Path(__file__).resolve().parent

# ---- FOLDER PATHS ----
DATASETS_DIR = BASE_DIR / "datasets"
RAW_DATA_DIR = DATASETS_DIR / "raw"
PROCESSED_DATA_DIR = DATASETS_DIR / "processed"

DATABASE_DIR = BASE_DIR / "database"
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"
LOGS_DIR = BASE_DIR / "logs"

# ---- RAW DATASET FILE PATHS ----
CUSTOMERS_CSV = RAW_DATA_DIR / "customers.csv"
PRODUCTS_CSV = RAW_DATA_DIR / "products.csv"
STORES_CSV = RAW_DATA_DIR / "stores.csv"
EMPLOYEES_CSV = RAW_DATA_DIR / "employees.csv"
INVENTORY_CSV = RAW_DATA_DIR / "inventory.csv"
ORDERS_CSV = RAW_DATA_DIR / "orders.csv"

# ---- DATABASE CONNECTION SETTINGS (pulled from .env) ----
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "insightflow_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ---- LOGGING SETTINGS ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "insightflow.log"

# ---- BUSINESS CONSTANTS ----
LOW_STOCK_THRESHOLD_MULTIPLIER = 1.0
CURRENCY_SYMBOL = "$"


def ensure_directories_exist() -> None:
    """Create all required project folders if they don't already exist."""
    for folder in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        DATABASE_DIR,
        REPORTS_DIR,
        CHARTS_DIR,
        LOGS_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_directories_exist()
    print("BASE_DIR:", BASE_DIR)
    print("RAW_DATA_DIR:", RAW_DATA_DIR)
    print("DB_NAME:", DB_NAME)
    print("Config loaded successfully.")