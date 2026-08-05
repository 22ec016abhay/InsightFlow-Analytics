"""
visualizer.py
=============
Turns analyzer.py's results into actual chart images, saved
automatically to reports/charts/. Every function here follows the
same pattern: build a matplotlib chart, save it as a PNG, close the
figure (to free memory), and log what was saved.
"""
 
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
 
import matplotlib
matplotlib.use("Agg")  # renders to file without needing a display window
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
 
import config
from utils import get_logger, log_errors
 
logger = get_logger(__name__)
 
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
 
 
def _save_chart(fig, filename: str) -> Path:
    """Save a matplotlib figure to reports/charts/ and close it to free memory."""
    config.ensure_directories_exist()
    output_path = config.CHARTS_DIR / filename
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved chart -> {output_path}")
    return output_path
 
 
@log_errors
def plot_monthly_sales_trend(monthly_df: pd.DataFrame) -> Path:
    """Line chart: revenue trend over time."""
    fig, ax = plt.subplots()
    ax.plot(monthly_df["order_month"], monthly_df["total_revenue"], marker="o", color="#2563eb")
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45, ha="right")
    return _save_chart(fig, "monthly_sales_trend.png")
 
 
@log_errors
def plot_top_customers(top_customers_df: pd.DataFrame) -> Path:
    """Bar chart: highest-spending customers."""
    fig, ax = plt.subplots()
    ax.barh(top_customers_df["customer_name"], top_customers_df["total_spent"], color="#16a34a")
    ax.set_title("Top Customers by Total Spend")
    ax.set_xlabel("Total Spent ($)")
    ax.invert_yaxis()  # highest spender at the top
    return _save_chart(fig, "top_customers.png")
 
 
@log_errors
def plot_category_sales(category_df: pd.DataFrame) -> Path:
    """Pie chart: revenue share by product category."""
    fig, ax = plt.subplots()
    ax.pie(
        category_df["revenue"],
        labels=category_df["category"],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title("Revenue Share by Category")
    ax.axis("equal")
    return _save_chart(fig, "category_sales_pie.png")
 
 
@log_errors
def plot_store_performance(store_df: pd.DataFrame) -> Path:
    """Bar chart: revenue by store."""
    fig, ax = plt.subplots()
    ax.bar(store_df["store_name"], store_df["revenue"], color="#f59e0b")
    ax.set_title("Revenue by Store")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=60, ha="right")
    return _save_chart(fig, "store_performance.png")
 
 
@log_errors
def plot_order_value_histogram(orders: pd.DataFrame) -> Path:
    """Histogram: distribution of individual order values."""
    fig, ax = plt.subplots()
    ax.hist(orders["total_price"].dropna(), bins=40, color="#8b5cf6", edgecolor="white")
    ax.set_title("Distribution of Order Values")
    ax.set_xlabel("Order Value ($)")
    ax.set_ylabel("Number of Orders")
    return _save_chart(fig, "order_value_histogram.png")
 
 
@log_errors
def plot_price_vs_quantity_scatter(orders: pd.DataFrame) -> Path:
    """Scatter plot: unit price vs quantity ordered — spot patterns/outliers."""
    fig, ax = plt.subplots()
    sample = orders.sample(min(2000, len(orders)), random_state=42)  # sample for readability
    ax.scatter(sample["unit_price"], sample["quantity"], alpha=0.3, color="#ef4444", s=15)
    ax.set_title("Unit Price vs Quantity Ordered")
    ax.set_xlabel("Unit Price ($)")
    ax.set_ylabel("Quantity")
    return _save_chart(fig, "price_vs_quantity_scatter.png")
 
 
@log_errors
def plot_revenue_boxplot_by_region(orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> Path:
    """Box plot: spread of order values across regions."""
    df = orders.merge(stores[["store_id", "region"]], on="store_id", how="left")
    regions = df["region"].dropna().unique()
    data_by_region = [df.loc[df["region"] == r, "total_price"].dropna() for r in regions]
 
    fig, ax = plt.subplots()
    ax.boxplot(data_by_region, tick_labels=regions)
    ax.set_title("Order Value Spread by Region")
    ax.set_ylabel("Order Value ($)")
    return _save_chart(fig, "order_value_boxplot_by_region.png")
 
 
@log_errors
def plot_correlation_heatmap(orders: pd.DataFrame) -> Path:
    """Correlation heatmap between numeric order fields."""
    numeric_cols = ["quantity", "unit_price", "discount_pct", "total_price"]
    numeric_cols = [c for c in numeric_cols if c in orders.columns]
    corr = orders[numeric_cols].corr()
 
    fig, ax = plt.subplots()
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
    ax.set_yticklabels(numeric_cols)
 
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
 
    fig.colorbar(im, ax=ax)
    ax.set_title("Correlation Heatmap (Order Fields)")
    return _save_chart(fig, "correlation_heatmap.png")
 
 
@log_errors
def generate_all_charts(analysis_results: dict, orders: pd.DataFrame, products: pd.DataFrame, stores: pd.DataFrame) -> list[Path]:
    """Generate every chart in one call. Returns the list of saved file paths."""
    saved = [
        plot_monthly_sales_trend(analysis_results["monthly_sales"]),
        plot_top_customers(analysis_results["top_customers"]),
        plot_category_sales(analysis_results["category_performance"]),
        plot_store_performance(analysis_results["store_performance"]),
        plot_order_value_histogram(orders),
        plot_price_vs_quantity_scatter(orders),
        plot_revenue_boxplot_by_region(orders, products, stores),
        plot_correlation_heatmap(orders),
    ]
    logger.info(f"Generated {len(saved)} charts total")
    return saved
 
 
if __name__ == "__main__":
    # Quick manual test: run "python src/visualizer.py"
    from analyzer import load_cleaned_data, run_full_analysis
 
    data = load_cleaned_data()
    results = run_full_analysis()
 
    saved_charts = generate_all_charts(
        results, data["orders"], data["products"], data["stores"]
    )
 
    print(f"\nGenerated {len(saved_charts)} charts:")
    for path in saved_charts:
        print(" -", path.name)
 