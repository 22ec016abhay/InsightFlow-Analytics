"""
validator.py
============
Inspects raw data and REPORTS problems — it never modifies anything.
cleaner.py (the next file) is the one that actually fixes what gets
found here.
 
Each check function takes a pandas DataFrame and returns a small
report (a dictionary) describing what it found. validate_dataset()
runs every relevant check and combines the results.
"""
 
import pandas as pd
 
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import get_logger, log_errors
 
logger = get_logger(__name__)
 
 
class ValidationError(Exception):
    """Raised when a dataset is too damaged to validate (e.g. missing required columns)."""
    pass
 
 
def check_duplicate_rows(df: pd.DataFrame, subset: str) -> dict:
    """Count duplicate rows based on an ID column (e.g. 'order_id')."""
    duplicate_count = int(df.duplicated(subset=subset).sum())
    return {
        "check": "duplicate_rows",
        "column": subset,
        "issue_count": duplicate_count,
        "passed": duplicate_count == 0,
    }
 
 
def check_missing_values(df: pd.DataFrame, columns: list[str]) -> dict:
    """Count how many rows have a missing (null/blank) value in each given column."""
    results = {}
    for col in columns:
        if col in df.columns:
            missing = int(df[col].isna().sum())
            results[col] = missing
    total_missing = sum(results.values())
    return {
        "check": "missing_values",
        "by_column": results,
        "issue_count": total_missing,
        "passed": total_missing == 0,
    }
 
 
def check_negative_values(df: pd.DataFrame, columns: list[str]) -> dict:
    """Count rows where a numeric column has a negative value (e.g. quantity, stock)."""
    results = {}
    for col in columns:
        if col in df.columns:
            negative = int((pd.to_numeric(df[col], errors="coerce") < 0).sum())
            results[col] = negative
    total_negative = sum(results.values())
    return {
        "check": "negative_values",
        "by_column": results,
        "issue_count": total_negative,
        "passed": total_negative == 0,
    }
 
 
def check_invalid_dates(df: pd.DataFrame, column: str) -> dict:
    """Count rows where a date column cannot be parsed as a real date."""
    if column not in df.columns:
        return {"check": "invalid_dates", "column": column, "issue_count": 0, "passed": True}
 
    parsed = pd.to_datetime(df[column], format="%Y-%m-%d", errors="coerce")
    invalid_count = int(parsed.isna().sum() - df[column].isna().sum())
    invalid_count = max(invalid_count, 0)
    return {
        "check": "invalid_dates",
        "column": column,
        "issue_count": invalid_count,
        "passed": invalid_count == 0,
    }
 
 
def check_outliers_iqr(df: pd.DataFrame, column: str) -> dict:
    """
    Flag statistical outliers using the IQR (interquartile range) method —
    a standard NumPy/Pandas technique: anything outside
    [Q1 - 1.5*IQR, Q3 + 1.5*IQR] is considered an outlier.
    """
    if column not in df.columns:
        return {"check": "outliers", "column": column, "issue_count": 0, "passed": True}
 
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outlier_count = int(((series < lower_bound) | (series > upper_bound)).sum())
 
    return {
        "check": "outliers",
        "column": column,
        "issue_count": outlier_count,
        "bounds": (round(lower_bound, 2), round(upper_bound, 2)),
        "passed": outlier_count == 0,
    }
 
 
@log_errors
def validate_orders(df: pd.DataFrame) -> list[dict]:
    """Run every relevant check against the orders dataset."""
    report = [
        check_duplicate_rows(df, subset="order_id"),
        check_missing_values(df, columns=["unit_price", "order_date"]),
        check_negative_values(df, columns=["quantity"]),
        check_invalid_dates(df, column="order_date"),
        check_outliers_iqr(df, column="quantity"),
    ]
    return report
 
 
@log_errors
def validate_products(df: pd.DataFrame) -> list[dict]:
    report = [
        check_duplicate_rows(df, subset="product_id"),
        check_missing_values(df, columns=["unit_price", "category"]),
        check_negative_values(df, columns=["unit_cost", "unit_price"]),
    ]
    return report
 
 
@log_errors
def validate_customers(df: pd.DataFrame) -> list[dict]:
    report = [
        check_duplicate_rows(df, subset="customer_id"),
        check_missing_values(df, columns=["email"]),
    ]
    return report
 
 
@log_errors
def validate_inventory(df: pd.DataFrame) -> list[dict]:
    report = [
        check_duplicate_rows(df, subset="inventory_id"),
        check_negative_values(df, columns=["stock_quantity"]),
        check_missing_values(df, columns=["last_restock_date"]),
    ]
    return report
 
 
def print_report(dataset_name: str, report: list[dict]) -> None:
    """Pretty-print a validation report to the console."""
    print(f"\n=== Validation Report: {dataset_name} ===")
    for entry in report:
        status = "PASS" if entry["passed"] else "FAIL"
        print(f"[{status}] {entry['check']:<18} issues found: {entry['issue_count']}")
 
 
if __name__ == "__main__":
    # Quick manual test: run "python src/validator.py"
    import config
 
    orders_df = pd.read_csv(config.ORDERS_CSV)
    products_df = pd.read_csv(config.PRODUCTS_CSV)
 
    orders_report = validate_orders(orders_df)
    products_report = validate_products(products_df)
 
    print_report("orders", orders_report)
    print_report("products", products_report)
 