"""
test_models.py
==============
Unit tests for models.py — checks that calculated properties
(total_price, profit_margin, needs_reorder, etc.) return correct
values, using small hand-built objects (no database needed).
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from datetime import date
from models import Order, Product, InventoryItem, Customer


def test_order_total_price_no_discount():
    order = Order(
        order_id=1, customer_id=1, product_id=1, store_id=1, employee_id=1,
        order_date=date(2025, 1, 1), quantity=3, unit_price=10.0, discount_pct=0.0,
    )
    assert order.total_price == 30.0


def test_order_total_price_with_discount():
    order = Order(
        order_id=1, customer_id=1, product_id=1, store_id=1, employee_id=1,
        order_date=date(2025, 1, 1), quantity=4, unit_price=50.0, discount_pct=0.1,
    )
    # 4 * 50 = 200, minus 10% = 180
    assert order.total_price == 180.0


def test_order_is_completed():
    completed = Order(
        order_id=1, customer_id=1, product_id=1, store_id=1, employee_id=1,
        order_date=date(2025, 1, 1), quantity=1, unit_price=10.0, order_status="Completed",
    )
    cancelled = Order(
        order_id=2, customer_id=1, product_id=1, store_id=1, employee_id=1,
        order_date=date(2025, 1, 1), quantity=1, unit_price=10.0, order_status="Cancelled",
    )
    assert completed.is_completed is True
    assert cancelled.is_completed is False


def test_product_profit_margin():
    product = Product(product_id=1, product_name="Widget", unit_cost=50.0, unit_price=100.0)
    assert product.profit_margin == 50.0  # (100-50)/100 * 100 = 50%


def test_product_profit_margin_missing_data():
    product = Product(product_id=1, product_name="Widget", unit_cost=None, unit_price=100.0)
    assert product.profit_margin is None


def test_inventory_needs_reorder():
    low_stock = InventoryItem(inventory_id=1, store_id=1, product_id=1, stock_quantity=5, reorder_level=10)
    healthy_stock = InventoryItem(inventory_id=2, store_id=1, product_id=1, stock_quantity=50, reorder_level=10)
    assert low_stock.needs_reorder is True
    assert healthy_stock.needs_reorder is False


def test_customer_full_name():
    customer = Customer(customer_id=1, first_name="Ada", last_name="Lovelace")
    assert customer.full_name == "Ada Lovelace"
