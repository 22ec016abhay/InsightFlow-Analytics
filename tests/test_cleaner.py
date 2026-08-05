"""
test_cleaner.py
================
Unit tests for cleaner.py — builds tiny, deliberately messy
DataFrames in memory (no CSV files needed) and checks that each
clean_* function fixes exactly what it's supposed to.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
import numpy as np
from cleaner import clean_products, clean_orders, clean_inventory


def test_clean_products_removes_duplicates():
    df = pd.DataFrame({
        "product_id": [1, 1, 2],
        "product_name": ["Widget", "Widget", "Gadget"],
        "category": ["Tools", "Tools", "Tools"],
        "unit_cost": [10.0, 10.0, 20.0],
        "unit_price": [15.0, 15.0, 30.0],
    })
    cleaned = clean_products(df)
    assert len(cleaned) == 2
    assert cleaned["product_id"].is_unique


def test_clean_products_fixes_negative_cost():
    df = pd.DataFrame({
        "product_id": [1],
        "product_name": ["Widget"],
        "category": ["Tools"],
        "unit_cost": [-10.0],   # data entry error
        "unit_price": [15.0],
    })
    cleaned = clean_products(df)
    assert cleaned["unit_cost"].iloc[0] == 10.0  # made positive


def test_clean_products_fills_missing_category():
    df = pd.DataFrame({
        "product_id": [1],
        "product_name": ["Widget"],
        "category": [None],
        "unit_cost": [10.0],
        "unit_price": [15.0],
    })
    cleaned = clean_products(df)
    assert cleaned["category"].iloc[0] == "Uncategorized"


def test_clean_orders_removes_negative_quantity():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "product_id": [1, 1],
        "quantity": [-5, 5],
        "unit_price": [10.0, 10.0],
        "discount_pct": [0.0, 0.0],
        "order_date": ["2025-01-01", "2025-01-02"],
    })
    cleaned = clean_orders(df)
    # negative quantity should become positive (abs), not removed
    assert (cleaned["quantity"] >= 0).all()


def test_clean_orders_drops_invalid_dates():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "product_id": [1, 1],
        "quantity": [1, 1],
        "unit_price": [10.0, 10.0],
        "discount_pct": [0.0, 0.0],
        "order_date": ["2025-01-01", "not_a_date"],
    })
    cleaned = clean_orders(df)
    assert len(cleaned) == 1  # the invalid-date row got dropped
    assert cleaned["order_id"].iloc[0] == 1


def test_clean_inventory_clamps_negative_stock():
    df = pd.DataFrame({
        "inventory_id": [1],
        "store_id": [1],
        "product_id": [1],
        "stock_quantity": [-15],   # impossible in reality
        "reorder_level": [10],
        "last_restock_date": ["2025-01-01"],
    })
    cleaned = clean_inventory(df)
    assert cleaned["stock_quantity"].iloc[0] == 0
