"""Tests for usaspending_client.py -- P46 Defense Budget & Appropriations Tracker."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from usaspending_client import (
    _get_keywords, _build_payload, USASpendingError,
    fetch_spending_over_time, build_live_funding,
)
from config import TECH_AREAS, TRACKED_FISCAL_YEARS, DATA_SOURCE_LIVE


class TestGetKeywords:
    def test_aiml_keywords_nonempty(self):
        kws = _get_keywords("AI/ML")
        assert len(kws) >= 1

    def test_hypersonics_keywords_nonempty(self):
        kws = _get_keywords("Hypersonics")
        assert len(kws) >= 1

    def test_aiml_contains_ai_term(self):
        kws = _get_keywords("AI/ML")
        combined = " ".join(kws).lower()
        assert "artificial intelligence" in combined or "machine learning" in combined

    def test_hypersonics_contains_hypersonic(self):
        kws = _get_keywords("Hypersonics")
        combined = " ".join(kws).lower()
        assert "hypersonic" in combined

    def test_space_contains_space_term(self):
        kws = _get_keywords("Space")
        combined = " ".join(kws).lower()
        assert "space" in combined

    def test_cyber_contains_cyber_term(self):
        kws = _get_keywords("Cyber")
        combined = " ".join(kws).lower()
        assert "cyber" in combined

    def test_invalid_area_raises(self):
        with pytest.raises(USASpendingError):
            _get_keywords("Quantum")

    def test_all_areas_have_keywords(self):
        for area in TECH_AREAS:
            kws = _get_keywords(area)
            assert isinstance(kws, list)
            assert len(kws) >= 1


class TestBuildPayload:
    def test_payload_has_group(self):
        payload = _build_payload(["artificial intelligence"])
        assert payload["group"] == "fiscal_year"

    def test_payload_has_filters(self):
        payload = _build_payload(["test"])
        assert "filters" in payload

    def test_payload_keywords_passed(self):
        kws = ["artificial intelligence", "machine learning"]
        payload = _build_payload(kws)
        assert payload["filters"]["keywords"] == kws

    def test_payload_filters_dod(self):
        payload = _build_payload(["test"])
        agencies = payload["filters"]["agencies"]
        assert len(agencies) >= 1
        dod_found = any("Defense" in a.get("name", "") for a in agencies)
        assert dod_found

    def test_payload_has_contract_types(self):
        payload = _build_payload(["test"])
        codes = payload["filters"]["award_type_codes"]
        assert "A" in codes  # contracts


class TestFetchSpendingOverTimeMocked:
    def _mock_response(self, results):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": results}
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_returns_dict_keyed_by_year(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2022"}, "aggregated_amount": 1_700_000_000},
            {"time_period": {"fiscal_year": "2023"}, "aggregated_amount": 2_200_000_000},
        ]
        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = self._mock_response(mock_results)
            result = fetch_spending_over_time("AI/ML", [2022, 2023])
        assert 2022 in result
        assert 2023 in result

    def test_converts_to_billions(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2024"}, "aggregated_amount": 2_800_000_000},
        ]
        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = self._mock_response(mock_results)
            result = fetch_spending_over_time("AI/ML", [2024])
        assert abs(result[2024] - 2.8) < 0.01

    def test_filters_out_of_scope_years(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2019"}, "aggregated_amount": 500_000_000},
            {"time_period": {"fiscal_year": "2024"}, "aggregated_amount": 2_800_000_000},
        ]
        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = self._mock_response(mock_results)
            result = fetch_spending_over_time("AI/ML", [2024])
        assert 2019 not in result
        assert 2024 in result

    def test_empty_results_returns_empty_dict(self):
        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = self._mock_response([])
            result = fetch_spending_over_time("AI/ML")
        assert result == {}

    def test_http_error_raises_usaspending_error(self):
        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.side_effect = Exception("Connection refused")
            with pytest.raises(USASpendingError):
                fetch_spending_over_time("AI/ML")


class TestBuildLiveFunding:
    def test_returns_program_funding_objects(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2022"}, "aggregated_amount": 1_700_000_000},
            {"time_period": {"fiscal_year": "2023"}, "aggregated_amount": 2_200_000_000},
        ]
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": mock_results}
        mock_resp.raise_for_status.return_value = None

        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = mock_resp
            result = build_live_funding("AI/ML", [2022, 2023])

        from models import ProgramFunding
        for f in result.values():
            assert isinstance(f, ProgramFunding)

    def test_no_breakdown_in_live_mode(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2024"}, "aggregated_amount": 2_800_000_000},
        ]
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": mock_results}
        mock_resp.raise_for_status.return_value = None

        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = mock_resp
            result = build_live_funding("AI/ML", [2024])

        f = result[2024]
        assert f.rdte_billions is None
        assert f.procurement_billions is None
        assert f.om_billions is None

    def test_data_source_live(self):
        mock_results = [
            {"time_period": {"fiscal_year": "2024"}, "aggregated_amount": 2_800_000_000},
        ]
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": mock_results}
        mock_resp.raise_for_status.return_value = None

        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = mock_resp
            result = build_live_funding("AI/ML", [2024])

        assert result[2024].data_source == DATA_SOURCE_LIVE

    def test_missing_years_have_zero_total(self):
        # API returns no data for 2023 → should still appear with 0.0
        mock_results = [
            {"time_period": {"fiscal_year": "2022"}, "aggregated_amount": 1_700_000_000},
        ]
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": mock_results}
        mock_resp.raise_for_status.return_value = None

        with patch("usaspending_client.requests") as mock_requests:
            mock_requests.post.return_value = mock_resp
            result = build_live_funding("AI/ML", [2022, 2023])

        assert result[2023].total_billions == 0.0
