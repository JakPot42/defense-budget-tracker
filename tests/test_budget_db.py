"""Tests for budget_db.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from budget_db import (
    get_demo_funding, all_demo_tech_areas, all_tracked_years, demo_tech_area_label,
)
from config import TRACKED_FISCAL_YEARS, DATA_SOURCE_DEMO
from models import ProgramFunding


class TestGetDemoFunding:
    def test_returns_dict(self):
        result = get_demo_funding("AI/ML")
        assert isinstance(result, dict)

    def test_all_fiscal_years_returned(self):
        result = get_demo_funding("AI/ML")
        for fy in TRACKED_FISCAL_YEARS:
            assert fy in result

    def test_values_are_program_funding(self):
        result = get_demo_funding("AI/ML")
        for fy, f in result.items():
            assert isinstance(f, ProgramFunding)

    def test_tech_area_stored_correctly(self):
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            result = get_demo_funding(area)
            for fy, f in result.items():
                assert f.tech_area == area

    def test_fiscal_year_stored_correctly(self):
        result = get_demo_funding("AI/ML")
        for fy, f in result.items():
            assert f.fiscal_year == fy

    def test_data_source_is_demo(self):
        result = get_demo_funding("AI/ML")
        for f in result.values():
            assert f.data_source == DATA_SOURCE_DEMO

    def test_has_breakdown_all_areas(self):
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            result = get_demo_funding(area)
            for f in result.values():
                assert f.has_breakdown

    def test_invalid_area_raises(self):
        with pytest.raises(KeyError):
            get_demo_funding("Quantum")

    def test_filtered_years(self):
        result = get_demo_funding("AI/ML", [2022, 2024])
        assert sorted(result.keys()) == [2022, 2024]

    def test_aiml_fy2022_total(self):
        result = get_demo_funding("AI/ML")
        assert result[2022].total_billions == 1.7

    def test_aiml_fy2026_total(self):
        result = get_demo_funding("AI/ML")
        assert result[2026].total_billions == 4.4

    def test_hypersonics_fy2022_rdte_dominant(self):
        result = get_demo_funding("Hypersonics")
        f = result[2022]
        assert f.rdte_billions > f.procurement_billions

    def test_space_procurement_dominant_fy2024(self):
        result = get_demo_funding("Space")
        f = result[2024]
        assert f.procurement_billions > f.rdte_billions

    def test_cyber_om_dominant_all_years(self):
        result = get_demo_funding("Cyber")
        for f in result.values():
            assert f.om_billions > f.rdte_billions


class TestHelpers:
    def test_all_demo_tech_areas_length(self):
        areas = all_demo_tech_areas()
        assert len(areas) == 4

    def test_all_demo_tech_areas_names(self):
        areas = all_demo_tech_areas()
        for area in ["AI/ML", "Hypersonics", "Space", "Cyber"]:
            assert area in areas

    def test_all_tracked_years_length(self):
        years = all_tracked_years()
        assert len(years) == 5

    def test_all_tracked_years_range(self):
        years = all_tracked_years()
        assert min(years) == 2022
        assert max(years) == 2026

    def test_label_aiml(self):
        label = demo_tech_area_label("AI/ML")
        assert "Artificial Intelligence" in label or "AI" in label

    def test_label_hypersonics(self):
        label = demo_tech_area_label("Hypersonics")
        assert "Hypersonic" in label

    def test_label_unknown_returns_area_name(self):
        label = demo_tech_area_label("Unknown")
        assert label == "Unknown"
