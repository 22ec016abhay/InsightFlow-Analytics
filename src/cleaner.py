
"""
cleaner.py
==========
Takes messy raw data and actually FIXES it — this is where
validator.py's findings get resolved.
 
Each clean_* function returns a brand-new, cleaned DataFrame (the
original is never modified in place — this makes bugs much easier
to trace, since raw data always stays untouched on disk).
 
clean_all() runs the full pipeline for every dataset and saves the
results to datasets/processed/.
"""
 
import numpy as np
import pandas as pd
 
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from utils import get_logger, timer_decorator, log_errors
 
logger = get_logger(__name__)
 
 
class CleaningError(Exception):
    """Raised when a dataset cannot be cleaned (e.g. required column missing)."""
    pass
 
 
@log_errors
def clean_stores(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the stores dataset."""
    df = df.drop_duplicates(subset="store_id").copy()
    df["state"] = df["state"].str.upper().str.strip()
    df["square_footage"] = pd.to_numeric(df["square_footage"], errors="coerce")
    logger.info(f"clean_stores: {len(df)} rows after cleaning")
    return df
 
 
@log_errors
def clean_employees(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the employees dataset."""
    df = df.drop_duplicates(subset="employee_id").copy()
 
    # Standardize role casing (e.g. "sales associate" -> "Sales Associate")
    df["role"] = df["role"].str.strip().str.title()
 
    # Fill missing salary with the median salary (a common, defensible default)
    median_salary = df["salary"].median()
    df["salary"] = df["salary"].fillna(median_salary)
 
    # Flag malformed emails instead of guessing a fix
    df["email_valid"] = df["email"].str.contains(r"^[^@]+@[^@]+\.[^@]+$", regex=True, na=False)
 
    logger.info(f"clean_employees: {len(df)} rows after cleaning")
    return df
 
 
@log_errors
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the products dataset."""
    df = df.drop_duplicates(subset="product_id").copy()
 
    # Standardize category casing
    df["category"] = df["category"].str.strip().str.title()
    df["category"] = df["category"].fillna("Uncategorized")
 
    # Negative unit_cost is a data-entry error -> take absolute value
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").abs()
 
    # Missing unit_price: estimate using a standard markup over cost
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    estimated_price = df["unit_cost"] * 1.6
    df["unit_price"] = df["unit_price"].fillna(estimated_price)
 
    logger.info(f"clean_products: {len(df)} rows after cleaning")
    return df
 
 
@log_errors
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the customers dataset."""
    df = df.drop_duplicates(subset="customer_id").copy()
    df["state"] = df["state"].str.upper().str.strip()
    df["phone"] = df["phone"].replace("N/A", np.nan)
    df["email_missing"] = df["email"].isna()
    logger.info(f"clean_customers: {len(df)} rows after cleaning")
    return df
 
 
@log_errors
def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the inventory dataset."""
    df = df.drop_duplicates(subset="inventory_id").copy()
 
    # Negative stock is impossible in reality -> clamp to 0
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce")
    df["stock_quantity"] = df["stock_quantity"].clip(lower=0)
 
    df["last_restock_date"] = pd.to_datetime(df["last_restock_date"], errors="coerce")
 
    logger.info(f"clean_inventory: {len(df)} rows after cleaning")
    return df
 
 
@log_errors
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the orders dataset — the most heavily 'dirty' one."""
    df = df.drop_duplicates(subset="order_id").copy()
 
    # Negative quantities are miscoded returns -> take absolute value
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").abs()
 
    # Cap extreme outlier quantities (fat-finger entries like 850, 1200)
    # using the IQR method instead of an arbitrary hard number
    q1, q3 = df["quantity"].quantile(0.25), df["quantity"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    df["quantity"] = df["quantity"].clip(upper=upper_bound)
 
    # Invalid date strings -> NaT (pandas' "missing date"), then drop those rows
    # since order_date is essential for time-based analysis
    df["order_date"] = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
    before = len(df)
    df = df.dropna(subset=["order_date"])
    logger.info(f"clean_orders: dropped {before - len(df)} rows with invalid order_date")
 
    # Missing unit_price -> fill with the median price for that product
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["unit_price"] = df.groupby("product_id")["unit_price"].transform(
        lambda x: x.fillna(x.median())
    )
    # Any still-missing prices (product had no valid prices at all) -> overall median
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median())
 
    # Feature engineering: total_price and order month, useful for later analysis
    df["total_price"] = (df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])).round(2)
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
 
    logger.info(f"clean_orders: {len(df)} rows after cleaning")
    return df
 
 
@timer_decorator
@log_errors
def clean_all() -> dict[str, pd.DataFrame]:
    """
    Run the full cleaning pipeline: read every raw CSV, clean it,
    save the result to datasets/processed/, and return all cleaned
    DataFrames in a dictionary.
    """
    config.ensure_directories_exist()
 
    pipeline = {
        "stores": (config.STORES_CSV, clean_stores),
        "employees": (config.EMPLOYEES_CSV, clean_employees),
        "products": (config.PRODUCTS_CSV, clean_products),
        "customers": (config.CUSTOMERS_CSV, clean_customers),
        "inventory": (config.INVENTORY_CSV, clean_inventory),
        "orders": (config.ORDERS_CSV, clean_orders),
    }
 
    cleaned = {}
    for name, (raw_path, clean_func) in pipeline.items():
        raw_df = pd.read_csv(raw_path)
        cleaned_df = clean_func(raw_df)
        output_path = config.PROCESSED_DATA_DIR / f"{name}_cleaned.csv"
        cleaned_df.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned '{name}' -> {output_path}")
        cleaned[name] = cleaned_df
 
    return cleaned
 
 
if __name__ == "__main__":
    # Quick manual test: run "python src/cleaner.py"
    results = clean_all()
    for name, df in results.items():
        print(f"{name:12s}: {len(df):>6} rows -> datasets/processed/{name}_cleaned.csv")