-- ============================================================
-- InsightFlow Analytics — Database Schema
-- ============================================================
-- Run this file against the insightflow_db database.
-- Creates all 6 core tables with primary keys, foreign keys,
-- and indexes on columns we'll query/join on frequently.
--
-- Order matters: a table can't reference another table that
-- doesn't exist yet. So we create STORES before EMPLOYEES,
-- then come back and link the manager_id afterwards.
-- ============================================================

-- Drop tables if re-running this script during development
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;


-- ============================================================
-- 1. STORES
-- ============================================================
CREATE TABLE stores (
    store_id        INTEGER PRIMARY KEY,
    store_name      VARCHAR(100) NOT NULL,
    city            VARCHAR(50)  NOT NULL,
    state           VARCHAR(2)   NOT NULL,
    region          VARCHAR(20)  NOT NULL,
    opened_date     DATE,
    square_footage  INTEGER,
    manager_id      INTEGER  -- FK added later, after employees exists
);


-- ============================================================
-- 2. EMPLOYEES
-- ============================================================
CREATE TABLE employees (
    employee_id  INTEGER PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100),
    role         VARCHAR(50),
    store_id     INTEGER REFERENCES stores(store_id),
    hire_date    DATE,
    salary       NUMERIC(10, 2)
);

-- Now that employees exists, link stores.manager_id -> employees.employee_id
ALTER TABLE stores
    ADD CONSTRAINT fk_store_manager
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id);


-- ============================================================
-- 3. PRODUCTS
-- ============================================================
CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    product_name  VARCHAR(150) NOT NULL,
    category      VARCHAR(50),
    brand         VARCHAR(50),
    unit_cost     NUMERIC(10, 2),
    unit_price    NUMERIC(10, 2),
    supplier      VARCHAR(50)
);


-- ============================================================
-- 4. CUSTOMERS
-- ============================================================
CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100),
    phone           VARCHAR(20),
    city            VARCHAR(50),
    state           VARCHAR(2),
    region          VARCHAR(20),
    signup_date     DATE,
    loyalty_member  BOOLEAN
);


-- ============================================================
-- 5. INVENTORY  (links stores <-> products)
-- ============================================================
CREATE TABLE inventory (
    inventory_id       INTEGER PRIMARY KEY,
    store_id           INTEGER REFERENCES stores(store_id),
    product_id         INTEGER REFERENCES products(product_id),
    stock_quantity     INTEGER,
    reorder_level      INTEGER,
    last_restock_date  DATE
);


-- ============================================================
-- 6. ORDERS  (the big transactional table)
-- ============================================================
CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),
    product_id      INTEGER REFERENCES products(product_id),
    store_id        INTEGER REFERENCES stores(store_id),
    employee_id     INTEGER REFERENCES employees(employee_id),
    order_date      DATE,
    quantity        INTEGER,
    unit_price      NUMERIC(10, 2),
    discount_pct    NUMERIC(4, 2),
    payment_method  VARCHAR(30),
    order_status    VARCHAR(20)
);


-- ============================================================
-- INDEXES — speed up common joins and filters
-- ============================================================
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id  ON orders(product_id);
CREATE INDEX idx_orders_store_id    ON orders(store_id);
CREATE INDEX idx_orders_order_date  ON orders(order_date);
CREATE INDEX idx_inventory_store_id   ON inventory(store_id);
CREATE INDEX idx_inventory_product_id ON inventory(product_id);


-- ============================================================
-- Quick confirmation query — run this to verify all tables exist
-- ============================================================
-- \dt