"""congress.gov API client for P46 Defense Budget & Appropriations Tracker.

Free API -- requires a free API key from https://api.congress.gov/sign-up/
Set CONGRESS_API_KEY environment variable.

Falls back to demo data gracefully if the key is not set.
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
    CONGRESS_BASE,
    FY_TO_CONGRESS,
    NDAA_BILL_NUMBERS,
    DATA_SOURCE_LIVE,
    DATA_SOURCE_DEMO,
    TECH_AREAS,
)
from models import NdaaContext
from seed_data import DEMO_NDAA_CONTEXT


class CongressClientError(Exception):
    """Raised when congress.gov API call fails."""


def get_api_key() -> Optional[str]:
    return os.environ.get("CONGRESS_API_KEY")


def has_api_key() -> bool:
    return bool(get_api_key())


def fetch_ndaa_summary(congress_num: int, bill_type: str, bill_number: str, timeout: int = 30) -> str:
    """Fetch NDAA bill summary text from congress.gov."""
    if not _REQUESTS_AVAILABLE:
        raise CongressClientError("requests library not installed. Run: pip install requests")
    api_key = get_api_key()
    if not api_key:
        raise CongressClientError(
            "CONGRESS_API_KEY environment variable not set. "
            "Get a free key at https://api.congress.gov/sign-up/"
        )

    url = f"{CONGRESS_BASE}/bill/{congress_num}/{bill_type}/{bill_number}/summaries"
    params = {"api_key": api_key, "format": "json"}

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:
        raise CongressClientError(f"congress.gov request failed: {exc}") from exc

    try:
        data = resp.json()
    except Exception as exc:
        raise CongressClientError(f"Failed to parse congress.gov response: {exc}") from exc

    summaries = data.get("summaries", [])
    if not summaries:
        return ""
    # Return the most recent summary text
    latest = max(summaries, key=lambda s: s.get("updateDate", ""))
    return latest.get("text", "")


def get_ndaa_context_demo(tech_area: str, fiscal_year: int) -> NdaaContext:
    """Return seeded NDAA context for demo mode."""
    if tech_area not in DEMO_NDAA_CONTEXT:
        raise CongressClientError(f"No demo NDAA context for tech area: {tech_area!r}")
    area_data = DEMO_NDAA_CONTEXT[tech_area]
    if fiscal_year not in area_data:
        raise CongressClientError(
            f"No demo NDAA context for {tech_area!r} FY{fiscal_year}"
        )

    raw = area_data[fiscal_year]
    congress_num = FY_TO_CONGRESS.get(fiscal_year, 0)

    return NdaaContext(
        tech_area=tech_area,
        fiscal_year=fiscal_year,
        congress_num=congress_num,
        ndaa_title=raw["ndaa_title"],
        key_provisions=raw["key_provisions"],
        authorized_amount_note=raw["authorized_amount_note"],
        data_source=DATA_SOURCE_DEMO,
    )


def get_ndaa_context_live(tech_area: str, fiscal_year: int, timeout: int = 30) -> NdaaContext:
    """Fetch live NDAA context from congress.gov and build NdaaContext.

    Falls back to demo data if API key is missing or fetch fails.
    """
    if not has_api_key():
        return get_ndaa_context_demo(tech_area, fiscal_year)

    congress_num = FY_TO_CONGRESS.get(fiscal_year)
    if congress_num is None:
        return get_ndaa_context_demo(tech_area, fiscal_year)

    bill_info = NDAA_BILL_NUMBERS.get(fiscal_year)
    if bill_info is None:
        return get_ndaa_context_demo(tech_area, fiscal_year)

    bill_type, bill_number = bill_info

    try:
        summary_text = fetch_ndaa_summary(congress_num, bill_type, bill_number, timeout)
    except CongressClientError:
        # Graceful fallback to demo data
        return get_ndaa_context_demo(tech_area, fiscal_year)

    if not summary_text:
        return get_ndaa_context_demo(tech_area, fiscal_year)

    # Build a lightweight context from the summary
    raw_demo = DEMO_NDAA_CONTEXT.get(tech_area, {}).get(fiscal_year, {})
    return NdaaContext(
        tech_area=tech_area,
        fiscal_year=fiscal_year,
        congress_num=congress_num,
        ndaa_title=raw_demo.get("ndaa_title", f"NDAA FY{fiscal_year}"),
        key_provisions=[f"[from congress.gov summary] {summary_text[:500]}"],
        authorized_amount_note=raw_demo.get("authorized_amount_note", ""),
        data_source=DATA_SOURCE_LIVE,
    )


def get_ndaa_contexts(
    tech_area: str,
    fiscal_years: list[int],
    demo_mode: bool = True,
    timeout: int = 30,
) -> list[NdaaContext]:
    """Get NDAA context for each fiscal year; falls back to demo gracefully."""
    contexts: list[NdaaContext] = []
    for fy in fiscal_years:
        if demo_mode:
            try:
                ctx = get_ndaa_context_demo(tech_area, fy)
            except CongressClientError:
                continue
        else:
            ctx = get_ndaa_context_live(tech_area, fy, timeout)
        contexts.append(ctx)
    return contexts
