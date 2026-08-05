"""
main.py
=======
InsightFlow Analytics — interactive command-line menu.
This is the file you actually run day-to-day: `python main.py`

It ties together every module in src/ behind a simple numbered menu,
so you never have to remember which script does what.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from utils import get_logger
from cleaner import clean_all
from analyzer import load_cleaned_data, run_full_analysis
from visualizer import generate_all_charts
from report_generator import generate_excel_report
from dashboard import run_full_pipeline
from database import run_query, DatabaseConnectionError

logger = get_logger(__name__)

MENU_TEXT = """
==============================
   InsightFlow Analytics
==============================
1  Load Data (preview raw datasets)
2  Clean Data
3  Analyze Sales
4  Analyze Customers
5  Product Analysis
6  Inventory Analysis
7  Generate Charts
8  Generate Excel Report
9  Run SQL Analytics (via PostgreSQL)
10 Run Full Pipeline (2 + 3 + 7 + 8)
0  Exit
==============================
"""

# Cache analysis results across menu choices in the same session,
# so the user doesn't have to re-run analysis for every option.
_session_cache: dict = {}


def _get_analysis() -> dict:
    """Run (or reuse) the full analysis for this session."""
    if "analysis" not in _session_cache:
        print("\nRunning analysis (first time this session)...")
        _session_cache["analysis"] = run_full_analysis()
    return _session_cache["analysis"]


def handle_load_data() -> None:
    import config
    import pandas as pd
    print("\n--- Raw Dataset Preview ---")
    for name, path in [
        ("stores", config.STORES_CSV), ("employees", config.EMPLOYEES_CSV),
        ("products", config.PRODUCTS_CSV), ("customers", config.CUSTOMERS_CSV),
        ("inventory", config.INVENTORY_CSV), ("orders", config.ORDERS_CSV),
    ]:
        try:
            df = pd.read_csv(path)
            print(f"{name:12s}: {len(df):>6} rows, columns: {list(df.columns)[:4]}...")
        except FileNotFoundError:
            print(f"{name:12s}: FILE NOT FOUND at {path}")


def handle_clean_data() -> None:
    clean_all()
    print("Cleaning complete. See datasets/processed/")


def handle_analyze_sales() -> None:
    results = _get_analysis()
    print("\n--- Monthly Sales ---")
    print(results["monthly_sales"].to_string(index=False))
    print("\n--- Average Order Value ---")
    print(results["aov_stats"])


def handle_analyze_customers() -> None:
    results = _get_analysis()
    print("\n--- Top 10 Customers ---")
    print(results["top_customers"].to_string(index=False))


def handle_product_analysis() -> None:
    results = _get_analysis()
    print("\n--- Best Selling Products ---")
    print(results["best_products"].to_string(index=False))
    print("\n--- Worst Selling Products ---")
    print(results["worst_products"].to_string(index=False))
    print("\n--- Category Performance ---")
    print(results["category_performance"].to_string(index=False))


def handle_inventory_analysis() -> None:
    results = _get_analysis()
    print("\n--- Stock Alerts (needs reorder) ---")
    print(results["stock_alerts"].to_string(index=False))
    print("\n--- Inventory Summary ---")
    print(results["inventory_summary"])


def handle_generate_charts() -> None:
    results = _get_analysis()
    data = load_cleaned_data()
    saved = generate_all_charts(results, data["orders"], data["products"], data["stores"])
    print(f"\nGenerated {len(saved)} charts in reports/charts/")


def handle_generate_excel_report() -> None:
    results = _get_analysis()
    path = generate_excel_report(results)
    print(f"\nExcel report saved: {path}")


def handle_sql_analytics() -> None:
    print("\n--- SQL Analytics (live query against PostgreSQL) ---")
    try:
        rows = run_query("""
            SELECT s.region, COUNT(o.order_id) AS total_orders,
                   ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount_pct))::numeric, 2) AS revenue
            FROM orders o
            JOIN stores s ON o.store_id = s.store_id
            GROUP BY s.region
            ORDER BY revenue DESC;
        """)
        for row in rows:
            print(f"  {row['region']:<12} orders={row['total_orders']:<6} revenue=${row['revenue']:,.2f}")
    except DatabaseConnectionError as exc:
        print(f"Could not run SQL analytics: {exc}")


def handle_full_pipeline() -> None:
    _session_cache["analysis"] = run_full_pipeline()


def main() -> None:
    actions = {
        "1": handle_load_data,
        "2": handle_clean_data,
        "3": handle_analyze_sales,
        "4": handle_analyze_customers,
        "5": handle_product_analysis,
        "6": handle_inventory_analysis,
        "7": handle_generate_charts,
        "8": handle_generate_excel_report,
        "9": handle_sql_analytics,
        "10": handle_full_pipeline,
    }

    while True:
        print(MENU_TEXT)
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice, please try again.")
            continue

        try:
            action()
        except Exception as exc:
            logger.error(f"Error running menu option {choice}: {exc}")
            print(f"Something went wrong: {exc}")

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()