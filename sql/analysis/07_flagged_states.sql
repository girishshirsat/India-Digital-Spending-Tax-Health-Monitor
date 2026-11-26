-- Business question: which states are flagged most often, and in which direction?
SELECT
    state_name,
    COUNT(*) FILTER (WHERE flag) AS flagged_quarters,
    COUNT(divergence_score) AS scored_quarters,
    ROUND(100.0 * COUNT(*) FILTER (WHERE flag)
          / NULLIF(COUNT(divergence_score), 0), 1) AS flagged_pct,
    COUNT(*) FILTER (WHERE flag AND divergence_score > 0) AS upi_ahead_quarters,
    COUNT(*) FILTER (WHERE flag AND divergence_score < 0) AS gst_ahead_quarters
FROM vw_divergence_scores
GROUP BY state_name
ORDER BY flagged_quarters DESC, state_name;