"""Data models for P46 Defense Budget & Appropriations Tracker."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProgramFunding:
    """Funding snapshot for one technology area in one fiscal year."""
    tech_area: str
    fiscal_year: int
    rdte_billions: Optional[float]       # None when breakdown not available (live mode)
    procurement_billions: Optional[float]
    om_billions: Optional[float]
    total_billions: float
    data_source: str                     # "DEMO" or "LIVE"
    notes: str = ""

    @property
    def has_breakdown(self) -> bool:
        return (
            self.rdte_billions is not None
            and self.procurement_billions is not None
            and self.om_billions is not None
        )

    @property
    def rdte_pct(self) -> Optional[float]:
        if not self.has_breakdown or self.total_billions == 0:
            return None
        return round(self.rdte_billions / self.total_billions * 100, 1)  # type: ignore[operator]

    @property
    def procurement_pct(self) -> Optional[float]:
        if not self.has_breakdown or self.total_billions == 0:
            return None
        return round(self.procurement_billions / self.total_billions * 100, 1)  # type: ignore[operator]

    @property
    def om_pct(self) -> Optional[float]:
        if not self.has_breakdown or self.total_billions == 0:
            return None
        return round(self.om_billions / self.total_billions * 100, 1)  # type: ignore[operator]


@dataclass
class YearOverYear:
    """Year-over-year funding change between two fiscal years."""
    from_year: int
    to_year: int
    from_total: float
    to_total: float
    delta_billions: float
    pct_change: Optional[float]          # None if from_total == 0
    trend: str                           # STRONG_GROWTH | GROWING | FLAT | CUT | STRONG_CUT | NEW_START

    @property
    def is_increase(self) -> bool:
        return self.delta_billions > 0

    @property
    def pct_display(self) -> str:
        if self.pct_change is None:
            return "N/A"
        sign = "+" if self.pct_change >= 0 else ""
        return f"{sign}{self.pct_change:.1f}%"

    @property
    def delta_display(self) -> str:
        sign = "+" if self.delta_billions >= 0 else ""
        return f"{sign}${self.delta_billions:.1f}B"


@dataclass
class FundingTrend:
    """Multi-year funding trend for one technology area."""
    tech_area: str
    fiscal_years: list[int]
    funding_by_year: dict[int, ProgramFunding]
    yoy_changes: list[YearOverYear]
    overall_trend: str                   # STRONG_GROWTH | GROWING | FLAT | CUT | etc.
    cagr: float                          # compound annual growth rate (%)
    peak_year: int
    peak_total: float
    trough_year: int
    trough_total: float
    data_source: str

    @property
    def cagr_display(self) -> str:
        sign = "+" if self.cagr >= 0 else ""
        return f"{sign}{self.cagr:.1f}% CAGR"

    @property
    def total_range(self) -> tuple[float, float]:
        totals = [self.funding_by_year[y].total_billions for y in self.fiscal_years]
        return min(totals), max(totals)

    @property
    def latest_year(self) -> int:
        return max(self.fiscal_years)

    @property
    def earliest_year(self) -> int:
        return min(self.fiscal_years)


@dataclass
class NdaaContext:
    """NDAA / appropriations context for a technology area in a fiscal year."""
    tech_area: str
    fiscal_year: int
    congress_num: int
    ndaa_title: str
    key_provisions: list[str]
    authorized_amount_note: str          # high-level authorization note (not exact line items)
    data_source: str                     # "DEMO" or "LIVE"


@dataclass
class BudgetReport:
    """Complete budget analysis report for one technology area."""
    tech_area: str
    tech_area_label: str
    prepared_date: str
    fiscal_years: list[int]
    trend: FundingTrend
    ndaa_contexts: list[NdaaContext]
    plain_english: str                   # Claude-generated or seeded narrative
    data_source: str

    @property
    def latest_funding(self) -> Optional[ProgramFunding]:
        if not self.fiscal_years:
            return None
        return self.trend.funding_by_year.get(max(self.fiscal_years))

    @property
    def first_funding(self) -> Optional[ProgramFunding]:
        if not self.fiscal_years:
            return None
        return self.trend.funding_by_year.get(min(self.fiscal_years))
