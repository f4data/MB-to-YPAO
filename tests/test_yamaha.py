"""Unit tests for mb_to_ypao.yamaha."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from mb_to_ypao.yamaha import (
    AvrResult,
    build_peq_xml,
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
        assert result.status_code == 200
        assert "successfully" in result.message.lower()

    def test_avr_error_code(self) -> None:
        resp = self._mock_response(200, '<YAMAHA_AV RC="3"/>')
        result = process_avr_response(resp)
        assert "powered on" in result.message.lower()

    def test_http_error(self) -> None:
        resp = self._mock_response(500, "Internal Server Error")
        result = process_avr_response(resp)
        assert result.status_code == 500
        assert "connect" in result.message.lower()
