"""Parse MultEQ-X / Magic Beans calibration text into structured filter data."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from mb_to_ypao.constants import FREQUENCIES, Q_FACTORS, SPEAKERS


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
    return FREQUENCIES[raw]


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


# ---------------------------------------------------------------------------
# Text → XML
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


def parse_filters_text(text: str) -> ET.Element:
    """Parse the full MB calibration text and return a ``<Manual_Data>`` XML element.

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
