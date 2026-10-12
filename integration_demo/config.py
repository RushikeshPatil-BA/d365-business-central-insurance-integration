"""Business configuration for the integration demo.

In production these values would live in configuration tables or app settings,
never hard-coded in integration logic (see BRD rule BR-02).
"""

# Chart of accounts (BC numbers - see docs/06_data_migration.md)
GL_PREMIUM_INCOME = "4000"
GL_IPT_PAYABLE = "2310"
GL_CLAIMS_PAID = {
    "TRAVEL": "5100",  # Claims Paid - Travel
    "PMI": "5200",     # Claims Paid - Private Medical
}

# Dimensions (FR-GL-02)
VALID_PRODUCTS = {"TRAVEL", "PMI"}
VALID_CHANNELS = {"DIRECT", "BROKER", "AFFINITY"}

# Claims payments (INT-02)
CLAIMS_JOURNAL_CODE = "CLAIMS-PAY"
AUTHORITY_LIMIT = 10_000.00  # BR-02: payments at or above this need a second approver in BC

# Bank reconciliation (INT-03)
DATE_WINDOW_DAYS = 3  # FR-BR-02 rule 2

# API resilience (NFR-05)
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 5
