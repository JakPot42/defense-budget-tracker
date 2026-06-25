"""Core trend computation for P46 Defense Budget & Appropriations Tracker."""
from __future__ import annotations

import math
from config import (
    CAGR_STRONG_GROWTH, CAGR_GROWING, CAGR_FLAT_LOW, CAGR_CUT,
    YOY_STRONG_GROWTH, YOY_GROWING, YOY_FLAT_LOW, YOY_CUT,
    TREND_STRONG_GROWTH, TREND_GROWING, TREND_FLAT,
    TREND_CUT, TREND_STRONG_CUT, TREND_NEW_START, TREND_VOLATILE, TREND_UNKNOWN,
    DATA_SOURCE_DEMO, DATA_SOURCE_LIVE,
)
from models import ProgramFunding, YearOverYear, FundingTrend


def _classify_yoy(pct: float) -> str:
    if pct >= YOY_STRONG_GROWTH:
        return TREND_STRONG_GROWTH
    if pct >= YOY_GROWING:
        return TREND_GROWING
    if pct >= YOY_FLAT_LOW:
        return TREND_FLAT
    if pct >= YOY_CUT:
        return TREND_CUT
    return TREND_STRONG_CUT


def _classify_overall(cagr: float, yoy_trends: list[str]) -> str:
    """Classify the multi-year overall trend from CAGR and per-year labels."""
    if cagr >= CAGR_STRONG_GROWTH:
        return TREND_STRONG_GROWTH
    if cagr >= CAGR_GROWING:
        return TREND_GROWING
    if cagr >= CAGR_FLAT_LOW:
        # Check for volatility: alternating growth/cuts with high spread
        cut_count = sum(1 for t in yoy_trends if t in (TREND_CUT, TREND_STRONG_CUT))
        grow_count = sum(1 for t in yoy_trends if t in (TREND_STRONG_GROWTH, TREND_GROWING))
        if cut_count > 0 and grow_count > 0:
            return TREND_VOLATILE
        return TREND_FLAT
    if cagr >= CAGR_CUT:
        return TREND_CUT
    return TREND_STRONG_CUT


def compute_yoy(from_funding: ProgramFunding, to_funding: ProgramFunding) -> YearOverYear:
    """Compute year-over-year change between two adjacent funding records."""
    from_total = from_funding.total_billions
    to_total = to_funding.total_billions
    delta = round(to_total - from_total, 2)

    if from_total == 0 and to_total > 0:
        pct = None  # new start; undefined percentage
        trend = TREND_NEW_START
    elif from_total == 0:
        pct = None
        trend = TREND_UNKNOWN
    else:
        raw_pct = (to_total - from_total) / from_total * 100
        pct = round(raw_pct, 1)
        trend = _classify_yoy(raw_pct)

    return YearOverYear(
        from_year=from_funding.fiscal_year,
        to_year=to_funding.fiscal_year,
        from_total=from_total,
        to_total=to_total,
        delta_billions=delta,
        pct_change=pct,
        trend=trend,
    )


def compute_cagr(start_value: float, end_value: float, n_periods: int) -> float:
    """Compound annual growth rate (%)."""
    if n_periods <= 0:
        return 0.0
    if start_value <= 0:
        return 0.0
    return round((math.pow(end_value / start_value, 1.0 / n_periods) - 1) * 100, 2)


def compute_trend(
    tech_area: str,
    funding_by_year: dict[int, ProgramFunding],
    data_source: str = DATA_SOURCE_DEMO,
) -> FundingTrend:
    """Derive a FundingTrend from a dict of ProgramFunding keyed by fiscal year."""
    if not funding_by_year:
        raise ValueError(f"No funding data provided for {tech_area}")

    years = sorted(funding_by_year.keys())

    # YoY chain
    yoy_changes: list[YearOverYear] = []
    for i in range(len(years) - 1):
        yoy = compute_yoy(funding_by_year[years[i]], funding_by_year[years[i + 1]])
        yoy_changes.append(yoy)

    # CAGR from first to last year
    first_total = funding_by_year[years[0]].total_billions
    last_total = funding_by_year[years[-1]].total_billions
    n_periods = len(years) - 1
    cagr = compute_cagr(first_total, last_total, n_periods)

    yoy_trend_labels = [y.trend for y in yoy_changes]
    overall = _classify_overall(cagr, yoy_trend_labels)

    # Peak and trough
    peak_year = max(years, key=lambda y: funding_by_year[y].total_billions)
    trough_year = min(years, key=lambda y: funding_by_year[y].total_billions)

    return FundingTrend(
        tech_area=tech_area,
        fiscal_years=years,
        funding_by_year=funding_by_year,
        yoy_changes=yoy_changes,
        overall_trend=overall,
        cagr=cagr,
        peak_year=peak_year,
        peak_total=funding_by_year[peak_year].total_billions,
        trough_year=trough_year,
        trough_total=funding_by_year[trough_year].total_billions,
        data_source=data_source,
    )


def compare_areas(trends: list[FundingTrend]) -> list[tuple[str, float, str]]:
    """Return list of (tech_area, cagr, overall_trend) sorted by CAGR descending."""
    return sorted(
        [(t.tech_area, t.cagr, t.overall_trend) for t in trends],
        key=lambda x: x[1],
        reverse=True,
    )


def rdte_share_trend(trend: FundingTrend) -> str:
    """Describe whether RDT&E is growing or shrinking as a portfolio share."""
    years = trend.fiscal_years
    if len(years) < 2:
        return "insufficient data"

    first = trend.funding_by_year[years[0]]
    last = trend.funding_by_year[years[-1]]

    if not first.has_breakdown or not last.has_breakdown:
        return "breakdown not available"

    first_share = first.rdte_pct or 0.0
    last_share = last.rdte_pct or 0.0
    delta = last_share - first_share

    if delta > 5:
        return f"RDT&E share INCREASING ({first_share:.0f}% -> {last_share:.0f}%): R&D phase, pre-procurement"
    if delta < -5:
        return f"RDT&E share DECLINING ({first_share:.0f}% -> {last_share:.0f}%): maturing toward procurement"
    return f"RDT&E share STABLE ({first_share:.0f}% -> {last_share:.0f}%): steady mixed portfolio"
