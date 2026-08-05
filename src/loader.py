"""
loader.py
=========
Connects database.py (raw SQL results) with models.py (clean Python
objects). Every "load_*" function here runs a query and returns a
LIST OF MODEL OBJECTS, not raw dictionaries.

Example:
    stores = load_all_stores()
    for store in stores:
        print(store.store_name, store.region)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import run_query
from models import Store, Employee, Product, Customer, InventoryItem, Order
from utils import get_logger, timer_decorator, log_errors

logger = get_logger(__name__)


class DataLoadError(Exception):
    """Raised when InsightFlow Analytics fails to load data from the database."""
    pass


@timer_decorator
@log_errors
def load_all_stores() -> list[Store]:
    """Load every row from the stores table as a list of Store objects."""
    rows = run_query("SELECT * FROM stores ORDER BY store_id;")
    stores = [Store.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(stores)} stores")
    return stores


@timer_decorator
@log_errors
def load_all_employees() -> list[Employee]:
    """Load every row from the employees table as a list of Employee objects."""
    rows = run_query("SELECT * FROM employees ORDER BY employee_id;")
    employees = [Employee.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(employees)} employees")
    return employees


@timer_decorator
@log_errors
def load_all_products() -> list[Product]:
    """Load every row from the products table as a list of Product objects."""
    rows = run_query("SELECT * FROM products ORDER BY product_id;")
    products = [Product.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(products)} products")
    return products


@timer_decorator
@log_errors
def load_all_customers() -> list[Customer]:
    """Load every row from the customers table as a list of Customer objects."""
    rows = run_query("SELECT * FROM customers ORDER BY customer_id;")
    customers = [Customer.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(customers)} customers")
    return customers


@timer_decorator
@log_errors
def load_all_inventory() -> list[InventoryItem]:
    """Load every row from the inventory table as a list of InventoryItem objects."""
    rows = run_query("SELECT * FROM inventory ORDER BY inventory_id;")
    items = [InventoryItem.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(items)} inventory records")
    return items


@timer_decorator
@log_errors
def load_all_orders() -> list[Order]:
    """Load every row from the orders table as a list of Order objects."""
    rows = run_query("SELECT * FROM orders ORDER BY order_id;")
    orders = [Order.from_dict(row) for row in rows]
    logger.info(f"Loaded {len(orders)} orders")
    return orders


@log_errors
def load_orders_by_store(store_id: int) -> list[Order]:
    """Load only the orders that belong to a specific store."""
    rows = run_query(
        "SELECT * FROM orders WHERE store_id = %s ORDER BY order_date;",
        (store_id,),
    )
    if not rows:
        logger.warning(f"No orders found for store_id={store_id}")
    return [Order.from_dict(row) for row in rows]


if __name__ == "__main__":
    # Quick manual test: run "python src/loader.py"
    try:
        stores = load_all_stores()
        products = load_all_products()
        orders = load_all_orders()

        print(f"\nLoaded {len(stores)} stores, {len(products)} products, {len(orders)} orders.")

        if orders:
            sample = orders[0]
            print(f"First order total price: ${sample.total_price}")

    except DataLoadError as exc:
        print("Data load FAILED:", exc)