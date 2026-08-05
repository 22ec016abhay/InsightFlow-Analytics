# InsightFlow Analytics

**A production-grade retail analytics platform built with Python, PostgreSQL, Pandas, NumPy, Matplotlib, and OpenPyXL.**

InsightFlow Analytics simulates a real retail company's data pipeline — from raw, messy operational data all the way to cleaned datasets, a live PostgreSQL database, business intelligence dashboards, automated charts, and polished Excel reports. Built as a portfolio project to demonstrate professional Python architecture, SQL, and end-to-end data analysis.

---

## Overview

Retail companies generate data across many disconnected systems — point-of-sale, inventory, HR, e-commerce — and that data is rarely clean. InsightFlow Analytics models this reality with six related datasets (Stores, Employees, Products, Customers, Inventory, Orders) containing realistic, intentional data quality issues: duplicate records, missing values, invalid dates, negative quantities, and inconsistent formatting.

The project takes that messy data through a full professional pipeline:

```
Raw CSVs  →  Validation  →  Cleaning  →  PostgreSQL  →  Analysis  →  Charts + Excel Report
```

Everything is driven by a single interactive command-line menu (`main.py`).

---

## Features

- **Realistic relational datasets** — 15 stores, 50 employees, 300 products, 2,000 customers, 2,600+ inventory records, 15,000 orders, all properly joinable
- **Data validation** — automated detection of duplicates, missing values, negative numbers, invalid dates, and statistical outliers (IQR method)
- **Data cleaning** — deduplication, missing-value imputation, type correction, outlier handling, and feature engineering, all using Pandas/NumPy
- **PostgreSQL database** — normalized schema with primary keys, foreign keys, indexes, and a Python connection layer using context managers
- **Business analytics** — monthly/daily sales, average order value, top customers, best/worst products, category performance, store & regional performance, inventory stock alerts
- **Automated visualizations** — 8 chart types (line, bar, pie, histogram, scatter, box plot, correlation heatmap) saved automatically
- **Professional Excel reports** — multi-sheet workbook with formatted headers, filters, totals, and a summary dashboard, built with OpenPyXL
- **Interactive CLI** — a numbered menu tying every module together, including live SQL analytics queries
- **Unit tests** — 19 passing pytest tests covering cleaning logic, validation checks, and model calculations
- **Centralized logging** — every module logs to both console and file via a shared logging utility

---

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.12 |
| Database | PostgreSQL |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib |
| Reporting | OpenPyXL |
| Database Driver | psycopg2 |
| Testing | pytest |
| Environment | python-dotenv, venv |

---

## Folder Structure

```
InsightFlow-Analytics/
├── main.py                    # Interactive CLI entry point
├── config.py                  # Central configuration (paths, DB settings)
├── requirements.txt
├── .env.example
├── .gitignore
├── datasets/
│   ├── raw/                   # Original, messy CSV data
│   └── processed/             # Cleaned, analysis-ready CSV data
├── database/
│   ├── create_tables.sql      # Production schema (PK/FK/indexes)
│   └── create_staging_tables.sql
├── reports/
│   ├── charts/                # Auto-generated PNG charts
│   └── InsightFlow_Business_Report.xlsx
├── logs/
│   └── insightflow.log
├── src/
│   ├── config.py
│   ├── utils.py                # Logging + decorators
│   ├── database.py             # PostgreSQL connection layer
│   ├── models.py                # Dataclasses (Order, Customer, Product...)
│   ├── loader.py                # DB → model objects
│   ├── validator.py             # Data quality checks
│   ├── cleaner.py               # Data cleaning pipeline
│   ├── analyzer.py              # Business analytics
│   ├── visualizer.py            # Chart generation
│   ├── report_generator.py      # Excel report generation
│   └── dashboard.py             # Orchestrates the full pipeline
└── tests/
    ├── test_models.py
    ├── test_cleaner.py
    └── test_validator.py
```

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/InsightFlow-Analytics.git
cd InsightFlow-Analytics
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up PostgreSQL**
```bash
psql -U postgres -c "CREATE DATABASE insightflow_db;"
psql -U postgres -d insightflow_db -f database/create_tables.sql
```

**5. Configure environment variables**
```bash
cp .env.example .env
# then edit .env with your real PostgreSQL credentials
```

**6. Load the data**
Import the CSVs in `datasets/raw/` into their matching PostgreSQL tables (via pgAdmin's Import/Export tool, or `\copy` in `psql`).

---

## Usage

Run the interactive menu:
```bash
python main.py
```

```
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
```

Or run the full pipeline directly:
```bash
python src/dashboard.py
```

Run the test suite:
```bash
python -m pytest tests/ -v
```

---

## Screenshots

*(Add your own screenshots here — the interactive menu, a chart from `reports/charts/`, and a sheet from the Excel report make great additions.)*

---

## Future Improvements

- Add a customer lifetime value (CLV) prediction model
- Build a web dashboard (Streamlit or Flask) as an alternative to the CLI
- Add CI/CD with GitHub Actions to run tests automatically on push
- Expand test coverage to `analyzer.py` and `report_generator.py`
- Add Docker support for one-command environment setup
- Support incremental/streaming data loads instead of full CSV imports

---

## Author

Built as a portfolio project to demonstrate professional Python, SQL, and data analytics skills.