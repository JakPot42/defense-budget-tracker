"""Configuration constants for P46 Defense Budget & Appropriations Tracker."""

# ---- API endpoints ----------------------------------------------------------
USASPENDING_BASE = "https://api.usaspending.gov/api/v2"
USASPENDING_SPENDING_OVER_TIME = f"{USASPENDING_BASE}/search/spending_over_time/"
CONGRESS_BASE = "https://api.congress.gov/v3"

# ---- Fiscal years tracked ---------------------------------------------------
TRACKED_FISCAL_YEARS = [2022, 2023, 2024, 2025, 2026]
DEFAULT_START_FY = 2022
DEFAULT_END_FY = 2026

# ---- Technology areas -------------------------------------------------------
TECH_AREAS = {
    "AI/ML": {
        "label": "Artificial Intelligence & Machine Learning",
        "keywords": [
            "artificial intelligence", "machine learning", "AI systems",
            "autonomous systems AI", "CDAO", "predictive analytics defense",
        ],
        "dod_component": "CDAO",  # Chief Digital and AI Office
        "short_code": "AI_ML",
    },
    "Hypersonics": {
        "label": "Hypersonic Weapons & Glide Vehicles",
        "keywords": [
            "hypersonic", "hypersonic glide", "conventional prompt strike",
            "ARRW", "HACM", "CPS hypersonic", "Long Range Hypersonic Weapon",
        ],
        "dod_component": "DARPA/Services",
        "short_code": "HYPERS",
    },
    "Space": {
        "label": "Space Systems & Space Force",
        "keywords": [
            "Space Force", "space systems", "satellite communications defense",
            "Space Development Agency", "OPIR", "National Security Space Launch",
        ],
        "dod_component": "USSF",
        "short_code": "SPACE",
    },
    "Cyber": {
        "label": "Cyberspace Operations & Defense",
        "keywords": [
            "cyberspace operations", "CYBERCOM", "cyber defense", "cyber warfare",
            "network defense", "defensive cyber operations", "cyber mission force",
        ],
        "dod_component": "USCYBERCOM",
        "short_code": "CYBER",
    },
}

TECH_AREA_NAMES = list(TECH_AREAS.keys())

# ---- Budget categories ------------------------------------------------------
BUDGET_CATEGORIES = {
    "RDT&E": {
        "label": "Research, Development, Test & Evaluation",
        "description": "Budget Activities 1-7; program elements for basic/applied research and development",
        "psc_prefix": ["A", "B"],  # Research and Development PSC codes
    },
    "Procurement": {
        "label": "Procurement",
        "description": "Budget Activity 8; production and deployment of fielded systems",
        "psc_prefix": ["E", "F", "G", "H"],  # Equipment PSC codes
    },
    "O&M": {
        "label": "Operations & Maintenance",
        "description": "Budget Activities 1-4 (O&M appropriation); sustainment and readiness",
        "psc_prefix": ["J", "S", "V", "W", "Z"],  # Maintenance/services PSC codes
    },
}

# ---- Trend thresholds -------------------------------------------------------
CAGR_STRONG_GROWTH = 20.0   # % — e.g. doubling every 4 years
CAGR_GROWING = 5.0           # %
CAGR_FLAT_LOW = -5.0         # %
CAGR_CUT = -20.0             # % — significant cut

YOY_STRONG_GROWTH = 20.0
YOY_GROWING = 5.0
YOY_FLAT_LOW = -5.0
YOY_CUT = -20.0

# Trend labels
TREND_STRONG_GROWTH = "STRONG_GROWTH"
TREND_GROWING = "GROWING"
TREND_FLAT = "FLAT"
TREND_CUT = "CUT"
TREND_STRONG_CUT = "STRONG_CUT"
TREND_NEW_START = "NEW_START"
TREND_VOLATILE = "VOLATILE"
TREND_UNKNOWN = "UNKNOWN"

TREND_LABELS = {
    TREND_STRONG_GROWTH: "Strong Growth (>20% CAGR)",
    TREND_GROWING: "Growing (5-20% CAGR)",
    TREND_FLAT: "Flat (-5% to +5% CAGR)",
    TREND_CUT: "Cut (-5% to -20% CAGR)",
    TREND_STRONG_CUT: "Strong Cut (>20% reduction)",
    TREND_NEW_START: "New Start (first funding)",
    TREND_VOLATILE: "Volatile (high variance)",
    TREND_UNKNOWN: "Unknown",
}

# ---- Congress / NDAA mapping ------------------------------------------------
# Each fiscal year's NDAA belongs to a specific Congress
FY_TO_CONGRESS = {
    2022: 117,
    2023: 117,
    2024: 118,
    2025: 118,
    2026: 119,
}

# Known NDAA HR bill numbers for reference
NDAA_BILL_NUMBERS = {
    2022: ("hr", "4350"),   # H.R. 4350 → P.L. 117-81
    2023: ("hr", "7776"),   # H.R. 7776 → P.L. 117-263
    2024: ("hr", "2670"),   # H.R. 2670 → P.L. 118-31
    2025: ("hr", "5009"),   # H.R. 5009 (118th Congress FY2025 NDAA)
    2026: ("hr", "3116"),   # H.R. 3116 (119th Congress FY2026 NDAA — pending)
}

# ---- Display ----------------------------------------------------------------
DATA_SOURCE_DEMO = "DEMO"
DATA_SOURCE_LIVE = "LIVE"

DATA_DISCLAIMER = (
    "DATA NOTE: DEMO MODE -- figures represent illustrative estimates seeded from "
    "public DoD budget documents and Congressional Research Service reports. "
    "Live mode queries USASpending.gov contract awards (free, no auth required) "
    "and congress.gov NDAA summaries (requires free CONGRESS_API_KEY). "
    "USASpending figures reflect contract obligations only, not full DoD appropriations "
    "(excludes in-house R&D, classified programs, and non-contracted spending)."
)

LIVE_DATA_NOTE = (
    "LIVE DATA -- USASpending.gov contract obligations for DoD keyword search. "
    "This reflects CONTRACTED spending only; full DoD program element budgets "
    "are available in DoD Budget Justification documents at comptroller.defense.gov."
)
