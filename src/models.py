"""
This module defines Python dataclasses that represent the database tables.
Each class corresponds to a table and provides a convenient way to work
with the data in Python code. These classes act as "shapes" for the data, allowing
Python object "shapes" for every table in the database.

Instead of passing raw dictionaries around (order["quantity"] *
order["unit_price"]), other modules will use these classes:
(order.quantity * order.unit_price), plus calculated properties
like order.total_price.

Uses:
- dataclasses  -> auto-generates __init__ for us
- inheritance  -> Employee and Customer both share a Person base
- @property    -> calculated fields (e.g. total_price, full_name)
- classmethod  -> from_dict() builds a model from a database row
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


# ------------------------------------------------------------------
# Base class — shared by Employee and Customer
# ------------------------------------------------------------------
@dataclass
class Person:
    """Common fields shared by any human record in the system."""
    first_name: str
    last_name: str
    email: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Combine first and last name into one readable string."""
        return f"{self.first_name} {self.last_name}"


# ------------------------------------------------------------------
# STORE
# ------------------------------------------------------------------
@dataclass
class Store:
    store_id: int
    store_name: str
    city: str
    state: str
    region: str
    opened_date: Optional[date] = None
    square_footage: Optional[int] = None
    manager_id: Optional[int] = None

    @classmethod
    def from_dict(cls, row: dict) -> "Store":
        """Build a Store object from a database row (dict)."""
        return cls(
            store_id=row["store_id"],
            store_name=row["store_name"],
            city=row["city"],
            state=row["state"],
            region=row["region"],
            opened_date=row.get("opened_date"),
            square_footage=row.get("square_footage"),
            manager_id=row.get("manager_id"),
        )


# ------------------------------------------------------------------
# EMPLOYEE (inherits from Person)
# ------------------------------------------------------------------
@dataclass
class Employee(Person):
    employee_id: int = 0
    role: str = ""
    store_id: Optional[int] = None
    hire_date: Optional[date] = None
    salary: Optional[float] = None

    @classmethod
    def from_dict(cls, row: dict) -> "Employee":
        return cls(
            employee_id=row["employee_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row.get("email"),
            role=row.get("role", ""),
            store_id=row.get("store_id"),
            hire_date=row.get("hire_date"),
            salary=row.get("salary"),
        )


# ------------------------------------------------------------------
# CUSTOMER (inherits from Person)
# ------------------------------------------------------------------
@dataclass
class Customer(Person):
    customer_id: int = 0
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    signup_date: Optional[date] = None
    loyalty_member: bool = False

    @classmethod
    def from_dict(cls, row: dict) -> "Customer":
        return cls(
            customer_id=row["customer_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row.get("email"),
            phone=row.get("phone"),
            city=row.get("city"),
            state=row.get("state"),
            region=row.get("region"),
            signup_date=row.get("signup_date"),
            loyalty_member=bool(row.get("loyalty_member", False)),
        )


# ------------------------------------------------------------------
# PRODUCT
# ------------------------------------------------------------------
@dataclass
class Product:
    product_id: int
    product_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    unit_cost: Optional[float] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None

    @property
    def profit_margin(self) -> Optional[float]:
        """Profit per unit as a percentage of unit_price. None if data is missing."""
        if not self.unit_price or self.unit_cost is None:
            return None
        return round(((self.unit_price - self.unit_cost) / self.unit_price) * 100, 2)

    @classmethod
    def from_dict(cls, row: dict) -> "Product":
        return cls(
            product_id=row["product_id"],
            product_name=row["product_name"],
            category=row.get("category"),
            brand=row.get("brand"),
            unit_cost=row.get("unit_cost"),
            unit_price=row.get("unit_price"),
            supplier=row.get("supplier"),
        )


# ------------------------------------------------------------------
# INVENTORY ITEM
# ------------------------------------------------------------------
@dataclass
class InventoryItem:
    inventory_id: int
    store_id: int
    product_id: int
    stock_quantity: int
    reorder_level: int
    last_restock_date: Optional[date] = None

    @property
    def needs_reorder(self) -> bool:
        """True if stock has dropped to or below the reorder level."""
        return self.stock_quantity <= self.reorder_level

    @classmethod
    def from_dict(cls, row: dict) -> "InventoryItem":
        return cls(
            inventory_id=row["inventory_id"],
            store_id=row["store_id"],
            product_id=row["product_id"],
            stock_quantity=row["stock_quantity"],
            reorder_level=row["reorder_level"],
            last_restock_date=row.get("last_restock_date"),
        )


# ------------------------------------------------------------------
# ORDER
# ------------------------------------------------------------------
@dataclass
class Order:
    order_id: int
    customer_id: int
    product_id: int
    store_id: int
    employee_id: int
    order_date: Optional[date]
    quantity: int
    unit_price: float
    discount_pct: float = 0.0
    payment_method: Optional[str] = None
    order_status: Optional[str] = None

    @property
    def total_price(self) -> float:
        """Final price after quantity and discount are applied."""
        gross = self.quantity * self.unit_price
        return round(gross * (1 - self.discount_pct), 2)

    @property
    def is_completed(self) -> bool:
        return (self.order_status or "").lower() == "completed"

    @classmethod
    def from_dict(cls, row: dict) -> "Order":
        return cls(
            order_id=row["order_id"],
            customer_id=row["customer_id"],
            product_id=row["product_id"],
            store_id=row["store_id"],
            employee_id=row["employee_id"],
            order_date=row.get("order_date"),
            quantity=row["quantity"],
            unit_price=row["unit_price"],
            discount_pct=row.get("discount_pct", 0.0),
            payment_method=row.get("payment_method"),
            order_status=row.get("order_status"),
        )


if __name__ == "__main__":
    # Quick manual test: run "python src/models.py"
    sample_order = Order.from_dict({
        "order_id": 1,
        "customer_id": 101,
        "product_id": 55,
        "store_id": 3,
        "employee_id": 12,
        "order_date": date(2025, 6, 1),
        "quantity": 4,
        "unit_price": 49.99,
        "discount_pct": 0.1,
        "payment_method": "Credit Card",
        "order_status": "Completed",
    })
    print("Order total price:", sample_order.total_price)
    print("Order is completed:", sample_order.is_completed)

    sample_customer = Customer.from_dict({
        "customer_id": 101,
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "loyalty_member": True,
    })
    print("Customer full name:", sample_customer.full_name)