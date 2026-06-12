"""
Application constants for tenants module.
Centralized definition for consistency & easy maintenance.
"""

# Plan types
PLAN_TRIAL = "TRIAL"
PLAN_STANDARD = "STANDARD"
PLAN_PROFESSIONAL = "PROFESSIONAL"
PLAN_ENTERPRISE = "ENTERPRISE"

PLAN_CHOICES = [PLAN_TRIAL, PLAN_STANDARD, PLAN_PROFESSIONAL, PLAN_ENTERPRISE]

# Plan limits
PLAN_LIMITS = {
    PLAN_TRIAL: {
        "duration_days": 30,
        "max_users": 3,
        "max_branches": 1,
        "max_vehicles": 10,
        "features": ["basic_ticketing", "basic_reporting"],
    },
    PLAN_STANDARD: {
        "max_users": 10,
        "max_branches": 1,
        "max_vehicles": 50,
        "features": ["ticketing", "hr", "basic_cargo", "reporting"],
    },
    PLAN_PROFESSIONAL: {
        "max_users": 50,
        "max_branches": 5,
        "max_vehicles": 200,
        "features": ["ticketing", "hr", "cargo", "reporting", "api"],
    },
    PLAN_ENTERPRISE: {
        "max_users": 999,
        "max_branches": 999,
        "max_vehicles": 9999,
        "features": ["all"],
    },
}

# Feature flags
FEATURE_TICKETING = "TICKETING"
FEATURE_HR = "HR"
FEATURE_CARGO = "CARGO"
FEATURE_API = "API"
FEATURE_REPORTING = "REPORTING"

# Currencies
CURRENCY_VND = "VND"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
CURRENCY_LAK = "LAK"
CURRENCY_KHR = "KHR"

# Languages
LANG_VI = "vi"
LANG_EN = "en"
LANG_LO = "lo"
LANG_KM = "km"

# Timezones
TZ_HCM = "Asia/Ho_Chi_Minh"
TZ_VIENTIANE = "Asia/Vientiane"
TZ_PHNOM_PENH = "Asia/Phnom_Penh"
TZ_BANGKOK = "Asia/Bangkok"

# Sort
SORT_CHOICES = [
    ("", "Sắp xếp theo"),
    ("az", "Tên: A → Z"),
    ("za", "Tên: Z → A"),
    ("latest", "Mới nhất"),
    ("oldest", "Cũ nhất"),
]

# Plans
PLAN_CHOICES = (
    ("TRIAL", "Trial"),
    ("STANDARD", "Standard"),
    ("PROFESSIONAL", "Professional"),
    ("ENTERPRISE", "Enterprise"),
)

# Status
STATUS_CHOICES = (
    ("True", "Kích hoạt"),
    ("False", "Khóa"),
)

# Column
COLUMN_CHOICES = [
    ("code", "Code"),
    ("name", "Tên Tenant"),
]
