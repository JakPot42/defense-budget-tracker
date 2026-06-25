"""USASpending.gov API client for P46 Defense Budget & Appropriations Tracker.

Free public API -- no authentication required.
Endpoint: POST /api/v2/search/spending_over_time/

Returns total DoD contract obligations (in $B) for keyword-matched awards,
grouped by fiscal year. Note: this captures CONTRACTED spending only --
not the full DoD appropriation, which includes in-house R&D, classified
programs, and non-contracted spending.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import requests  # type: ignore
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

from config import (
    USASPENDING_SPENDING_OVER_TIME,
    TECH_AREAS,
    TRACKED_FISCAL_YEARS,
    DATA_SOURCE_LIVE,
    DATA_SOURCE_DEMO,
    LIVE_DATA_NOTE,
)
from models import ProgramFunding


class USASpendingError(Exception):
    """Raised when USASpending.gov API call fails."""


def _get_keywords(tech_area: str) -> list[str]:
    """Return the keyword list for a given tech area."""
    if tech_area not in TECH_AREAS:
        raise USASpendingError(f"Unknown tech area: {tech_area!r}. Valid: {list(TECH_AREAS)}")
    return TECH_AREAS[tech_area]["keywords"]


def _build_payload(keywords: list[str]) -> dict:
    return {
        "group": "fiscal_year",
        "filters": {
            "keywords": keywords,
            "agencies": [
                {
                    "type": "awarding",
                    "tier": "toptier",
                    "name": "Department of Defense",
                }
            ],
            "award_type_codes": ["A", "B", "C", "D"],  # contracts only
        },
    }


def fetch_spending_over_time(
    tech_area: str,
    fiscal_years: Optional[list[int]] = None,
    timeout: int = 30,
) -> dict[int, float]:
    """Fetch total DoD contract obligations ($B) by fiscal year for a tech area.

    Returns a dict keyed by fiscal year (int) with values in $B.
    Only returns years present in the API response AND in fiscal_years filter.
    """
    if not _REQUESTS_AVAILABLE:
        raise USASpendingError("requests library not installed. Run: pip install requests")

    target_years = set(fiscal_years or TRACKED_FISCAL_YEARS)
    keywords = _get_keywords(tech_area)
    payload = _build_payload(keywords)

    try:
        resp = requests.post(USASPENDING_SPENDING_OVER_TIME, json=payload, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:
        raise USASpendingError(f"USASpending.gov request failed: {exc}") from exc

    try:
        data = resp.json()
    except Exception as exc:
        raise USASpendingError(f"Failed to parse USASpending response: {exc}") from exc

    results: dict[int, float] = {}
    for item in data.get("results", []):
        try:
            fy = int(item["time_period"]["fiscal_year"])
            amount_billions = round(item["aggregated_amount"] / 1e9, 2)
            if fy in target_years:
                results[fy] = amount_billions
        except (KeyError, TypeError, ValueError):
            continue

    return results


def build_live_funding(
    tech_area: str,
    fiscal_years: Optional[list[int]] = None,
    timeout: int = 30,
) -> dict[int, ProgramFunding]:
    """Fetch live USASpending data and wrap in ProgramFunding objects.

    RDT&E/Procurement/O&M breakdown is NOT available from this endpoint --
    those fields will be None. Total reflects contract obligations only.
    """
    target_years = fiscal_years or TRACKED_FISCAL_YEARS
    raw = fetch_spending_over_time(tech_area, target_years, timeout)

    result: dict[int, ProgramFunding] = {}
    for fy in target_years:
        total = raw.get(fy, 0.0)
        result[fy] = ProgramFunding(
            tech_area=tech_area,
            fiscal_year=fy,
            rdte_billions=None,
            procurement_billions=None,
            om_billions=None,
            total_billions=total,
            data_source=DATA_SOURCE_LIVE,
            notes=LIVE_DATA_NOTE,
        )
    return result
