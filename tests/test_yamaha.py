"""Unit tests for mb_to_ypao.yamaha."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import requests

from mb_to_ypao.yamaha import (
    AvrResult,
    build_peq_xml,
    check_avr_status,
    prepare_system_from_peq_flat,
    prepare_system_peq_through,
    prettify_xml,
    process_avr_response,
    serialize_xml,
)

SAMPLE_INPUT = """\
Set up the channels according to this configuration.

Front Left
==========
Filter 1:
- Frequency: 125 Hz
- Q factor: 0.50
- Gain: -6.00 dB
"""


# ── XML construction ─────────────────────────────────────────────────────────


class TestBuildPeqXml:
    def test_root_tag(self) -> None:
        root = build_peq_xml(SAMPLE_INPUT)
        assert root.tag == "YAMAHA_AV"
        assert root.get("cmd") == "PUT"

    def test_nested_structure(self) -> None:
        root = build_peq_xml(SAMPLE_INPUT)
        peq = root.find("System/Speaker_Preout/Pattern_1/PEQ")
        assert peq is not None
        manual_data = peq.find("Manual_Data")
        assert manual_data is not None

    def test_contains_speaker_bands(self) -> None:
        root = build_peq_xml(SAMPLE_INPUT)
        front_l = root.find(".//Front_L")
        assert front_l is not None
        assert front_l.find("Band_1") is not None


class TestSerializeXml:
    def test_returns_bytes(self) -> None:
        root = ET.Element("test")
        result = serialize_xml(root)
        assert isinstance(result, bytes)
        assert b"<test" in result


class TestPrettifyXml:
    def test_produces_indented_output(self) -> None:
        raw = b"<root><child/></root>"
        pretty = prettify_xml(raw)
        assert "  <child/>" in pretty

    def test_accepts_string(self) -> None:
        pretty = prettify_xml("<root><child/></root>")
        assert "  <child/>" in pretty


# ── AVR response processing ─────────────────────────────────────────────────


class TestProcessAvrResponse:
    def _mock_response(self, status_code: int, text: str) -> MagicMock:
        mock = MagicMock()
        mock.status_code = status_code
        mock.text = text
        return mock

    def test_success(self) -> None:
        resp = self._mock_response(200, '<YAMAHA_AV RC="0"/>')
        result = process_avr_response(resp)
        assert isinstance(result, AvrResult)
        assert result.ok is True
        assert result.status_code == 200

    def test_success_custom_msg(self) -> None:
        resp = self._mock_response(200, '<YAMAHA_AV RC="0"/>')
        result = process_avr_response(resp, success_msg="Custom OK")
        assert result.message == "Custom OK"

    def test_avr_error_code(self) -> None:
        resp = self._mock_response(200, '<YAMAHA_AV RC="3"/>')
        result = process_avr_response(resp)
        assert result.ok is False
        assert "powered on" in result.message.lower()

    def test_http_error(self) -> None:
        resp = self._mock_response(500, "Internal Server Error")
        result = process_avr_response(resp)
        assert result.ok is False
        assert result.status_code == 500
        assert "connect" in result.message.lower()


# ── check_avr_status ─────────────────────────────────────────────────────────


class TestCheckAvrStatus:
    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_success(self, mock_send: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        result = check_avr_status("192.168.1.1")
        assert result.ok is True
        assert "reachable" in result.message.lower()

    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_connection_error(self, mock_send: MagicMock) -> None:
        mock_send.side_effect = requests.ConnectionError("refused")
        result = check_avr_status("10.0.0.1")
        assert result.ok is False
        assert "failed" in result.message.lower()


# ── prepare_system_peq_through ───────────────────────────────────────────────


class TestPrepareSystemPeqThrough:
    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_all_steps_succeed(self, mock_send: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        result = prepare_system_peq_through("192.168.1.1")
        assert result.ok is True
        assert mock_send.call_count == 5

    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_partial_failure(self, mock_send: MagicMock) -> None:
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.text = '<YAMAHA_AV RC="0"/>'

        fail_resp = MagicMock()
        fail_resp.status_code = 200
        fail_resp.text = '<YAMAHA_AV RC="3"/>'

        mock_send.side_effect = [ok_resp, ok_resp, fail_resp]

        result = prepare_system_peq_through("192.168.1.1")
        assert result.ok is False
        assert mock_send.call_count == 3  # stopped at 3rd step

    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_connection_failure(self, mock_send: MagicMock) -> None:
        mock_send.side_effect = requests.ConnectionError("refused")
        result = prepare_system_peq_through("10.0.0.1")
        assert result.ok is False
        assert "connection failed" in result.message.lower()


# ── prepare_system_from_peq_flat ─────────────────────────────────────────────


class TestPrepareSystemFromPeqFlat:
    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_all_steps_succeed(self, mock_send: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<YAMAHA_AV RC="0"/>'
        mock_send.return_value = mock_resp

        result = prepare_system_from_peq_flat("192.168.1.1")
        assert result.ok is True
        assert mock_send.call_count == 5

    @patch("mb_to_ypao.yamaha.send_to_avr")
    def test_partial_failure(self, mock_send: MagicMock) -> None:
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.text = '<YAMAHA_AV RC="0"/>'

        fail_resp = MagicMock()
        fail_resp.status_code = 500
        fail_resp.text = "Error"

        mock_send.side_effect = [ok_resp, fail_resp]

        result = prepare_system_from_peq_flat("192.168.1.1")
        assert result.ok is False
        assert mock_send.call_count == 2
