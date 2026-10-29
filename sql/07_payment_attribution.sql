-- ============================================================================
-- 07_payment_attribution.sql
-- Omnichannel payment attribution bridge across multiple models and windows
-- ============================================================================

-- Step 1: Candidate Interaction-to-Payment Pairs within Lookback Window (Default 14 days)
CREATE OR REPLACE TABLE bridge_payment_interaction AS
WITH candidate_touches AS (
    SELECT 
        p.payment_id,
        p.account_id,
        p.amount_paid,
        p.payment_timestamp,
        i.interaction_id,
        i.channel,
        i.agent_id,
        i.campaign_id,
        i.interaction_timestamp,
        i.is_rpc,
        -- Time delta in days between interaction and payment
        EXTRACT(EPOCH FROM (p.payment_timestamp - i.interaction_timestamp)) / 86400.0 AS touch_lag_days,
        ROW_NUMBER() OVER (
            PARTITION BY p.payment_id 
            ORDER BY i.interaction_timestamp DESC
        ) AS last_touch_rank,
        ROW_NUMBER() OVER (
            PARTITION BY p.payment_id 
            ORDER BY i.interaction_timestamp ASC
        ) AS first_touch_rank,
        COUNT(*) OVER (
            PARTITION BY p.payment_id
        ) AS total_touches_in_window
    FROM fact_payment p
    INNER JOIN fact_interaction i 
        ON p.account_id = i.account_id
        AND i.interaction_timestamp <= p.payment_timestamp
        AND i.interaction_timestamp >= (p.payment_timestamp - INTERVAL 14 DAY)
)
SELECT 
    payment_id,
    account_id,
    amount_paid,
    payment_timestamp,
    interaction_id,
    channel,
    agent_id,
    campaign_id,
    interaction_timestamp,
    is_rpc,
    touch_lag_days,
    last_touch_rank,
    first_touch_rank,
    total_touches_in_window,
    
    -- Model 1: Last Touch Attribution Weight (1.0 for most recent touch, 0 otherwise)
    CASE WHEN last_touch_rank = 1 THEN 1.0 ELSE 0.0 END AS weight_last_touch,
    
    -- Model 2: First Touch Attribution Weight (1.0 for first touch, 0 otherwise)
    CASE WHEN first_touch_rank = 1 THEN 1.0 ELSE 0.0 END AS weight_first_touch,
    
    -- Model 3: Linear Multi-Touch Weight (Equal 1/N split)
    1.0 / NULLIF(total_touches_in_window, 0) AS weight_linear_multi_touch,
    
    -- Model 4: Time-Decay Weight (Half-life = 3.5 days: 2^(-delta / 3.5))
    POWER(2.0, - (touch_lag_days / 3.5)) AS raw_decay_weight
FROM candidate_touches;

-- Step 2: Time-Decay Normalized Attribution Weights
CREATE OR REPLACE TABLE fact_payment_attribution AS
WITH decay_sums AS (
    SELECT 
        payment_id,
        SUM(raw_decay_weight) AS sum_decay_weights
    FROM bridge_payment_interaction
    GROUP BY payment_id
)
SELECT 
    b.payment_id,
    b.account_id,
    b.amount_paid,
    b.payment_timestamp,
    b.interaction_id,
    b.channel,
    b.agent_id,
    b.campaign_id,
    b.touch_lag_days,
    b.weight_last_touch,
    b.weight_first_touch,
    b.weight_linear_multi_touch,
    b.raw_decay_weight / NULLIF(d.sum_decay_weights, 0) AS weight_time_decay,
    
    -- Monetary Attributions across Models
    ROUND(b.amount_paid * b.weight_last_touch, 2) AS attributed_inr_last_touch,
    ROUND(b.amount_paid * b.weight_first_touch, 2) AS attributed_inr_first_touch,
    ROUND(b.amount_paid * b.weight_linear_multi_touch, 2) AS attributed_inr_linear,
    ROUND(b.amount_paid * (b.raw_decay_weight / NULLIF(d.sum_decay_weights, 0)), 2) AS attributed_inr_time_decay
FROM bridge_payment_interaction b
JOIN decay_sums d ON b.payment_id = d.payment_id;

-- Step 3: Attribution Comparison by Channel (Comparing Models and Unattributed Organic Recovery)
CREATE OR REPLACE VIEW v_attribution_channel_comparison AS
WITH attributed_totals AS (
    SELECT 
        channel,
        ROUND(SUM(attributed_inr_last_touch), 2) AS collections_last_touch,
        ROUND(SUM(attributed_inr_first_touch), 2) AS collections_first_touch,
        ROUND(SUM(attributed_inr_linear), 2) AS collections_linear,
        ROUND(SUM(attributed_inr_time_decay), 2) AS collections_time_decay
    FROM fact_payment_attribution
    GROUP BY 1
),
unattributed_summary AS (
    SELECT 
        'ORGANIC_UNATTRIBUTED' AS channel,
        ROUND(SUM(p.amount_paid), 2) AS collections_last_touch,
        ROUND(SUM(p.amount_paid), 2) AS collections_first_touch,
        ROUND(SUM(p.amount_paid), 2) AS collections_linear,
        ROUND(SUM(p.amount_paid), 2) AS collections_time_decay
    FROM fact_payment p
    LEFT JOIN (SELECT DISTINCT payment_id FROM fact_payment_attribution) a ON p.payment_id = a.payment_id
    WHERE a.payment_id IS NULL
)
SELECT * FROM attributed_totals
UNION ALL
SELECT * FROM unattributed_summary
ORDER BY 2 DESC;
