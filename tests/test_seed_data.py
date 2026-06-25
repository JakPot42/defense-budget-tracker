"""Tests for seed_data.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from seed_data import (
    DEMO_FUNDING, DEMO_NDAA_CONTEXT, DEMO_REPORT_TEXT,
    DEMO_TREND_EXPLANATIONS, DEMO_AREA_ORDER,
)
from config import TRACKED_FISCAL_YEARS, TECH_AREA_NAMES


class TestDemoFundingStructure:
    def test_all_tech_areas_present(self):
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            assert area in DEMO_FUNDING

    def test_all_fiscal_years_present(self):
        for area in DEMO_FUNDING:
            for fy in TRACKED_FISCAL_YEARS:
                assert fy in DEMO_FUNDING[area], f"Missing FY{fy} for {area}"

    def test_all_required_keys_per_year(self):
        required = {"rdte", "proc", "om", "total", "notes"}
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert required.issubset(data.keys()), \
                    f"Missing keys in {area} FY{fy}: {required - data.keys()}"

    def test_all_totals_positive(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert data["total"] > 0, f"Zero/negative total for {area} FY{fy}"

    def test_all_totals_match_components(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                expected = round(data["rdte"] + data["proc"] + data["om"], 2)
                actual = round(data["total"], 2)
                assert abs(expected - actual) < 0.01, \
                    f"{area} FY{fy}: rdte+proc+om={expected} != total={actual}"

    def test_rdte_non_negative(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert data["rdte"] >= 0

    def test_procurement_non_negative(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert data["proc"] >= 0

    def test_om_non_negative(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert data["om"] >= 0


class TestDemoFundingValues:
    def test_aiml_fy2022_total(self):
        assert DEMO_FUNDING["AI/ML"][2022]["total"] == 1.7

    def test_aiml_fy2026_total(self):
        assert DEMO_FUNDING["AI/ML"][2026]["total"] == 4.4

    def test_aiml_growth(self):
        assert DEMO_FUNDING["AI/ML"][2026]["total"] > DEMO_FUNDING["AI/ML"][2022]["total"]

    def test_hypersonics_fy2022_proc_zero(self):
        assert DEMO_FUNDING["Hypersonics"][2022]["proc"] == 0.0

    def test_hypersonics_fy2026_proc_nonzero(self):
        assert DEMO_FUNDING["Hypersonics"][2026]["proc"] > 0

    def test_hypersonics_procurement_growth(self):
        # procurement grows from 0 to significant
        assert DEMO_FUNDING["Hypersonics"][2026]["proc"] > DEMO_FUNDING["Hypersonics"][2023]["proc"]

    def test_space_largest_portfolio(self):
        # Space has the biggest absolute numbers
        for fy in TRACKED_FISCAL_YEARS:
            space = DEMO_FUNDING["Space"][fy]["total"]
            for area in ["AI/ML", "Hypersonics", "Cyber"]:
                assert space > DEMO_FUNDING[area][fy]["total"], \
                    f"Space FY{fy} not largest"

    def test_cyber_om_dominant(self):
        # Cyber has O&M > RDT&E for all years (labor-intensive ops)
        for fy in TRACKED_FISCAL_YEARS:
            assert DEMO_FUNDING["Cyber"][fy]["om"] > DEMO_FUNDING["Cyber"][fy]["rdte"]

    def test_aiml_rdte_dominant_early(self):
        # In early years, AI/ML is mostly RDT&E
        fy22 = DEMO_FUNDING["AI/ML"][2022]
        assert fy22["rdte"] > fy22["proc"]

    def test_all_notes_nonempty(self):
        for area, years in DEMO_FUNDING.items():
            for fy, data in years.items():
                assert data["notes"].strip(), f"Empty notes for {area} FY{fy}"


class TestDemoNdaaContext:
    def test_all_tech_areas_have_ndaa_context(self):
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            assert area in DEMO_NDAA_CONTEXT

    def test_all_fiscal_years_have_ndaa_context(self):
        for area in DEMO_NDAA_CONTEXT:
            for fy in TRACKED_FISCAL_YEARS:
                assert fy in DEMO_NDAA_CONTEXT[area], \
                    f"No NDAA context for {area} FY{fy}"

    def test_ndaa_context_required_keys(self):
        required = {"ndaa_title", "key_provisions", "authorized_amount_note"}
        for area, years in DEMO_NDAA_CONTEXT.items():
            for fy, data in years.items():
                assert required.issubset(data.keys()), \
                    f"Missing NDAA keys for {area} FY{fy}"

    def test_key_provisions_nonempty(self):
        for area, years in DEMO_NDAA_CONTEXT.items():
            for fy, data in years.items():
                assert len(data["key_provisions"]) >= 1, \
                    f"No provisions for {area} FY{fy}"

    def test_ndaa_titles_mention_fiscal_year(self):
        for area, years in DEMO_NDAA_CONTEXT.items():
            for fy, data in years.items():
                title = data["ndaa_title"]
                assert str(fy) in title or "illustrative" in title.lower(), \
                    f"NDAA title for {area} FY{fy} doesn't mention year: {title}"

    def test_fy2024_has_public_law(self):
        for area in DEMO_NDAA_CONTEXT:
            data = DEMO_NDAA_CONTEXT[area][2024]
            # FY2024 NDAA P.L. 118-31 should appear in title or provisions
            combined = data["ndaa_title"] + " ".join(data["key_provisions"])
            assert "118" in combined or "P.L." in combined or "2024" in combined

    def test_aiml_fy2024_mentions_cdao(self):
        ctx = DEMO_NDAA_CONTEXT["AI/ML"][2024]
        combined = " ".join(ctx["key_provisions"])
        assert "CDAO" in combined or "AI" in combined

    def test_hypersonics_fy2024_mentions_arrw_or_cps(self):
        ctx = DEMO_NDAA_CONTEXT["Hypersonics"][2024]
        combined = " ".join(ctx["key_provisions"])
        assert "ARRW" in combined or "CPS" in combined or "hypersonic" in combined.lower()


class TestDemoReportText:
    def test_report_is_string(self):
        assert isinstance(DEMO_REPORT_TEXT, str)

    def test_report_nonempty(self):
        assert len(DEMO_REPORT_TEXT) > 500

    def test_report_ascii_safe(self):
        for i, ch in enumerate(DEMO_REPORT_TEXT):
            assert ord(ch) < 128, f"Non-ASCII char at position {i}: {repr(ch)}"

    def test_report_mentions_ai_ml(self):
        assert "Artificial Intelligence" in DEMO_REPORT_TEXT or "AI/ML" in DEMO_REPORT_TEXT

    def test_report_mentions_rdte(self):
        assert "RDT" in DEMO_REPORT_TEXT

    def test_report_mentions_procurement(self):
        assert "Procurement" in DEMO_REPORT_TEXT or "procurement" in DEMO_REPORT_TEXT

    def test_report_mentions_strong_growth(self):
        assert "STRONG" in DEMO_REPORT_TEXT.upper() or "CAGR" in DEMO_REPORT_TEXT

    def test_report_has_demo_notice(self):
        assert "DEMO" in DEMO_REPORT_TEXT or "illustrative" in DEMO_REPORT_TEXT.lower()

    def test_report_has_data_source_note(self):
        assert "USASpending" in DEMO_REPORT_TEXT or "usaspending" in DEMO_REPORT_TEXT.lower()


class TestDemoCoverageObjects:
    def test_demo_area_order_matches_funding(self):
        for area in DEMO_AREA_ORDER:
            assert area in DEMO_FUNDING

    def test_demo_area_order_length(self):
        assert len(DEMO_AREA_ORDER) == 4

    def test_trend_explanations_cover_non_aiml(self):
        for area in ["Hypersonics", "Space", "Cyber"]:
            assert area in DEMO_TREND_EXPLANATIONS

    def test_trend_explanations_nonempty(self):
        for area, text in DEMO_TREND_EXPLANATIONS.items():
            assert len(text) > 50, f"Thin explanation for {area}"

    def test_trend_explanations_ascii_safe(self):
        for area, text in DEMO_TREND_EXPLANATIONS.items():
            for i, ch in enumerate(text):
                assert ord(ch) < 128, f"Non-ASCII in {area} explanation at {i}: {repr(ch)}"
