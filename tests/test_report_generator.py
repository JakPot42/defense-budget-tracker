"""Tests for report_generator.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models import BudgetReport
from budget_db import get_demo_funding, demo_tech_area_label
from trend_engine import compute_trend
from congress_client import get_ndaa_contexts
from report_generator import generate_report, ReportGeneratorError, _build_action_items
from seed_data import DEMO_REPORT_TEXT
from config import DATA_SOURCE_DEMO, TRACKED_FISCAL_YEARS


def _build_report(tech_area: str) -> BudgetReport:
    funding = get_demo_funding(tech_area)
    trend = compute_trend(tech_area, funding, DATA_SOURCE_DEMO)
    contexts = get_ndaa_contexts(tech_area, TRACKED_FISCAL_YEARS, demo_mode=True)
    return BudgetReport(
        tech_area=tech_area,
        tech_area_label=demo_tech_area_label(tech_area),
        prepared_date="2026-06-25",
        fiscal_years=list(TRACKED_FISCAL_YEARS),
        trend=trend,
        ndaa_contexts=contexts,
        plain_english="",
        data_source=DATA_SOURCE_DEMO,
    )


@pytest.fixture
def aiml_report():
    return _build_report("AI/ML")


@pytest.fixture
def hyp_report():
    return _build_report("Hypersonics")


@pytest.fixture
def space_report():
    return _build_report("Space")


@pytest.fixture
def cyber_report():
    return _build_report("Cyber")


class TestGenerateReportDemoMode:
    def test_aiml_returns_prebuilt_text(self, aiml_report):
        brief, items = generate_report(aiml_report, demo_mode=True)
        assert brief == DEMO_REPORT_TEXT

    def test_aiml_returns_action_items_list(self, aiml_report):
        brief, items = generate_report(aiml_report, demo_mode=True)
        assert isinstance(items, list)
        assert len(items) >= 1

    def test_hypersonics_assembles_brief(self, hyp_report):
        brief, items = generate_report(hyp_report, demo_mode=True)
        assert brief != DEMO_REPORT_TEXT
        assert isinstance(brief, str)
        assert len(brief) > 200

    def test_space_assembles_brief(self, space_report):
        brief, items = generate_report(space_report, demo_mode=True)
        assert isinstance(brief, str)
        assert len(brief) > 200

    def test_cyber_assembles_brief(self, cyber_report):
        brief, items = generate_report(cyber_report, demo_mode=True)
        assert isinstance(brief, str)
        assert len(brief) > 200

    def test_hypersonics_includes_tech_area(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        assert "Hypersonic" in brief

    def test_space_includes_tech_area(self, space_report):
        brief, _ = generate_report(space_report, demo_mode=True)
        assert "Space" in brief

    def test_cyber_includes_tech_area(self, cyber_report):
        brief, _ = generate_report(cyber_report, demo_mode=True)
        assert "Cyber" in brief

    def test_assembled_brief_has_demo_notice(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        assert "DEMO" in brief

    def test_assembled_brief_ascii_safe(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        for i, ch in enumerate(brief):
            assert ord(ch) < 128, f"Non-ASCII at position {i}: {repr(ch)}"

    def test_assembled_brief_ascii_safe_space(self, space_report):
        brief, _ = generate_report(space_report, demo_mode=True)
        for i, ch in enumerate(brief):
            assert ord(ch) < 128, f"Non-ASCII at position {i}: {repr(ch)}"

    def test_assembled_brief_ascii_safe_cyber(self, cyber_report):
        brief, _ = generate_report(cyber_report, demo_mode=True)
        for i, ch in enumerate(brief):
            assert ord(ch) < 128, f"Non-ASCII at position {i}: {repr(ch)}"

    def test_assembled_brief_mentions_cagr(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        assert "CAGR" in brief or "%" in brief

    def test_assembled_brief_has_trend_label(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        assert "STRONG_GROWTH" in brief

    def test_assembled_brief_has_ndaa_section(self, hyp_report):
        brief, _ = generate_report(hyp_report, demo_mode=True)
        assert "NDAA" in brief or "FY" in brief


class TestBuildActionItems:
    def test_returns_list(self, aiml_report):
        items = _build_action_items(aiml_report)
        assert isinstance(items, list)

    def test_nonempty_for_strong_growth(self, aiml_report):
        items = _build_action_items(aiml_report)
        assert len(items) >= 1

    def test_nonempty_for_hypersonics(self, hyp_report):
        items = _build_action_items(hyp_report)
        assert len(items) >= 1

    def test_strong_growth_mentions_cagr_or_budget(self, aiml_report):
        items = _build_action_items(aiml_report)
        combined = " ".join(items)
        assert "budget" in combined.lower() or "CAGR" in combined or "growth" in combined.lower()

    def test_procurement_surge_triggers_contractor_note(self, hyp_report):
        items = _build_action_items(hyp_report)
        combined = " ".join(items)
        # Hypersonics FY2026 has 33% procurement share → triggers contractor item
        assert "procurement" in combined.lower() or "production" in combined.lower() or "contractor" in combined.lower()


class TestLiveModeError:
    def test_live_mode_no_api_key_raises(self, aiml_report):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with pytest.raises(ReportGeneratorError):
            generate_report(aiml_report, demo_mode=False)
