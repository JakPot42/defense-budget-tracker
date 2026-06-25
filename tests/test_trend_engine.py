"""Tests for trend_engine.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import math
from models import ProgramFunding
from trend_engine import compute_yoy, compute_cagr, compute_trend, compare_areas, rdte_share_trend
from config import (
    DATA_SOURCE_DEMO,
    TREND_STRONG_GROWTH, TREND_GROWING, TREND_FLAT,
    TREND_CUT, TREND_STRONG_CUT, TREND_NEW_START, TREND_UNKNOWN,
)


def _fund(tech_area, fy, total, rdte=None, proc=None, om=None):
    return ProgramFunding(
        tech_area=tech_area,
        fiscal_year=fy,
        rdte_billions=rdte,
        procurement_billions=proc,
        om_billions=om,
        total_billions=total,
        data_source=DATA_SOURCE_DEMO,
    )


# ---------------------------------------------------------------------------
# compute_cagr
# ---------------------------------------------------------------------------

class TestComputeCagr:
    def test_zero_periods_returns_zero(self):
        assert compute_cagr(1.0, 2.0, 0) == 0.0

    def test_zero_start_returns_zero(self):
        assert compute_cagr(0.0, 2.0, 4) == 0.0

    def test_negative_start_returns_zero(self):
        assert compute_cagr(-1.0, 2.0, 4) == 0.0

    def test_strong_growth_aiml(self):
        # (4.4 / 1.7)^(1/4) - 1 ≈ 0.269 → 26.9%
        cagr = compute_cagr(1.7, 4.4, 4)
        assert abs(cagr - 26.9) < 0.5

    def test_strong_growth_hypersonics(self):
        # (6.9 / 2.2)^(1/4) - 1 ≈ 0.330 → 33%
        cagr = compute_cagr(2.2, 6.9, 4)
        assert abs(cagr - 33.0) < 1.0

    def test_growing_space(self):
        # (28.5 / 19.7)^(1/4) - 1 ≈ 0.097 → ~9.7%
        cagr = compute_cagr(19.7, 28.5, 4)
        assert abs(cagr - 9.7) < 0.5

    def test_growing_cyber(self):
        # (17.7 / 13.3)^(1/4) - 1 ≈ 0.074 → ~7.4%
        cagr = compute_cagr(13.3, 17.7, 4)
        assert abs(cagr - 7.4) < 0.5

    def test_flat_zero_growth(self):
        cagr = compute_cagr(5.0, 5.0, 4)
        assert cagr == 0.0

    def test_cut_scenario(self):
        # 5.0 -> 3.0 over 4 years
        cagr = compute_cagr(5.0, 3.0, 4)
        assert cagr < 0

    def test_single_period(self):
        # 1.7 -> 2.2 is +29.4%
        cagr = compute_cagr(1.7, 2.2, 1)
        assert abs(cagr - 29.4) < 0.5

    def test_one_hundred_pct_growth_one_period(self):
        cagr = compute_cagr(1.0, 2.0, 1)
        assert abs(cagr - 100.0) < 0.01


# ---------------------------------------------------------------------------
# compute_yoy
# ---------------------------------------------------------------------------

class TestComputeYoy:
    def test_growing_trend(self):
        f1 = _fund("AI/ML", 2022, 1.7)
        f2 = _fund("AI/ML", 2023, 2.2)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend in (TREND_GROWING, TREND_STRONG_GROWTH)
        assert yoy.delta_billions == pytest.approx(0.5, abs=0.01)
        assert yoy.pct_change == pytest.approx(29.4, abs=0.5)

    def test_strong_growth(self):
        f1 = _fund("X", 2022, 1.0)
        f2 = _fund("X", 2023, 2.5)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_STRONG_GROWTH

    def test_flat(self):
        f1 = _fund("X", 2022, 5.0)
        f2 = _fund("X", 2023, 5.1)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_FLAT

    def test_cut(self):
        f1 = _fund("X", 2022, 5.0)
        f2 = _fund("X", 2023, 4.5)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_CUT

    def test_strong_cut(self):
        f1 = _fund("X", 2022, 5.0)
        f2 = _fund("X", 2023, 3.5)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_STRONG_CUT

    def test_new_start(self):
        f1 = _fund("X", 2022, 0.0)
        f2 = _fund("X", 2023, 1.0)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_NEW_START
        assert yoy.pct_change is None

    def test_unknown_when_both_zero(self):
        f1 = _fund("X", 2022, 0.0)
        f2 = _fund("X", 2023, 0.0)
        yoy = compute_yoy(f1, f2)
        assert yoy.trend == TREND_UNKNOWN

    def test_years_stored(self):
        f1 = _fund("X", 2023, 2.0)
        f2 = _fund("X", 2024, 2.5)
        yoy = compute_yoy(f1, f2)
        assert yoy.from_year == 2023
        assert yoy.to_year == 2024

    def test_negative_delta(self):
        f1 = _fund("X", 2023, 3.0)
        f2 = _fund("X", 2024, 2.0)
        yoy = compute_yoy(f1, f2)
        assert yoy.delta_billions < 0

    def test_from_and_to_totals_stored(self):
        f1 = _fund("X", 2022, 1.5)
        f2 = _fund("X", 2023, 2.0)
        yoy = compute_yoy(f1, f2)
        assert yoy.from_total == 1.5
        assert yoy.to_total == 2.0


# ---------------------------------------------------------------------------
# compute_trend (full pipeline)
# ---------------------------------------------------------------------------

class TestComputeTrendAiMl:
    @pytest.fixture
    def ai_trend(self):
        from budget_db import get_demo_funding
        funding = get_demo_funding("AI/ML")
        return compute_trend("AI/ML", funding, DATA_SOURCE_DEMO)

    def test_overall_trend_strong_growth(self, ai_trend):
        assert ai_trend.overall_trend == TREND_STRONG_GROWTH

    def test_cagr_above_20(self, ai_trend):
        assert ai_trend.cagr > 20.0

    def test_cagr_close_to_expected(self, ai_trend):
        # ~26.9% CAGR from 1.7 to 4.4 over 4 years
        assert abs(ai_trend.cagr - 26.9) < 1.0

    def test_five_yoy_entries(self, ai_trend):
        # 5 years → 4 YoY entries
        assert len(ai_trend.yoy_changes) == 4

    def test_all_yoy_growing_or_strong_growth(self, ai_trend):
        for yoy in ai_trend.yoy_changes:
            assert yoy.trend in (TREND_GROWING, TREND_STRONG_GROWTH)

    def test_peak_year_is_2026(self, ai_trend):
        assert ai_trend.peak_year == 2026

    def test_trough_year_is_2022(self, ai_trend):
        assert ai_trend.trough_year == 2022

    def test_fiscal_years_list(self, ai_trend):
        assert ai_trend.fiscal_years == [2022, 2023, 2024, 2025, 2026]

    def test_tech_area_stored(self, ai_trend):
        assert ai_trend.tech_area == "AI/ML"


class TestComputeTrendHypersonics:
    @pytest.fixture
    def hyp_trend(self):
        from budget_db import get_demo_funding
        funding = get_demo_funding("Hypersonics")
        return compute_trend("Hypersonics", funding, DATA_SOURCE_DEMO)

    def test_strong_growth(self, hyp_trend):
        assert hyp_trend.overall_trend == TREND_STRONG_GROWTH

    def test_cagr_above_20(self, hyp_trend):
        assert hyp_trend.cagr > 20.0

    def test_cagr_around_33(self, hyp_trend):
        assert abs(hyp_trend.cagr - 33.0) < 2.0

    def test_fy2022_to_fy2023_strong_growth(self, hyp_trend):
        # 2.2 -> 3.2 = +45%
        yoy_first = hyp_trend.yoy_changes[0]
        assert yoy_first.trend == TREND_STRONG_GROWTH

    def test_peak_year_2026(self, hyp_trend):
        assert hyp_trend.peak_year == 2026

    def test_peak_total_close_to_69(self, hyp_trend):
        assert abs(hyp_trend.peak_total - 6.9) < 0.1


class TestComputeTrendSpace:
    @pytest.fixture
    def space_trend(self):
        from budget_db import get_demo_funding
        funding = get_demo_funding("Space")
        return compute_trend("Space", funding, DATA_SOURCE_DEMO)

    def test_growing_trend(self, space_trend):
        assert space_trend.overall_trend == TREND_GROWING

    def test_cagr_between_5_and_20(self, space_trend):
        assert 5.0 < space_trend.cagr < 20.0

    def test_cagr_around_97(self, space_trend):
        assert abs(space_trend.cagr - 9.7) < 1.0

    def test_largest_portfolio(self, space_trend):
        # Space is the largest total by a wide margin
        assert space_trend.peak_total > 25.0

    def test_all_yoy_growing(self, space_trend):
        for yoy in space_trend.yoy_changes:
            assert yoy.trend in (TREND_GROWING, TREND_STRONG_GROWTH, TREND_FLAT)


class TestComputeTrendCyber:
    @pytest.fixture
    def cyber_trend(self):
        from budget_db import get_demo_funding
        funding = get_demo_funding("Cyber")
        return compute_trend("Cyber", funding, DATA_SOURCE_DEMO)

    def test_growing_trend(self, cyber_trend):
        assert cyber_trend.overall_trend == TREND_GROWING

    def test_cagr_between_5_and_20(self, cyber_trend):
        assert 5.0 < cyber_trend.cagr < 20.0

    def test_slowest_cagr_of_four(self, cyber_trend):
        from budget_db import get_demo_funding
        ai_t = compute_trend("AI/ML", get_demo_funding("AI/ML"), DATA_SOURCE_DEMO)
        hyp_t = compute_trend("Hypersonics", get_demo_funding("Hypersonics"), DATA_SOURCE_DEMO)
        assert cyber_trend.cagr < ai_t.cagr
        assert cyber_trend.cagr < hyp_t.cagr


class TestComputeTrendEdgeCases:
    def test_single_year_raises(self):
        funding = {2024: _fund("X", 2024, 1.0)}
        trend = compute_trend("X", funding, DATA_SOURCE_DEMO)
        assert trend.yoy_changes == []

    def test_empty_funding_raises(self):
        with pytest.raises(ValueError):
            compute_trend("X", {}, DATA_SOURCE_DEMO)

    def test_two_years_single_yoy(self):
        funding = {
            2022: _fund("X", 2022, 1.0),
            2023: _fund("X", 2023, 1.5),
        }
        trend = compute_trend("X", funding, DATA_SOURCE_DEMO)
        assert len(trend.yoy_changes) == 1


# ---------------------------------------------------------------------------
# compare_areas
# ---------------------------------------------------------------------------

class TestCompareAreas:
    @pytest.fixture
    def all_trends(self):
        from budget_db import get_demo_funding
        trends = []
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            funding = get_demo_funding(area)
            trends.append(compute_trend(area, funding, DATA_SOURCE_DEMO))
        return trends

    def test_returns_four_entries(self, all_trends):
        result = compare_areas(all_trends)
        assert len(result) == 4

    def test_sorted_by_cagr_descending(self, all_trends):
        result = compare_areas(all_trends)
        cagrs = [r[1] for r in result]
        assert cagrs == sorted(cagrs, reverse=True)

    def test_hypersonics_highest_cagr(self, all_trends):
        result = compare_areas(all_trends)
        assert result[0][0] == "Hypersonics"

    def test_cyber_lower_than_aiml(self, all_trends):
        result = compare_areas(all_trends)
        areas_ordered = [r[0] for r in result]
        ai_idx = areas_ordered.index("AI/ML")
        cyber_idx = areas_ordered.index("Cyber")
        assert ai_idx < cyber_idx  # AI/ML before Cyber


# ---------------------------------------------------------------------------
# rdte_share_trend
# ---------------------------------------------------------------------------

class TestRdteShareTrend:
    def test_aiml_rdte_declining_share(self):
        from budget_db import get_demo_funding
        funding = get_demo_funding("AI/ML")
        trend = compute_trend("AI/ML", funding, DATA_SOURCE_DEMO)
        result = rdte_share_trend(trend)
        # RDT&E share goes from 71% to 55% — declining
        assert "DECLINING" in result.upper() or "maturing" in result.lower()

    def test_live_mode_no_breakdown(self):
        funding = {
            2022: _fund("X", 2022, 1.0),
            2024: _fund("X", 2024, 1.5),
        }
        trend = compute_trend("X", funding, DATA_SOURCE_DEMO)
        result = rdte_share_trend(trend)
        assert "not available" in result.lower() or "breakdown" in result.lower()

    def test_increasing_rdte_share(self):
        # RDT&E share growing: 50% -> 70%
        from models import ProgramFunding
        funding = {
            2022: ProgramFunding("X", 2022, 0.5, 0.4, 0.1, 1.0, DATA_SOURCE_DEMO),
            2026: ProgramFunding("X", 2026, 2.8, 1.2, 0.0, 4.0, DATA_SOURCE_DEMO),
        }
        trend = compute_trend("X", funding, DATA_SOURCE_DEMO)
        result = rdte_share_trend(trend)
        assert "INCREASING" in result.upper()
