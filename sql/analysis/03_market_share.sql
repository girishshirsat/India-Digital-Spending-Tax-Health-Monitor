-- Business question: what share of India's UPI amount does each state have in each quarter?
SELECT
    state_name,
    year,
    quarter,
    total_amount,
    SUM(total_amount) OVER (PARTITION BY year, quarter) AS india_total,
    ROUND(
        100.0 * total_amount / SUM(total_amount) OVER (PARTITION BY year, quarter),
        2
    ) AS market_share_pct
FROM vw_state_quarter_metrics
ORDER BY market_share_pct DESC;