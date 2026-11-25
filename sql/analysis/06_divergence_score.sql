
-- Business question:
-- How much does UPI amount growth exceed CPI inflation
-- across Indian states, after adjusting for inflation?

WITH upi_growth AS (
    SELECT
        state_name,
        year,
        quarter,
        total_amount,
        cpi_yoy,

        LAG(total_amount, 4) OVER (PARTITION BY state_nameORDER BY year, quarter) AS previous_year_amount

    FROM vw_state_quarter_metrics
    -- WHERE state_name = 'maharashtra'
),

growth_calculation AS (
    SELECT
        state_name,
        year,
        quarter,
        total_amount,
        previous_year_amount,
        cpi_yoy,

        ROUND((total_amount - previous_year_amount) * 100.0/ NULLIF(previous_year_amount, 0),2) AS upi_yoy_pct

    FROM upi_growth
)

SELECT
    state_name,
    year,
    quarter,
    total_amount,
    previous_year_amount,
    upi_yoy_pct,
    ROUND(cpi_yoy, 2) AS cpi_yoy,
    ROUND(upi_yoy_pct - cpi_yoy, 2) AS real_growth_pct

FROM growth_calculation

ORDER BY state_name, year, quarter;
