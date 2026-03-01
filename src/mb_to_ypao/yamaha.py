"""Yamaha AVR communication: XML generation and HTTP transport."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.dom import minidom

import requests

from mb_to_ypao.parser import parse_filters_text


# ---------------------------------------------------------------------------
# Domain model for AVR responses
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AvrResult:
    """Outcome of a command sent to the Yamaha AVR."""

    message: str
    status_code: int
    raw_body: str = ""


# ---------------------------------------------------------------------------
# XML construction
# ---------------------------------------------------------------------------
def build_peq_xml(calibration_text: str) -> ET.Element:
    """Build a full ``YAMAHA_AV PUT`` XML tree from raw MB calibration text.

    Returns the root :class:`~xml.etree.ElementTree.Element`.
    """
    manual_data = parse_filters_text(calibration_text)

    root = ET.Element("YAMAHA_AV", cmd="PUT")
    system = ET.SubElement(root, "System")
    speaker_preout = ET.SubElement(system, "Speaker_Preout")
    pattern = ET.SubElement(speaker_preout, "Pattern_1")
    peq = ET.SubElement(pattern, "PEQ")
    peq.append(manual_data)

    return root


def serialize_xml(root: ET.Element) -> bytes:
    """Serialize an :class:`~xml.etree.ElementTree.Element` to UTF-8 bytes."""
    result = ET.tostring(root, encoding="utf-8", method="xml")
    assert isinstance(result, bytes)
    return result



def prettify_xml(xml_bytes: bytes | str) -> str:
    """Return an indented, human-readable representation of *xml_bytes*."""
    if isinstance(xml_bytes, str):
        xml_bytes = xml_bytes.encode("utf-8")
    return minidom.parseString(xml_bytes).toprettyxml(indent="  ")


# ---------------------------------------------------------------------------
# HTTP transport
# ---------------------------------------------------------------------------
def send_to_avr(xml_payload: bytes | str, avr_ip: str, *, timeout: float = 10.0) -> requests.Response:
    """POST *xml_payload* to the Yamaha AVR at *avr_ip*.

    The receiver exposes its control API on port 80 at
    ``/YamahaRemoteControl/ctrl``.
    """
    url = f"http://{avr_ip}:80/YamahaRemoteControl/ctrl"
    headers = {"Content-Type": "application/xml"}
    return requests.post(url, headers=headers, data=xml_payload, timeout=timeout)


def process_avr_response(response: requests.Response) -> AvrResult:
    """Inspect the AVR HTTP *response* and return a user-friendly :class:`AvrResult`."""
    if response.status_code != 200:
        return AvrResult(
            message="Failed to update PEQ values. Could not connect to Yamaha AVR.",
            status_code=response.status_code,
            raw_body=response.text,
        )

    response_xml = ET.fromstring(response.text)
    rc_value = response_xml.get("RC")

    if rc_value == "0":
        return AvrResult(message="PEQ values updated successfully!", status_code=200)

    return AvrResult(
        message="Failed to update PEQ values. The receiver should be powered on.",
        status_code=response.status_code,
        raw_body=response.text,
    )
