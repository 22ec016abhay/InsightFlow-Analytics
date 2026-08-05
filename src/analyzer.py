"""
analyzer.py
===========
The business analytics engine. Takes the CLEANED data (from
datasets/processed/) and produces the actual insights a retail
analyst would report: sales trends, top customers, product
performance, store performance, and inventory alerts.
 
Every function returns a pandas DataFrame (or a small dict of
summary stats) — ready to be handed to visualizer.py for charts or
report_generator.py for the Excel report.
"""
 
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
 
import numpy as np
import pandas as pd
 
import config
from utils import get_logger, timer_decorator, log_errors
 
logger = get_logger(__name__)
 
 
class AnalysisError(Exception):
    """Raised when analyzer.py cannot compute a requested insight."""
    pass
 
 
# ------------------------------------------------------------------
# Loading cleaned data (analyzer works on the OUTPUT of cleaner.py)
# ------------------------------------------------------------------
@log_errors
def load_cleaned_data() -> dict[str, pd.DataFrame]:
    """Load every _cleaned.csv file from datasets/processed/ into a dict of DataFrames."""
    names = ["stores", "employees", "products", "customers", "inventory", "orders"]
    data = {}
    for name in names:
        path = config.PROCESSED_DATA_DIR / f"{name}_cleaned.csv"
        if not path.exists():
            raise AnalysisError(
                f"Missing cleaned file: {path}. Run cleaner.py first."
            )
        data[name] = pd.read_csv(path)
    logger.info(f"Loaded {len(data)} cleaned datasets for analysis")
    return data
 
 
def _enrich_orders(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Join orders with product and store info — most analyses need this combined view."""
    df = orders.merge(products[["product_id", "product_name", "category", "unit_cost"]],
                       on="product_id", how="left", suffixes=("", "_product"))
    df = df.merge(stores[["store_id", "store_name", "region"]], on="store_id", how="left")
 
    # total_price should already exist from cleaner.py, but recompute defensively
    if "total_price" not in df.columns:
        df["total_price"] = (df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])).round(2)
 
    df["profit"] = ((df["unit_price"] - df["unit_cost"]) * df["quantity"] * (1 - df["discount_pct"])).round(2)
 
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
 
    return df
 
 
# ------------------------------------------------------------------
# SALES ANALYSIS
# ------------------------------------------------------------------
@timer_decorator
@log_errors
def monthly_sales(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Total revenue and order count per month."""
    df = _enrich_orders(orders, products, stores)
    summary = (
        df.groupby("order_month")
        .agg(total_revenue=("total_price", "sum"),
             total_orders=("order_id", "count"),
             avg_order_value=("total_price", "mean"))
        .round(2)
        .reset_index()
        .sort_values("order_month")
    )
    return summary
 
 
@log_errors
def daily_sales(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Total revenue per calendar day."""
    df = _enrich_orders(orders, products, stores)
    summary = (
        df.groupby(df["order_date"].dt.date)
        .agg(total_revenue=("total_price", "sum"), total_orders=("order_id", "count"))
        .round(2)
        .reset_index()
        .rename(columns={"order_date": "date"})
    )
    return summary
 
 
@log_errors
def average_order_value(orders: pd.DataFrame) -> dict:
    """Overall AOV plus basic NumPy statistics on order values."""
    values = orders["total_price"].dropna().to_numpy()
    return {
        "mean": round(float(np.mean(values)), 2),
        "median": round(float(np.median(values)), 2),
        "std_dev": round(float(np.std(values)), 2),
        "p25": round(float(np.percentile(values, 25)), 2),
        "p75": round(float(np.percentile(values, 75)), 2),
    }
 
 
# ------------------------------------------------------------------
# CUSTOMER ANALYSIS
# ------------------------------------------------------------------
@log_errors
def top_customers(orders: pd.DataFrame, customers: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top N customers by total amount spent (a basic Customer Lifetime Value view)."""
    spend = (
        orders.groupby("customer_id")
        .agg(total_spent=("total_price", "sum"), total_orders=("order_id", "count"))
        .round(2)
        .reset_index()
    )
    merged = spend.merge(customers[["customer_id", "first_name", "last_name", "region"]], on="customer_id")
    merged["customer_name"] = merged["first_name"] + " " + merged["last_name"]
    merged = merged.sort_values("total_spent", ascending=False).head(top_n)
    return merged[["customer_id", "customer_name", "region", "total_orders", "total_spent"]]
 
 
# ------------------------------------------------------------------
# PRODUCT ANALYSIS
# ------------------------------------------------------------------
@log_errors
def best_selling_products(orders: pd.DataFrame, products: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top N products by total revenue generated."""
    sales = (
        orders.groupby("product_id")
        .agg(units_sold=("quantity", "sum"), revenue=("total_price", "sum"))
        .round(2)
        .reset_index()
    )
    merged = sales.merge(products[["product_id", "product_name", "category"]], on="product_id")
    return merged.sort_values("revenue", ascending=False).head(top_n)
 
 
@log_errors
def worst_selling_products(orders: pd.DataFrame, products: pd.DataFrame, bottom_n: int = 10) -> pd.DataFrame:
    """Bottom N products by total revenue — candidates for discontinuation."""
    sales = (
        orders.groupby("product_id")
        .agg(units_sold=("quantity", "sum"), revenue=("total_price", "sum"))
        .round(2)
        .reset_index()
    )
    merged = sales.merge(products[["product_id", "product_name", "category"]], on="product_id")
    return merged.sort_values("revenue", ascending=True).head(bottom_n)
 
 
@log_errors
def category_performance(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit rolled up by product category."""
    df = _enrich_orders(orders, products, stores)
    summary = (
        df.groupby("category")
        .agg(revenue=("total_price", "sum"), profit=("profit", "sum"), units_sold=("quantity", "sum"))
        .round(2)
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    return summary
 
 
# ------------------------------------------------------------------
# STORE / REGIONAL PERFORMANCE
# ------------------------------------------------------------------
@log_errors
def store_performance(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Revenue, profit, and order count per store."""
    df = _enrich_orders(orders, products, stores)
    summary = (
        df.groupby(["store_id", "store_name"])
        .agg(revenue=("total_price", "sum"), profit=("profit", "sum"), total_orders=("order_id", "count"))
        .round(2)
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    return summary
 
 
@log_errors
def regional_performance(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit rolled up by region — uses a pivot table."""
    df = _enrich_orders(orders, products, stores)
    pivot = pd.pivot_table(
        df, index="region", values=["total_price", "profit"],
        aggfunc="sum",
    ).round(2).reset_index().sort_values("total_price", ascending=False)
    return pivot.rename(columns={"total_price": "revenue"})
 
 
# ------------------------------------------------------------------
# INVENTORY ANALYSIS
# ------------------------------------------------------------------
@log_errors
def stock_alerts(inventory: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> pd.DataFrame:
    """Items at or below their reorder level — need restocking now."""
    df = inventory.merge(products[["product_id", "product_name"]], on="product_id", how="left")
    df = df.merge(stores[["store_id", "store_name"]], on="store_id", how="left")
    low_stock = df[df["stock_quantity"] <= df["reorder_level"] * config.LOW_STOCK_THRESHOLD_MULTIPLIER]
    return low_stock[["store_name", "product_name", "stock_quantity", "reorder_level"]].sort_values("stock_quantity")
 
 
@log_errors
def inventory_summary(inventory: pd.DataFrame) -> dict:
    """Overall inventory statistics using NumPy."""
    stock = inventory["stock_quantity"].dropna().to_numpy()
    return {
        "total_units_in_stock": int(np.sum(stock)),
        "avg_stock_per_item": round(float(np.mean(stock)), 2),
        "median_stock": float(np.median(stock)),
        "items_out_of_stock": int((stock == 0).sum()),
    }
 
 
# ------------------------------------------------------------------
# Convenience: run everything at once
# ------------------------------------------------------------------
@timer_decorator
def run_full_analysis() -> dict:
    """Runs every analysis function and returns all results in one dictionary."""
    data = load_cleaned_data()
    orders, products, stores = data["orders"], data["products"], data["stores"]
    customers, inventory = data["customers"], data["inventory"]
 
    return {
        "monthly_sales": monthly_sales(orders, products, stores),
        "aov_stats": average_order_value(orders),
        "top_customers": top_customers(orders, customers),
        "best_products": best_selling_products(orders, products),
        "worst_products": worst_selling_products(orders, products),
        "category_performance": category_performance(orders, products, stores),
        "store_performance": store_performance(orders, products, stores),
        "regional_performance": regional_performance(orders, products, stores),
        "stock_alerts": stock_alerts(inventory, products, stores),
        "inventory_summary": inventory_summary(inventory),
    }
 
 
if __name__ == "__main__":
    # Quick manual test: run "python src/analyzer.py"
    results = run_full_analysis()
 
    print("\n=== Monthly Sales (first 5 rows) ===")
    print(results["monthly_sales"].head())
 
    print("\n=== Average Order Value Stats ===")
    print(results["aov_stats"])
 
    print("\n=== Top 5 Customers ===")
    print(results["top_customers"].head())
 
    print("\n=== Best Selling Products (top 5) ===")
    print(results["best_products"].head())
 
    print("\n=== Stock Alerts (low stock, first 5) ===")
    print(results["stock_alerts"].head())
 
    print("\n=== Inventory Summary ===")
    print(results["inventory_summary"])