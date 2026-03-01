"""Unit tests for mb_to_ypao.parser."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from mb_to_ypao.parser import (
    FilterData,
    parse_filters_text,
    parse_frequency,
    parse_gain,
    parse_q_factor,
    parse_speaker_name,
)

# ── Value-level parsers ──────────────────────────────────────────────────────


class TestParseSpeakerName:
    def test_known_speaker(self) -> None:
        assert parse_speaker_name("Front Left") == "Front_L"
        assert parse_speaker_name("Center") == "Center"
        assert parse_speaker_name("LFE") == "Subwoofer_1"

    def test_unknown_speaker_raises(self) -> None:
        with pytest.raises(KeyError):
            parse_speaker_name("Nonexistent Speaker")


class TestParseFrequency:
    def test_known_frequency(self) -> None:
        assert parse_frequency("125 Hz") == "125.0 Hz"
        assert parse_frequency("1000 Hz") == "1.00 kHz"

    def test_unknown_frequency_raises(self) -> None:
        with pytest.raises(KeyError):
            parse_frequency("999999 Hz")


class TestParseGain:
    def test_negative_gain(self) -> None:
        assert parse_gain("-6.00 dB") == -60

    def test_positive_gain(self) -> None:
        assert parse_gain("2.50 dB") == 25

    def test_zero_gain(self) -> None:
        assert parse_gain("0.00 dB") == 0

    def test_fractional_gain(self) -> None:
        assert parse_gain("-3.50 dB") == -35


class TestParseQFactor:
    def test_known_q(self) -> None:
        assert parse_q_factor("0.50") == "0.500"
        assert parse_q_factor("3.17") == "3.175"

    def test_unknown_q_raises(self) -> None:
        with pytest.raises(KeyError):
            parse_q_factor("99.99")


# ── FilterData dataclass ─────────────────────────────────────────────────────


class TestFilterData:
    def test_creation(self) -> None:
        f = FilterData(number=1, frequency="125.0 Hz", gain=-60, q_factor="0.500")
        assert f.number == 1
        assert f.frequency == "125.0 Hz"
        assert f.gain == -60
        assert f.q_factor == "0.500"

    def test_immutable(self) -> None:
        f = FilterData(number=1, frequency="125.0 Hz", gain=0, q_factor="1.000")
        with pytest.raises(AttributeError):
            f.number = 2  # type: ignore[misc]


# ── Full text parser ─────────────────────────────────────────────────────────

SAMPLE_INPUT = """\
Set up the channels according to this configuration.

Front Left
==========
Filter 1:
- Frequency: 125 Hz
- Q factor: 0.50
- Gain: -6.00 dB
Filter 2:
- Frequency: 1000 Hz
- Q factor: 1.26
- Gain: 1.50 dB
"""


class TestParseFiltersText:
    def test_produces_manual_data_element(self) -> None:
        root = parse_filters_text(SAMPLE_INPUT)
        assert root.tag == "Manual_Data"

    def test_contains_speaker_section(self) -> None:
        root = parse_filters_text(SAMPLE_INPUT)
        front_l = root.find("Front_L")
        assert front_l is not None

    def test_band_count(self) -> None:
        root = parse_filters_text(SAMPLE_INPUT)
        front_l = root.find("Front_L")
        assert front_l is not None
        bands = list(front_l)
        assert len(bands) == 2

    def test_band_values(self) -> None:
        root = parse_filters_text(SAMPLE_INPUT)
        front_l = root.find("Front_L")
        assert front_l is not None
        band1 = front_l.find("Band_1")
        assert band1 is not None

        freq = band1.find("Freq")
        assert freq is not None
        assert freq.text == "125.0 Hz"

        gain_val = band1.find("Gain/Val")
        assert gain_val is not None
        assert gain_val.text == "-60"

        q = band1.find("Q")
        assert q is not None
        assert q.text == "0.500"

    def test_roundtrip_to_xml_string(self) -> None:
        root = parse_filters_text(SAMPLE_INPUT)
        xml_bytes = ET.tostring(root, encoding="unicode")
        reparsed = ET.fromstring(xml_bytes)
        assert reparsed.tag == "Manual_Data"
