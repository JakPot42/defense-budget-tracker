"""Tests for congress_client.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from congress_client import (
    get_ndaa_context_demo, get_ndaa_contexts, has_api_key, CongressClientError,
)
from config import TRACKED_FISCAL_YEARS, FY_TO_CONGRESS, DATA_SOURCE_DEMO
from models import NdaaContext


class TestGetNdaaContextDemo:
    def test_returns_ndaa_context(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert isinstance(ctx, NdaaContext)

    def test_tech_area_stored(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert ctx.tech_area == "AI/ML"

    def test_fiscal_year_stored(self):
        ctx = get_ndaa_context_demo("Hypersonics", 2023)
        assert ctx.fiscal_year == 2023

    def test_congress_num_correct(self):
        ctx = get_ndaa_context_demo("Space", 2024)
        assert ctx.congress_num == FY_TO_CONGRESS[2024]  # 118

    def test_congress_num_2022(self):
        ctx = get_ndaa_context_demo("Cyber", 2022)
        assert ctx.congress_num == 117

    def test_congress_num_2026(self):
        ctx = get_ndaa_context_demo("AI/ML", 2026)
        assert ctx.congress_num == 119

    def test_ndaa_title_nonempty(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert len(ctx.ndaa_title) > 10

    def test_key_provisions_list(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert isinstance(ctx.key_provisions, list)
        assert len(ctx.key_provisions) >= 1

    def test_authorized_amount_note_nonempty(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert len(ctx.authorized_amount_note) > 0

    def test_data_source_demo(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        assert ctx.data_source == DATA_SOURCE_DEMO

    def test_all_tech_areas_all_years(self):
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            for fy in TRACKED_FISCAL_YEARS:
                ctx = get_ndaa_context_demo(area, fy)
                assert isinstance(ctx, NdaaContext)

    def test_invalid_tech_area_raises(self):
        with pytest.raises(CongressClientError):
            get_ndaa_context_demo("Quantum", 2024)

    def test_invalid_fy_raises(self):
        with pytest.raises(CongressClientError):
            get_ndaa_context_demo("AI/ML", 2010)

    def test_aiml_2024_mentions_cdao(self):
        ctx = get_ndaa_context_demo("AI/ML", 2024)
        combined = " ".join(ctx.key_provisions)
        assert "CDAO" in combined or "AI" in combined

    def test_hypersonics_2024_mentions_cancellation_or_program(self):
        ctx = get_ndaa_context_demo("Hypersonics", 2024)
        combined = " ".join(ctx.key_provisions).upper()
        assert any(kw in combined for kw in ["ARRW", "CPS", "HACM", "LRHW", "HYPERSONIC"])


class TestGetNdaaContexts:
    def test_returns_list(self):
        contexts = get_ndaa_contexts("AI/ML", TRACKED_FISCAL_YEARS, demo_mode=True)
        assert isinstance(contexts, list)

    def test_length_matches_years(self):
        contexts = get_ndaa_contexts("AI/ML", TRACKED_FISCAL_YEARS, demo_mode=True)
        assert len(contexts) == len(TRACKED_FISCAL_YEARS)

    def test_all_ndaa_context_instances(self):
        contexts = get_ndaa_contexts("Cyber", TRACKED_FISCAL_YEARS, demo_mode=True)
        for ctx in contexts:
            assert isinstance(ctx, NdaaContext)

    def test_fiscal_years_in_order(self):
        contexts = get_ndaa_contexts("Space", TRACKED_FISCAL_YEARS, demo_mode=True)
        years = [ctx.fiscal_year for ctx in contexts]
        assert years == sorted(years)

    def test_single_year(self):
        contexts = get_ndaa_contexts("AI/ML", [2024], demo_mode=True)
        assert len(contexts) == 1
        assert contexts[0].fiscal_year == 2024

    def test_partial_years(self):
        contexts = get_ndaa_contexts("Hypersonics", [2023, 2025], demo_mode=True)
        years = [ctx.fiscal_year for ctx in contexts]
        assert 2023 in years
        assert 2025 in years


class TestHasApiKey:
    def test_no_key_returns_false(self):
        os.environ.pop("CONGRESS_API_KEY", None)
        assert has_api_key() is False

    def test_key_set_returns_true(self):
        os.environ["CONGRESS_API_KEY"] = "test_key_123"
        assert has_api_key() is True
        os.environ.pop("CONGRESS_API_KEY", None)
