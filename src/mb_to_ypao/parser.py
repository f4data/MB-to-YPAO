"""Parse MultEQ-X / Magic Beans calibration text into structured filter data."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Literal

from mb_to_ypao.constants import GEQ_FREQUENCIES, PEQ_FREQUENCIES, Q_FACTORS, SPEAKERS


# ---------------------------------------------------------------------------
# Domain value objects
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class FilterData:
    """Validated representation of a single PEQ filter band."""

    number: int
    frequency: str
    gain: int
    q_factor: str


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------
def detect_format(text: str) -> Literal["peq", "geq"]:
    """Detect whether *text* uses the ``peq`` (PEQ) or ``geq`` (GEQ) format.

    Detection inspects the first non-empty content line after the first
    ``===`` section separator:

    - If that line starts with ``Filter`` → ``peq``
    - If that line contains ``Hz:`` → ``geq``

    Raises:
        ValueError: If the format cannot be determined.
    """
    found_header = False
    for line in text.strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("=") and stripped.replace("=", "") == "":
            found_header = True
            continue
        if found_header and stripped:
            if stripped.startswith("Filter"):
                return "peq"
            if "Hz:" in stripped:
                return "geq"
    msg = "Cannot detect calibration format from file content."
    raise ValueError(msg)


# ---------------------------------------------------------------------------
# Value-level parsers
# ---------------------------------------------------------------------------
def parse_speaker_name(speaker: str) -> str:
    """Map a MultEQ-X speaker label to the Yamaha XML tag name.

    Raises:
        KeyError: If *speaker* is not a recognised MultEQ-X label.
    """
    return SPEAKERS[speaker]


def parse_frequency(raw: str) -> str:
    """Map a MultEQ-X frequency string to the Yamaha YPAO representation.

    Raises:
        KeyError: If *raw* is not a recognised frequency value.
    """
    return PEQ_FREQUENCIES[raw]


def parse_gain(raw: str) -> int:
    """Convert a gain string like ``'-6.00 dB'`` to a Yamaha integer (x10).

    Example:
        >>> parse_gain("-6.00 dB")
        -60
    """
    value = raw.split()[0].strip()
    return int(float(value) * 10)


def parse_q_factor(raw: str) -> str:
    """Map a MultEQ-X Q-factor string to the Yamaha YPAO representation.

    Raises:
        KeyError: If *raw* is not a recognised Q value.
    """
    return Q_FACTORS[raw]


def encode_geq_gain(gain_db: float) -> int:
    """Round *gain_db* to the nearest 0.5 dB and express as a Yamaha integer (x10).

    The Yamaha GEQ accepts values in steps of 0.5 dB.  The AVR stores them as
    integers with an implicit ÷10 scaling (``Exp=1``).

    Examples:
        >>> encode_geq_gain(-3.87)  # rounds to -4.0 dB
        -40
        >>> encode_geq_gain(-3.73)  # rounds to -3.5 dB
        -35
        >>> encode_geq_gain(0.0)
        0
    """
    # round to nearest 0.5: multiply by 2, round to int, multiply by 5
    return int(round(gain_db * 2) * 5)


# ---------------------------------------------------------------------------
# Text → XML (peq / PEQ format)
# ---------------------------------------------------------------------------
def _build_filter_element(filt: FilterData) -> ET.Element:
    """Create an ``<Band_N>`` XML element from a :class:`FilterData` object."""
    band = ET.Element(f"Band_{filt.number}")

    freq_el = ET.SubElement(band, "Freq")
    freq_el.text = filt.frequency

    gain_el = ET.SubElement(band, "Gain")
    val_el = ET.SubElement(gain_el, "Val")
    val_el.text = str(filt.gain)

    q_el = ET.SubElement(band, "Q")
    q_el.text = filt.q_factor

    return band


def parse_filters_text_peq(text: str) -> ET.Element:
    """Parse the full MB calibration text (peq / PEQ format) and return a ``<Manual_Data>`` XML element.

    The input text is a multi-speaker calibration dump where each speaker
    section is introduced by a name line followed by an ``===`` underline.
    Within each section, numbered *Filter* blocks contain ``Frequency``,
    ``Q factor``, and ``Gain`` key-value pairs.
    """
    lines = text.strip().split("\n")
    manual_data = ET.Element("Manual_Data")
    current_section: ET.Element | None = None
    prev_line = ""

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("=") and stripped.replace("=", "") == "":
            # The previous (non-blank) line is the speaker name.
            speaker_tag = parse_speaker_name(prev_line.strip())
            current_section = ET.SubElement(manual_data, speaker_tag)

        elif stripped.startswith("Filter"):
            band_number = int(stripped.split()[1].strip(":"))
            filter_data: dict[str, str | int] = {"number": band_number}

        elif stripped.startswith("-"):
            key, _, value = stripped.partition(":")
            key = key.strip("- ")
            value = value.strip()

            if key == "Frequency":
                filter_data["frequency"] = parse_frequency(value)
            elif key == "Q factor":
                filter_data["q_factor"] = parse_q_factor(value)
            elif key == "Gain":
                filter_data["gain"] = parse_gain(value)

                # Gain is always the last key — emit the band element.
                if current_section is None:
                    msg = "Encountered filter data before any speaker section header."
                    raise ValueError(msg)

                filt = FilterData(
                    number=int(filter_data["number"]),
                    frequency=str(filter_data["frequency"]),
                    gain=int(filter_data["gain"]),
                    q_factor=str(filter_data["q_factor"]),
                )
                current_section.append(_build_filter_element(filt))

        prev_line = stripped

    return manual_data


# ---------------------------------------------------------------------------
# Text → XML (geq / GEQ format)
# ---------------------------------------------------------------------------
def _build_geq_gain_element(tag: str, val: int) -> ET.Element:
    """Create a ``<Gain_XYZ_Hz>`` XML element with Val, Exp, and Unit children."""
    gain_el = ET.Element(tag)
    val_el = ET.SubElement(gain_el, "Val")
    val_el.text = str(val)
    exp_el = ET.SubElement(gain_el, "Exp")
    exp_el.text = "1"
    unit_el = ET.SubElement(gain_el, "Unit")
    unit_el.text = "dB"
    return gain_el


def parse_filters_text_geq(text: str) -> ET.Element:
    """Parse MB calibration text in geq / GEQ format and return a ``<GEQ>`` XML element.

    The input text lists 7 fixed frequency bands per speaker (63 Hz … 16 kHz)
    as ``<freq>:\\t<gain> dB`` lines.  The LFE channel only has two bands
    (63 Hz and 160 Hz).

    Gain values are rounded to the nearest 0.5 dB and stored as integers
    multiplied by 10 (``Exp=1``).
    """
    lines = text.strip().split("\n")
    geq = ET.Element("GEQ")
    current_section: ET.Element | None = None
    prev_line = ""

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("=") and stripped.replace("=", "") == "":
            # The previous (non-blank) line is the speaker name.
            speaker_tag = parse_speaker_name(prev_line.strip())
            current_section = ET.SubElement(geq, speaker_tag)

        elif "Hz:" in stripped and current_section is not None:
            # e.g. "63 Hz:\t-3.87 dB"
            freq_part, _, gain_part = stripped.partition(":")
            freq_key = freq_part.strip()  # e.g. "63 Hz"
            gain_str = gain_part.strip().split()[0]  # e.g. "-3.87"
            gain_db = float(gain_str)

            tag = GEQ_FREQUENCIES[freq_key]
            val = encode_geq_gain(gain_db)
            current_section.append(_build_geq_gain_element(tag, val))

        prev_line = stripped

    return geq


# ---------------------------------------------------------------------------
# Public dispatcher — auto-detects format
# ---------------------------------------------------------------------------
def parse_filters_text(text: str) -> ET.Element:
    """Parse MB calibration text, auto-detecting the receiver format.

    Delegates to :func:`parse_filters_text_peq` or
    :func:`parse_filters_text_geq` based on :func:`detect_format`.

    Returns:
        - ``<Manual_Data>`` element for the ``peq`` format.
        - ``<GEQ>`` element for the ``geq`` format.
    """
    fmt = detect_format(text)
    if fmt == "geq":
        return parse_filters_text_geq(text)
    return parse_filters_text_peq(text)
