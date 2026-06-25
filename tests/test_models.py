"""Tests for models.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models import ProgramFunding, YearOverYear, FundingTrend, NdaaContext, BudgetReport
from config import DATA_SOURCE_DEMO, DATA_SOURCE_LIVE


class TestProgramFunding:
    def _make(self, **kwargs):
        defaults = dict(
            tech_area="AI/ML",
            fiscal_year=2024,
            rdte_billions=1.8,
            procurement_billions=0.6,
            om_billions=0.4,
            total_billions=2.8,
            data_source=DATA_SOURCE_DEMO,
        )
        defaults.update(kwargs)
        return ProgramFunding(**defaults)

    def test_construction(self):
        f = self._make()
        assert f.tech_area == "AI/ML"
        assert f.fiscal_year == 2024

    def test_has_breakdown_true(self):
        f = self._make()
        assert f.has_breakdown is True

    def test_has_breakdown_false_when_none(self):
        f = self._make(rdte_billions=None, procurement_billions=None, om_billions=None)
        assert f.has_breakdown is False

    def test_rdte_pct_correct(self):
        f = self._make(rdte_billions=1.8, procurement_billions=0.6, om_billions=0.4, total_billions=2.8)
        # 1.8 / 2.8 = 64.3%
        assert abs(f.rdte_pct - 64.3) < 0.1

    def test_procurement_pct_correct(self):
        f = self._make(rdte_billions=1.8, procurement_billions=0.6, om_billions=0.4, total_billions=2.8)
        # 0.6 / 2.8 = 21.4%
        assert abs(f.procurement_pct - 21.4) < 0.1

    def test_om_pct_correct(self):
        f = self._make(rdte_billions=1.8, procurement_billions=0.6, om_billions=0.4, total_billions=2.8)
        # 0.4 / 2.8 = 14.3%
        assert abs(f.om_pct - 14.3) < 0.1

    def test_rdte_pct_none_when_no_breakdown(self):
        f = self._make(rdte_billions=None, procurement_billions=None, om_billions=None)
        assert f.rdte_pct is None

    def test_rdte_pct_none_when_zero_total(self):
        f = self._make(rdte_billions=0.0, procurement_billions=0.0, om_billions=0.0, total_billions=0.0)
        assert f.rdte_pct is None

    def test_default_notes_empty(self):
        f = self._make()
        assert f.notes == ""

    def test_notes_stored(self):
        f = self._make(notes="test note")
        assert f.notes == "test note"


class TestYearOverYear:
    def _make(self, **kwargs):
        defaults = dict(
            from_year=2023, to_year=2024,
            from_total=2.2, to_total=2.8,
            delta_billions=0.6,
            pct_change=27.3,
            trend="GROWING",
        )
        defaults.update(kwargs)
        return YearOverYear(**defaults)

    def test_construction(self):
        y = self._make()
        assert y.from_year == 2023
        assert y.to_year == 2024

    def test_is_increase_true(self):
        y = self._make(delta_billions=0.6)
        assert y.is_increase is True

    def test_is_increase_false(self):
        y = self._make(delta_billions=-0.3)
        assert y.is_increase is False

    def test_pct_display_positive(self):
        y = self._make(pct_change=27.3)
        assert "+" in y.pct_display
        assert "27" in y.pct_display

    def test_pct_display_negative(self):
        y = self._make(pct_change=-10.5)
        assert "-10.5" in y.pct_display

    def test_pct_display_none(self):
        y = self._make(pct_change=None)
        assert y.pct_display == "N/A"

    def test_delta_display_positive(self):
        y = self._make(delta_billions=0.6)
        assert "+" in y.delta_display

    def test_delta_display_negative(self):
        y = self._make(delta_billions=-0.3)
        assert "-" in y.delta_display


class TestNdaaContext:
    def test_construction(self):
        ctx = NdaaContext(
            tech_area="AI/ML",
            fiscal_year=2024,
            congress_num=118,
            ndaa_title="NDAA FY2024",
            key_provisions=["Sec. 225: AI CoE"],
            authorized_amount_note="$2.1B estimated",
            data_source=DATA_SOURCE_DEMO,
        )
        assert ctx.tech_area == "AI/ML"
        assert ctx.fiscal_year == 2024
        assert ctx.congress_num == 118
        assert len(ctx.key_provisions) == 1


class TestFundingTrendProperties:
    def _make_trend(self):
        from models import ProgramFunding
        fy_data = {
            2022: ProgramFunding("AI/ML", 2022, 1.2, 0.3, 0.2, 1.7, DATA_SOURCE_DEMO),
            2024: ProgramFunding("AI/ML", 2024, 1.8, 0.6, 0.4, 2.8, DATA_SOURCE_DEMO),
            2026: ProgramFunding("AI/ML", 2026, 2.4, 1.2, 0.8, 4.4, DATA_SOURCE_DEMO),
        }
        return FundingTrend(
            tech_area="AI/ML",
            fiscal_years=[2022, 2024, 2026],
            funding_by_year=fy_data,
            yoy_changes=[],
            overall_trend="STRONG_GROWTH",
            cagr=26.9,
            peak_year=2026,
            peak_total=4.4,
            trough_year=2022,
            trough_total=1.7,
            data_source=DATA_SOURCE_DEMO,
        )

    def test_cagr_display_positive(self):
        t = self._make_trend()
        assert "+" in t.cagr_display
        assert "26.9" in t.cagr_display

    def test_total_range(self):
        t = self._make_trend()
        low, high = t.total_range
        assert low == 1.7
        assert high == 4.4

    def test_latest_year(self):
        t = self._make_trend()
        assert t.latest_year == 2026

    def test_earliest_year(self):
        t = self._make_trend()
        assert t.earliest_year == 2022
