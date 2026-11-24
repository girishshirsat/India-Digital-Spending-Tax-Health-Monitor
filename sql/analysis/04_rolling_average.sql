-- Business question: what is the smoothed UPI trend of a state,
-- using the average of the last 4 quarters?
WITH windowed AS (
    SELECT
        state_name,
        year,
        quarter,
        total_amount,
        AVG(total_amount) OVER w AS avg_4q,
        COUNT(total_amount) OVER w AS quarters_in_window
    FROM vw_state_quarter_metrics
    WINDOW w AS (
        PARTITION BY state_name
        ORDER BY year, quarter
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    )
)
SELECT
    state_name,
    year,
    quarter,
    total_amount,
    CASE WHEN quarters_in_window = 4 THEN ROUND(avg_4q, 0) END AS rolling_avg_4q
FROM windowed
ORDER BY year, quarter;