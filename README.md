# End-to-End Retail Sales Analytics Project

## Project Focus

This project analyzes a Walmart-style retail sales dataset to help leadership understand revenue, profit, customer behavior, product trends, discount impact, and regional performance.

The project is designed around the common Walmart sales dataset format:

- `Store`
- `Date`
- `Weekly_Sales`
- `Holiday_Flag` or `IsHoliday`
- `Temperature`
- `Fuel_Price`
- `CPI`
- `Unemployment`
- optional fields such as `Dept`, `Type`, `Size`, `Region`, `Category`, `Profit`, and `Customer_Segment`

## Project Flow

### 1. Business Understanding

Key questions:

1. Which stores or departments generate the highest weekly sales?
2. How do holidays affect sales performance?
3. What sales patterns appear over months, quarters, and years?
4. Which stores have volatile or declining sales trends?
5. How do economic indicators such as CPI, fuel price, unemployment, and temperature relate to sales?
6. Which products generate the most revenue?
7. Which regions are most profitable?
8. Which customer segments buy the most?
9. Are discounts increasing or hurting profit?

### 2. Data Collection

Use a CSV, Excel workbook, SQL database export, or Kaggle Walmart dataset. Put the source file in `data/raw/`.

### 3. Data Cleaning

Cleaning tasks covered by the Python pipeline:

- Remove duplicate rows
- Handle missing values in required fields
- Fix date formats
- Standardize common Walmart column names
- Create `Profit_Margin`, `Month`, `Quarter`, and `Week` fields

### 4. Exploratory Data Analysis

The output files analyze:

- Total sales and total profit
- Monthly revenue trend
- Top products and departments
- Sales by region
- Profit by category
- Discount vs profit relationship

### 5. SQL Analysis

Reusable SQL is available in `sql/analysis_queries.sql`, including:

- Monthly sales trend
- Top customers or customer segments by revenue
- Most profitable products
- Region-wise performance
- Category-wise discount impact

The SQL files use PostgreSQL syntax. Use `sql/load_postgres.sql` to load the cleaned CSV into the SQL schema.

### 6. Python Analysis

The Python scripts use:

- pandas
- numpy

The notebook-style EDA file is in `notebooks/retail_sales_eda.ipynb`.

### 7. Dashboard

The included dashboard is a static browser dashboard, and the same model can be rebuilt in Power BI, Tableau, Excel, or Streamlit.

Dashboard pages/sections:

- Executive overview
- Sales trends
- Product analysis
- Customer analysis
- Regional performance

### 8. Insights

Example insights from the generated sample data:

- Large-format stores drive the largest share of revenue.
- Holiday weeks increase sales but can also increase discount pressure.
- Some high-discount groups produce lower profit margins.
- Customer segment performance can be used for targeted promotions.

### 9. Recommendations

- Reduce discounts on low-margin products.
- Increase inventory for top-selling products before seasonal peaks.
- Focus marketing on high-value customer segments.
- Improve pricing and promotion strategy in low-performing regions.

## Folder Structure

```text
data/
  raw/                 Put your original Walmart CSV here
  sample/              Generated sample Walmart-style data
  processed/           Cleaned data produced by scripts
dashboard/             Static browser dashboard
notebooks/             Python EDA notebook
outputs/               Analysis summaries and exports
reports/               Business insight report
sql/                   SQL schema and analysis queries
src/                   Data generation and analysis scripts
```

## Quick Start

Generate sample data and summary outputs:

```powershell
python src/generate_sample_walmart_data.py
python src/analyze_walmart_sales.py --input data/sample/walmart_sales_sample.csv
```

Open the dashboard:

```powershell
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000/dashboard/
```

## Using Your Own Walmart Dataset

Place your CSV in `data/raw/`, then run:

```powershell
python src/analyze_walmart_sales.py --input data/raw/your_walmart_file.csv
```

The dashboard also has a CSV upload control, so you can load your dataset directly in the browser.

## Deliverables

- Data cleaning pipeline
- Exploratory analysis summaries
- SQL query library
- Python EDA notebook
- KPI dashboard
- Store, holiday, and time-series analysis
- Recommendations framework for inventory, marketing, and pricing decisions

## Final Portfolio Deliverables

- Cleaned dataset: `data/processed/walmart_sales_clean.csv`
- SQL queries: `sql/analysis_queries.sql`
- Python notebook: `notebooks/retail_sales_eda.ipynb`
- Interactive dashboard: `dashboard/index.html`
- Business insight report: `reports/business_insights.md`
- GitHub README: this file
