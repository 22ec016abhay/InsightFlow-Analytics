"""
test_validator.py
==================
Unit tests for validator.py — confirms each check function correctly
detects the problem it's designed to find, and correctly reports
"passed" when data is actually clean.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
from validator import (
    check_duplicate_rows,
    check_missing_values,
    check_negative_values,
    check_invalid_dates,
)


def test_check_duplicate_rows_detects_duplicates():
    df = pd.DataFrame({"order_id": [1, 1, 2]})
    result = check_duplicate_rows(df, subset="order_id")
    assert result["issue_count"] == 1
    assert result["passed"] is False


def test_check_duplicate_rows_passes_when_clean():
    df = pd.DataFrame({"order_id": [1, 2, 3]})
    result = check_duplicate_rows(df, subset="order_id")
    assert result["issue_count"] == 0
    assert result["passed"] is True


def test_check_missing_values_detects_nulls():
    df = pd.DataFrame({"price": [10.0, None, 20.0]})
    result = check_missing_values(df, columns=["price"])
    assert result["issue_count"] == 1
    assert result["passed"] is False


def test_check_negative_values_detects_negatives():
    df = pd.DataFrame({"quantity": [5, -3, 10]})
    result = check_negative_values(df, columns=["quantity"])
    assert result["issue_count"] == 1
    assert result["passed"] is False


def test_check_invalid_dates_detects_bad_dates():
    df = pd.DataFrame({"order_date": ["2025-01-01", "not_a_date", "2025-13-40"]})
    result = check_invalid_dates(df, column="order_date")
    assert result["issue_count"] == 2
    assert result["passed"] is False


def test_check_invalid_dates_passes_when_all_valid():
    df = pd.DataFrame({"order_date": ["2025-01-01", "2025-06-15"]})
    result = check_invalid_dates(df, column="order_date")
    assert result["issue_count"] == 0
    assert result["passed"] is True
