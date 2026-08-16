-- Monthly sales trend
SELECT
    DATE_TRUNC('month', order_date) AS sales_month,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY sales_month;

-- Top products by revenue
SELECT
    product,
    category,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(discount) AS average_discount,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY product, category
ORDER BY total_revenue DESC
LIMIT 10;

-- Customer segments by revenue
SELECT
    customer_segment,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    COUNT(*) AS order_lines
FROM walmart_sales
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- Region-wise performance
SELECT
    region,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY region
ORDER BY total_profit DESC;

-- Most profitable products
SELECT
    product,
    category,
    SUM(profit) AS total_profit,
    SUM(revenue) AS total_revenue,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY product, category
ORDER BY total_profit DESC
LIMIT 10;

-- Category-wise discount impact
SELECT
    category,
    AVG(discount) AS average_discount,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY category
ORDER BY average_discount DESC;

-- Discount bands vs profit
SELECT
    CASE
        WHEN discount < 0.03 THEN '0-3%'
        WHEN discount < 0.07 THEN '3-7%'
        WHEN discount < 0.12 THEN '7-12%'
        ELSE '12%+'
    END AS discount_band,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(profit_margin) AS average_profit_margin
FROM walmart_sales
GROUP BY
    CASE
        WHEN discount < 0.03 THEN '0-3%'
        WHEN discount < 0.07 THEN '3-7%'
        WHEN discount < 0.12 THEN '7-12%'
        ELSE '12%+'
    END
ORDER BY discount_band;
