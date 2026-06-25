"""Demo data access layer for P46 Defense Budget & Appropriations Tracker.

Wraps seed_data.py into ProgramFunding and NdaaContext model objects.
Provides both demo and live data retrieval with a consistent interface.
"""
from __future__ import annotations

from config import DATA_SOURCE_DEMO, TECH_AREAS, TRACKED_FISCAL_YEARS
from models import ProgramFunding
from seed_data import DEMO_FUNDING, DEMO_NDAA_CONTEXT, DEMO_AREA_ORDER

# Cache to avoid re-building on repeated calls
_FUNDING_CACHE: dict[str, dict[int, ProgramFunding]] = {}


def _build_program_funding(tech_area: str, fiscal_year: int, raw: dict) -> ProgramFunding:
    return ProgramFunding(
        tech_area=tech_area,
        fiscal_year=fiscal_year,
        rdte_billions=raw["rdte"],
        procurement_billions=raw["proc"],
        om_billions=raw["om"],
        total_billions=raw["total"],
        data_source=DATA_SOURCE_DEMO,
        notes=raw.get("notes", ""),
    )


def get_demo_funding(
    tech_area: str,
    fiscal_years: list[int] | None = None,
) -> dict[int, ProgramFunding]:
    """Return demo ProgramFunding for one tech area across requested fiscal years."""
    if tech_area not in DEMO_FUNDING:
        raise KeyError(f"Unknown tech area: {tech_area!r}. Valid: {list(DEMO_FUNDING)}")

    target_years = fiscal_years or TRACKED_FISCAL_YEARS
    cache_key = f"{tech_area}:{','.join(map(str, sorted(target_years)))}"

    if cache_key not in _FUNDING_CACHE:
        raw_area = DEMO_FUNDING[tech_area]
        result: dict[int, ProgramFunding] = {}
        for fy in target_years:
            if fy in raw_area:
                result[fy] = _build_program_funding(tech_area, fy, raw_area[fy])
        _FUNDING_CACHE[cache_key] = result

    return _FUNDING_CACHE[cache_key]


def all_demo_tech_areas() -> list[str]:
    """Return tech area names in canonical display order."""
    return list(DEMO_AREA_ORDER)


def all_tracked_years() -> list[int]:
    return list(TRACKED_FISCAL_YEARS)


def demo_tech_area_label(tech_area: str) -> str:
    if tech_area not in TECH_AREAS:
        return tech_area
    return TECH_AREAS[tech_area]["label"]
