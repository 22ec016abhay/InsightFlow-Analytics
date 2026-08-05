"""
dashboard.py
============
Ties cleaner.py, analyzer.py, visualizer.py, and report_generator.py
together into one orchestrated pipeline. main.py's menu calls into
THIS file rather than juggling four modules directly — one clean
entry point per major action.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from cleaner import clean_all
from analyzer import load_cleaned_data, run_full_analysis
from visualizer import generate_all_charts
from report_generator import generate_excel_report
from utils import get_logger, timer_decorator, log_errors

logger = get_logger(__name__)


@timer_decorator
@log_errors
def run_cleaning_step() -> dict:
    """Step: clean all raw datasets, save to datasets/processed/."""
    print("\nCleaning raw data...")
    cleaned = clean_all()
    for name, df in cleaned.items():
        print(f"  {name:12s}: {len(df):>6} rows -> datasets/processed/{name}_cleaned.csv")
    print("Cleaning complete.\n")
    return cleaned


@timer_decorator
@log_errors
def run_analysis_step() -> dict:
    """Step: run every business analysis and return the results dict."""
    print("\nRunning business analysis...")
    results = run_full_analysis()
    print(f"Analysis complete — {len(results)} insight sets generated.\n")
    return results


@timer_decorator
@log_errors
def run_chart_step(analysis_results: dict) -> list:
    """Step: generate every chart from the analysis results."""
    print("\nGenerating charts...")
    data = load_cleaned_data()
    saved = generate_all_charts(analysis_results, data["orders"], data["products"], data["stores"])
    for path in saved:
        print(f"  saved: reports/charts/{path.name}")
    print(f"Generated {len(saved)} charts.\n")
    return saved


@timer_decorator
@log_errors
def run_report_step(analysis_results: dict):
    """Step: generate the multi-sheet Excel business report."""
    print("\nGenerating Excel report...")
    path = generate_excel_report(analysis_results)
    print(f"Excel report saved: {path}\n")
    return path


@log_errors
def run_full_pipeline() -> dict:
    """
    Run the entire pipeline end-to-end: clean -> analyze -> charts -> report.
    This is what main.py's menu option "Run Everything" calls.
    """
    print("=" * 60)
    print("InsightFlow Analytics — Full Pipeline")
    print("=" * 60)

    run_cleaning_step()
    analysis_results = run_analysis_step()
    run_chart_step(analysis_results)
    run_report_step(analysis_results)

    print("=" * 60)
    print("Pipeline complete! Check reports/ for your Excel report")
    print("and reports/charts/ for all generated visualizations.")
    print("=" * 60)

    return analysis_results


if __name__ == "__main__":
    # Quick manual test: run "python src/dashboard.py"
    run_full_pipeline()