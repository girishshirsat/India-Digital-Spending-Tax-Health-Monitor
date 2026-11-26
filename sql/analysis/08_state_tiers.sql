-- Business question: which states are in the top, middle and bottom third
-- of UPI amount in the latest quarter (2024 Q4)?
SELECT
    state_name,
    total_amount,
    NTILE(3) OVER (ORDER BY total_amount DESC) AS tier
FROM vw_state_quarter_metrics
WHERE year = 2024 AND quarter = 4
ORDER BY tier, total_amount DESC;