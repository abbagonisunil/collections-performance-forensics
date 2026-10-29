"""SYNTHETIC TEST FIXTURES - FOR SOFTWARE UNIT TESTING ONLY.

WARNING: These fixtures are strictly synthetic mock records designed to test
data validation, deduplication algorithms, and mathematical invariants in unit tests.
THEY MUST NEVER BE USED FOR BUSINESS ANALYSIS OR LEADERSHIP REPORTING.
"""

import pandas as pd
from datetime import datetime, timedelta

# 1. Synthetic Payments Fixture
# Designed to test: exact duplicate ref, 5-minute replay retry, failed status, and valid payment
SYNTHETIC_PAYMENTS_DATA = [
    {
        "payment_id": "PAY_001",
        "transaction_reference": "UTR_VALID_101",
        "account_id": "ACC_1001",
        "amount_paid": 5000.0,
        "principal_component": 4000.0,
        "interest_component": 800.0,
        "fee_component": 200.0,
        "payment_method": "UPI",
        "payment_status": "SUCCESS",
        "payment_timestamp": "2024-03-10 10:15:00",
        "settlement_timestamp": "2024-03-10 10:15:30"
    },
    {
        "payment_id": "PAY_002",
        "transaction_reference": "UTR_VALID_101", # EXACT REF DUPLICATE of PAY_001
        "account_id": "ACC_1001",
        "amount_paid": 5000.0,
        "principal_component": 4000.0,
        "interest_component": 800.0,
        "fee_component": 200.0,
        "payment_method": "UPI",
        "payment_status": "SUCCESS",
        "payment_timestamp": "2024-03-10 10:16:00",
        "settlement_timestamp": "2024-03-10 10:16:30"
    },
    {
        "payment_id": "PAY_003",
        "transaction_reference": "UTR_RETRY_102",
        "account_id": "ACC_1002",
        "amount_paid": 3000.0,
        "principal_component": 3000.0,
        "interest_component": 0.0,
        "fee_component": 0.0,
        "payment_method": "NETBANKING",
        "payment_status": "SUCCESS",
        "payment_timestamp": "2024-04-12 14:00:00",
        "settlement_timestamp": "2024-04-12 14:05:00"
    },
    {
        "payment_id": "PAY_004", # REPLAY RETRY: same account ACC_1002, same amount 3000, 3 mins later
        "transaction_reference": "UTR_RETRY_103",
        "account_id": "ACC_1002",
        "amount_paid": 3000.0,
        "principal_component": 3000.0,
        "interest_component": 0.0,
        "fee_component": 0.0,
        "payment_method": "NETBANKING",
        "payment_status": "SUCCESS",
        "payment_timestamp": "2024-04-12 14:03:00",
        "settlement_timestamp": "2024-04-12 14:08:00"
    },
    {
        "payment_id": "PAY_005", # FAILED TRANSACTION
        "transaction_reference": "UTR_FAIL_104",
        "account_id": "ACC_1003",
        "amount_paid": 12000.0,
        "principal_component": 10000.0,
        "interest_component": 2000.0,
        "fee_component": 0.0,
        "payment_method": "DEBIT_CARD",
        "payment_status": "FAILED",
        "payment_timestamp": "2024-05-15 11:00:00",
        "settlement_timestamp": "2024-05-15 11:00:05"
    },
    {
        "payment_id": "PAY_006", # VALID PAYMENT
        "transaction_reference": "UTR_VALID_105",
        "account_id": "ACC_1003",
        "amount_paid": 12000.0,
        "principal_component": 10000.0,
        "interest_component": 2000.0,
        "fee_component": 0.0,
        "payment_method": "DEBIT_CARD",
        "payment_status": "SUCCESS",
        "payment_timestamp": "2024-05-15 11:20:00",
        "settlement_timestamp": "2024-05-15 11:25:00"
    }
]

# 2. Synthetic Accounts Fixture
SYNTHETIC_ACCOUNTS_DATA = [
    {
        "account_id": "ACC_1001",
        "borrower_id": "BOR_501",
        "client_name": "FINTECH_A",
        "product_type": "PERSONAL_LOAN",
        "disbursed_amount": 50000.0,
        "opening_principal": 40000.0,
        "current_outstanding": 35000.0,
        "dpd": 15,
        "dpd_bucket": "DPD 1-30",
        "status": "ACTIVE",
        "disbursed_at": "2023-11-01 00:00:00",
        "due_date": "2024-03-05 00:00:00"
    },
    {
        "account_id": "ACC_1002",
        "borrower_id": "BOR_502",
        "client_name": "BANK_B",
        "product_type": "CREDIT_LINE",
        "disbursed_amount": 25000.0,
        "opening_principal": 20000.0,
        "current_outstanding": 17000.0,
        "dpd": 45,
        "dpd_bucket": "DPD 31-60",
        "status": "ACTIVE",
        "disbursed_at": "2023-12-01 00:00:00",
        "due_date": "2024-04-05 00:00:00"
    },
    {
        "account_id": "ACC_1003",
        "borrower_id": "BOR_503",
        "client_name": "NBFC_C",
        "product_type": "PERSONAL_LOAN",
        "disbursed_amount": 100000.0,
        "opening_principal": 80000.0,
        "current_outstanding": 68000.0,
        "dpd": 75,
        "dpd_bucket": "DPD 61-90",
        "status": "ACTIVE",
        "disbursed_at": "2024-01-01 00:00:00",
        "due_date": "2024-05-05 00:00:00"
    }
]

# 3. Synthetic Calls & Dispositions Fixture
SYNTHETIC_CALLS_DATA = [
    {
        "call_id": "CALL_901",
        "account_id": "ACC_1001",
        "agent_id": "AGT_01",
        "campaign_id": "CMP_EARLY",
        "call_start_time": "2024-03-08 11:00:00",
        "call_end_time": "2024-03-08 11:03:30",
        "duration_seconds": 210,
        "call_type": "OUTBOUND_PREDICTIVE",
        "vendor_id": "VENDOR_X",
        "status": "COMPLETED"
    },
    {
        "call_id": "CALL_902",
        "account_id": "ACC_1002",
        "agent_id": "AGT_02",
        "campaign_id": "CMP_MID",
        "call_start_time": "2024-04-10 14:00:00",
        "call_end_time": "2024-04-10 14:01:00",
        "duration_seconds": 60,
        "call_type": "OUTBOUND_PREDICTIVE",
        "vendor_id": "VENDOR_Y",
        "status": "COMPLETED"
    }
]

SYNTHETIC_DISPOSITIONS_DATA = [
    {
        "disposition_id": "DISP_01",
        "call_id": "CALL_901",
        "disposition_code": "RPC_PTP",
        "disposition_category": "RPC",
        "sub_disposition": "PROMISE_MADE",
        "disposition_time": "2024-03-08 11:03:30",
        "agent_notes": "Borrower agreed to pay 5000 on March 10"
    },
    {
        "disposition_id": "DISP_02",
        "call_id": "CALL_902",
        "disposition_code": "RPC_CALL_BACK",
        "disposition_category": "RPC",
        "sub_disposition": "CALLBACK_REQUESTED",
        "disposition_time": "2024-04-10 14:01:00",
        "agent_notes": "Call back tomorrow afternoon"
    }
]

SYNTHETIC_PROMISES_DATA = [
    {
        "ptp_id": "PTP_001",
        "account_id": "ACC_1001",
        "call_id": "CALL_901",
        "agent_id": "AGT_01",
        "channel_origin": "CALL",
        "ptp_created_time": "2024-03-08 11:03:30",
        "promised_due_date": "2024-03-10",
        "promised_amount": 5000.0,
        "status": "KEPT"
    }
]
