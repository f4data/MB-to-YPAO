"""Flask application: web UI for converting MB filters and pushing PEQ to a Yamaha AVR."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, render_template, request
from markupsafe import escape

from mb_to_ypao.constants import AVR_RESET_PEQ_XML
from mb_to_ypao.yamaha import (
    AvrResult,
    build_peq_xml,
    prettify_xml,
    process_avr_response,
    send_to_avr,
    serialize_xml,
)


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        if request.method == "POST":
            action: str | None = request.form.get("action")
            ip: str = request.form.get("ip", "")

            if action == "reset":
                return _handle_reset(ip)

            if action == "submit":
                return _handle_submit(ip)

        return render_template("index.html")

    @app.route("/about")
    def about() -> str:
        return "This is the about page."

    return app


# ---------------------------------------------------------------------------
# Route helpers
# ---------------------------------------------------------------------------
def _handle_reset(ip: str) -> str:
    """Reset all PEQ values on the AVR to defaults."""
    xml_payload = AVR_RESET_PEQ_XML
    response = send_to_avr(xml_payload, ip)
    result = process_avr_response(response)
    pretty_xml = prettify_xml(xml_payload)
    return render_template("index.html", response=result.message, avr_data=escape(pretty_xml))


def _handle_submit(ip: str) -> str:
    """Parse an uploaded MB filter file, push the PEQ to the AVR."""
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return render_template("index.html", response="No file uploaded.")

    # Save to a temporary file so we don't litter the working directory.
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as tmp:
        uploaded.save(tmp)
        tmp_path = Path(tmp.name)

    try:
        content = tmp_path.read_text(encoding="utf-8")
    except Exception as exc:
        return render_template("index.html", response=f"Error reading file: {exc}")
    finally:
        tmp_path.unlink(missing_ok=True)

    root = build_peq_xml(content)
    xml_bytes = serialize_xml(root)

    response = send_to_avr(xml_bytes, ip)
    result: AvrResult = process_avr_response(response)

    pretty_xml = prettify_xml(xml_bytes)
    return render_template(
        "index.html",
        response=result.message,
        mb_data=content,
        avr_data=escape(pretty_xml),
    )


# ---------------------------------------------------------------------------
# Development entry point
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
