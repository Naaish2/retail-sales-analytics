-- PostgreSQL load script for data/processed/walmart_sales_clean.csv.
-- Update the absolute CSV path before running this command in psql.

\copy walmart_sales (
    store,
    dept,
    product,
    order_date,
    weekly_sales,
    revenue,
    quantity,
    unit_price,
    discount,
    holiday_flag,
    temperature,
    fuel_price,
    cpi,
    unemployment,
    store_type,
    store_size,
    region,
    category,
    profit,
    profit_margin,
    customer_segment,
    sales_year,
    sales_month,
    sales_quarter,
    sales_week
)
FROM 'C:/Users/Naais/Documents/data analytics end to end real world project/data/processed/walmart_sales_clean.csv'
WITH (FORMAT csv, HEADER true);
