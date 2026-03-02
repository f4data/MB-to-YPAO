"""Yamaha AVR communication: XML generation and HTTP transport."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.dom import minidom

import requests

from mb_to_ypao.constants import (
    AVR_DATA_COPY_FROM_FLAT_XML,
    AVR_GET_STATUS_XML,
    AVR_RESET_PEQ_XML,
    AVR_RESET_SOUND_VIDEO_XML,
    AVR_RESET_SURROUND_XML,
    AVR_SET_PEQ_THROUGH_XML,
    AVR_SET_SPK_LARGE_XML,
)
from mb_to_ypao.parser import parse_filters_text


# ---------------------------------------------------------------------------
# Domain model for AVR responses
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AvrResult:
    """Outcome of a command sent to the Yamaha AVR."""

    ok: bool
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


def process_avr_response(response: requests.Response, *, success_msg: str = "OK") -> AvrResult:
    """Inspect the AVR HTTP *response* and return a user-friendly :class:`AvrResult`."""
    if response.status_code != 200:
        return AvrResult(
            ok=False,
            message="Failed: could not connect to Yamaha AVR.",
            status_code=response.status_code,
            raw_body=response.text,
        )

    response_xml = ET.fromstring(response.text)
    rc_value = response_xml.get("RC")

    if rc_value == "0":
        return AvrResult(ok=True, message=success_msg, status_code=200)

    return AvrResult(
        ok=False,
        message="Failed: the receiver should be powered on (RC≠0).",
        status_code=response.status_code,
        raw_body=response.text,
    )


# ---------------------------------------------------------------------------
# High-level AVR operations
# ---------------------------------------------------------------------------
def check_avr_status(avr_ip: str) -> AvrResult:
    """Send a lightweight GET command to verify AVR connectivity."""
    try:
        response = send_to_avr(AVR_GET_STATUS_XML, avr_ip, timeout=5.0)
    except requests.RequestException as exc:
        return AvrResult(ok=False, message=f"Connection failed: {exc}", status_code=0)
    return process_avr_response(response, success_msg="AVR is reachable and powered on.")


def _run_preparation_steps(avr_ip: str, steps: list[tuple[str, str]]) -> AvrResult:
    """Execute a sequence of named XML commands against the AVR.

    Returns the first failing :class:`AvrResult`, or a success result if all
    steps complete without error.
    """
    for step_name, xml_payload in steps:
        try:
            response = send_to_avr(xml_payload, avr_ip)
        except requests.RequestException as exc:
            return AvrResult(ok=False, message=f"{step_name}: connection failed — {exc}", status_code=0)

        result = process_avr_response(response, success_msg="OK")
        if not result.ok:
            return AvrResult(
                ok=False,
                message=f"{step_name}: {result.message}",
                status_code=result.status_code,
                raw_body=result.raw_body,
            )
    return AvrResult(ok=True, message="All preparation steps completed successfully.", status_code=200)


def prepare_system_peq_through(avr_ip: str) -> AvrResult:
    """Prepare the AVR for MB calibration using PEQ Through mode.

    Steps: set PEQ Through → set speakers Large → reset PEQ →
    reset Surround → reset Sound/Video.
    """
    steps: list[tuple[str, str]] = [
        ("Set PEQ Through", AVR_SET_PEQ_THROUGH_XML),
        ("Set speakers Large", AVR_SET_SPK_LARGE_XML),
        ("Reset PEQ", AVR_RESET_PEQ_XML),
        ("Reset Surround", AVR_RESET_SURROUND_XML),
        ("Reset Sound/Video", AVR_RESET_SOUND_VIDEO_XML),
    ]
    return _run_preparation_steps(avr_ip, steps)


def prepare_system_from_peq_flat(avr_ip: str) -> AvrResult:
    """Prepare the AVR for MB calibration by copying from PEQ Flat.

    Steps: Data Copy From Flat → set speakers Large → reset PEQ →
    reset Surround → reset Sound/Video.
    """
    steps: list[tuple[str, str]] = [
        ("Data Copy From Flat", AVR_DATA_COPY_FROM_FLAT_XML),
        ("Set speakers Large", AVR_SET_SPK_LARGE_XML),
        ("Reset PEQ", AVR_RESET_PEQ_XML),
        ("Reset Surround", AVR_RESET_SURROUND_XML),
        ("Reset Sound/Video", AVR_RESET_SOUND_VIDEO_XML),
    ]
    return _run_preparation_steps(avr_ip, steps)
