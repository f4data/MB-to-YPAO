"""Unit tests for the Flask web application routes."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from mb_to_ypao.app import create_app
from mb_to_ypao.yamaha import AvrResult

# Path to the sample filter file shipped with the package.
SAMPLE_FILTER_FILE = Path(__file__).resolve().parent.parent / "src" / "mb_to_ypao" / "data" / "MB_custom_7.1_2_Filters_Global.txt"


@pytest.fixture()
def client() -> FlaskClient:
    """Create a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── GET / ─────────────────────────────────────────────────────────────────────


class TestIndexGet:
    def test_returns_200(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_three_sections(self, client: FlaskClient) -> None:
        resp = client.get("/")
        body = resp.data.decode()
        assert "Yamaha AVR Connection" in body
        assert "Preparation" in body
        assert "Magic Beans Filters" in body

    def test_contains_footer(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert b"Fernando Garcia" in resp.data

    def test_contains_verbose_checkbox(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert b"verbose-checkbox" in resp.data


# ── POST /api/check-status ───────────────────────────────────────────────────


class TestCheckStatus:
    @patch("mb_to_ypao.app.check_avr_status")
    def test_success(self, mock_check: MagicMock, client: FlaskClient) -> None:
        mock_check.return_value = AvrResult(ok=True, message="AVR is reachable.", status_code=200)
        resp = client.post("/api/check-status", json={"ip": "192.168.1.1"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_missing_ip(self, client: FlaskClient) -> None:
        resp = client.post("/api/check-status", json={"ip": ""})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["ok"] is False
        assert "required" in data["message"].lower()

    @patch("mb_to_ypao.app.check_avr_status")
    def test_failure(self, mock_check: MagicMock, client: FlaskClient) -> None:
        mock_check.return_value = AvrResult(ok=False, message="Connection failed.", status_code=0)
        resp = client.post("/api/check-status", json={"ip": "10.0.0.1"})
        data = resp.get_json()
        assert data["ok"] is False


# ── POST /api/prepare-peq-through ────────────────────────────────────────────


class TestPreparePeqThrough:
    @patch("mb_to_ypao.app.prepare_system_peq_through")
    def test_success(self, mock_prep: MagicMock, client: FlaskClient) -> None:
        mock_prep.return_value = AvrResult(ok=True, message="All preparation steps completed.", status_code=200)
        resp = client.post("/api/prepare-peq-through", json={"ip": "192.168.1.1"})
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_missing_ip(self, client: FlaskClient) -> None:
        resp = client.post("/api/prepare-peq-through", json={})
        assert resp.status_code == 400


# ── POST /api/prepare-from-peq-flat ──────────────────────────────────────────


class TestPrepareFromPeqFlat:
    @patch("mb_to_ypao.app.prepare_system_from_peq_flat")
    def test_success(self, mock_prep: MagicMock, client: FlaskClient) -> None:
        mock_prep.return_value = AvrResult(ok=True, message="All preparation steps completed.", status_code=200)
        resp = client.post("/api/prepare-from-peq-flat", json={"ip": "192.168.1.1"})
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_missing_ip(self, client: FlaskClient) -> None:
        resp = client.post("/api/prepare-from-peq-flat", json={})
        assert resp.status_code == 400


# ── POST /api/apply-filters ──────────────────────────────────────────────────


class TestApplyFilters:
    @patch("mb_to_ypao.app.send_to_avr")
    def test_with_sample_file(self, mock_send: MagicMock, client: FlaskClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        content = SAMPLE_FILTER_FILE.read_bytes()
        data = {
            "ip": "192.168.1.1",
            "file": (BytesIO(content), "MB_custom_7.1_2_Filters_Global.txt"),
        }
        resp = client.post("/api/apply-filters", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["ok"] is True
        assert json_data["input"]  # non-empty
        assert json_data["output"]  # non-empty

    def test_no_file(self, client: FlaskClient) -> None:
        resp = client.post("/api/apply-filters", data={"ip": "192.168.1.1"}, content_type="multipart/form-data")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["ok"] is False
        assert "no file" in data["message"].lower()

    def test_missing_ip(self, client: FlaskClient) -> None:
        data = {
            "ip": "",
            "file": (BytesIO(b"test"), "test.txt"),
        }
        resp = client.post("/api/apply-filters", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400

    @patch("mb_to_ypao.app.send_to_avr")
    def test_avr_failure(self, mock_send: MagicMock, client: FlaskClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="3"/>'
        mock_send.return_value = mock_resp

        content = SAMPLE_FILTER_FILE.read_bytes()
        data = {
            "ip": "192.168.1.1",
            "file": (BytesIO(content), "Filters.txt"),
        }
        resp = client.post("/api/apply-filters", data=data, content_type="multipart/form-data")
        json_data = resp.get_json()
        assert json_data["ok"] is False
