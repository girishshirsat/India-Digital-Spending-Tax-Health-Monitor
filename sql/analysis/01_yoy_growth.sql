-- Business question: how fast is UPI amount growing in a state
-- compared with the same quarter last year?
SELECT
    state_name,
    year,
    quarter,
    total_amount,
    LAG(total_amount, 4) OVER (PARTITION BY state_name ORDER BY year, quarter) AS amount_last_year,
    ROUND(
        100.0 * (total_amount - LAG(total_amount, 4) OVER (PARTITION BY state_name ORDER BY year, quarter))
        / LAG(total_amount, 4) OVER (PARTITION BY state_name ORDER BY year, quarter),
        2
    ) AS upi_amount_yoy_pct
FROM vw_state_quarter_metrics
ORDER BY year, quarter;