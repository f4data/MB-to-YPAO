"""Unit tests for the Flask web application routes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from mb_to_ypao.app import create_app


@pytest.fixture()
def client() -> FlaskClient:
    """Create a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── GET / ─────────────────────────────────────────────────────────────────────


class TestIndexGet:
    def test_returns_200(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_form(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert b"<form" in resp.data


# ── GET /about ────────────────────────────────────────────────────────────────


class TestAbout:
    def test_returns_200(self, client: FlaskClient) -> None:
        resp = client.get("/about")
        assert resp.status_code == 200
        assert b"about" in resp.data.lower()


# ── POST / (reset) ───────────────────────────────────────────────────────────


class TestResetAction:
    @patch("mb_to_ypao.app.send_to_avr")
    def test_reset_calls_avr(self, mock_send: MagicMock, client: FlaskClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        resp = client.post("/", data={"action": "reset", "ip": "192.168.1.1"})
        assert resp.status_code == 200
        mock_send.assert_called_once()


# ── POST / (submit) ──────────────────────────────────────────────────────────

SAMPLE_MB_FILE = b"""\
Set up the channels according to this configuration.

Front Left
==========
Filter 1:
- Frequency: 125 Hz
- Q factor: 0.50
- Gain: -6.00 dB
"""


class TestSubmitAction:
    @patch("mb_to_ypao.app.send_to_avr")
    def test_submit_with_file(self, mock_send: MagicMock, client: FlaskClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        from io import BytesIO

        data = {
            "action": "submit",
            "ip": "192.168.1.1",
            "file": (BytesIO(SAMPLE_MB_FILE), "Filters.txt"),
        }
        resp = client.post("/", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        mock_send.assert_called_once()

    def test_submit_no_file(self, client: FlaskClient) -> None:
        resp = client.post("/", data={"action": "submit", "ip": "192.168.1.1"})
        assert resp.status_code == 200
        assert b"No file uploaded" in resp.data
