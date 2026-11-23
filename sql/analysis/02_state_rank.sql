-- Business question: which 5 states have the highest UPI amount in each quarter?
WITH ranked AS (
    SELECT
        state_name,
        year,
        quarter,
        total_amount,
        RANK() OVER (
            PARTITION BY year, quarter ORDER BY total_amount DESC
        ) AS amount_rank,
        DENSE_RANK() OVER (
            PARTITION BY year, quarter ORDER BY total_amount DESC
        ) AS amount_dense_rank
    FROM vw_state_quarter_metrics
)
SELECT *
FROM ranked
WHERE amount_rank <= 5
ORDER BY amount_rank;