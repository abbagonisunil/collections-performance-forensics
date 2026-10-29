-- ============================================================================
-- 03_entity_resolution.sql
-- Entity resolution crosswalks across Borrowers, Accounts, Agents, and Vendor Codes
-- ============================================================================

-- 1. Borrower Crosswalk
CREATE OR REPLACE TABLE dim_borrower_crosswalk AS
SELECT 
    b.borrower_id AS canonical_borrower_id,
    COALESCE(b.external_borrower_id, b.borrower_id) AS external_borrower_id,
    b.phone_hash,
    b.full_name,
    COUNT(DISTINCT a.account_id) AS total_linked_accounts,
    'EXACT_KEY_MATCH' AS match_rule,
    1.0 AS match_confidence
FROM stg_borrowers b
LEFT JOIN stg_accounts a ON b.borrower_id = a.borrower_id
GROUP BY 1, 2, 3, 4;

-- 2. Agent Identity Resolution Crosswalk
-- Detects agents with multiple login usernames or multi-center aliases
CREATE OR REPLACE TABLE dim_agent_crosswalk AS
WITH ranked_agent_logins AS (
    SELECT 
        agent_id,
        login_username,
        agent_name,
        center_location,
        is_active,
        ROW_NUMBER() OVER (PARTITION BY LOWER(TRIM(agent_name)), center_location ORDER BY hire_date DESC, agent_id) AS rank_order,
        FIRST_VALUE(agent_id) OVER (PARTITION BY LOWER(TRIM(agent_name)), center_location ORDER BY hire_date DESC, agent_id) AS canonical_agent_id
    FROM stg_agents
)
SELECT 
    agent_id AS source_agent_id,
    canonical_agent_id,
    login_username,
    agent_name,
    center_location,
    CASE 
        WHEN agent_id = canonical_agent_id THEN 'CANONICAL_PRIMARY'
        ELSE 'RESOLVED_ALIAS'
    END AS resolution_status,
    0.95 AS resolution_confidence
FROM ranked_agent_logins;

-- 3. Telephony Disposition Code Crosswalk
-- Resolves raw vendor-specific disposition codes to canonical RPC / Non-RPC / Unreached categories
CREATE OR REPLACE TABLE ref_disposition_crosswalk AS
WITH raw_codes AS (
    SELECT DISTINCT 
        disposition_code_raw,
        disposition_category_raw
    FROM stg_call_dispositions
)
SELECT 
    disposition_code_raw,
    disposition_category_raw,
    CASE 
        -- Valid Right-Party Contacts
        WHEN disposition_code_raw IN ('RPC_PTP', 'RPC_PROMISE', 'RPC_CALL_BACK', 'RPC_DISPUTE', 'RPC_PAID', 'RPC_SETTLEMENT') THEN 'RPC'
        WHEN disposition_code_raw IN ('RPC', 'CONTACT_VERIFIED', 'BORROWER_CONFIRMED') THEN 'RPC'
        
        -- Non-Right-Party Contacts (Wrong Party, Third Party, Relative)
        WHEN disposition_code_raw IN ('WPC', 'THIRD_PARTY', 'REF_CONTACT', 'WRONG_NUMBER', 'RELATIVE_CONTACT') THEN 'NON_RPC'
        
        -- Unreached (Telephony failure, no answer, busy)
        WHEN disposition_code_raw IN ('NO_ANSWER', 'BUSY', 'SWITCHED_OFF', 'OUT_OF_COVERAGE', 'NETWORK_ERROR', 'ABANDONED', 'IVR_DROP') THEN 'UNREACHED'
        
        -- Fallback to raw category if already clean
        WHEN disposition_category_raw = 'RPC' THEN 'RPC'
        WHEN disposition_category_raw IN ('NON_RPC', 'WPC') THEN 'NON_RPC'
        ELSE 'UNREACHED'
    END AS canonical_disposition_category,
    
    CASE 
        WHEN disposition_code_raw IN ('RPC_PTP', 'RPC_PROMISE') THEN TRUE
        ELSE FALSE
    END AS is_ptp_promise,
    
    'CANONICAL_VENDOR_MAPPING_V2' AS mapping_version
FROM raw_codes;
