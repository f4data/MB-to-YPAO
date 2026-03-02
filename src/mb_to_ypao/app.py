"""Flask application: web UI for converting MB filters and pushing PEQ to a Yamaha AVR."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from markupsafe import escape

from mb_to_ypao import __version__
from mb_to_ypao.yamaha import (
    AvrResult,
    build_peq_xml,
    check_avr_status,
    prepare_system_from_peq_flat,
    prepare_system_peq_through,
    prettify_xml,
    process_avr_response,
    send_to_avr,
    serialize_xml,
)


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    @app.context_processor
    def inject_version() -> dict[str, str]:
        return {"app_version": __version__}

    # ── Page route ────────────────────────────────────────────────────────
    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    # ── JSON API routes ───────────────────────────────────────────────────
    @app.route("/api/check-status", methods=["POST"])
    def api_check_status() -> tuple[dict[str, object], int]:
        ip = _get_ip()
        if not ip:
            return _error_json("IP address is required."), 400
        result = check_avr_status(ip)
        return _result_json(result), 200

    @app.route("/api/prepare-peq-through", methods=["POST"])
    def api_prepare_peq_through() -> tuple[dict[str, object], int]:
        ip = _get_ip()
        if not ip:
            return _error_json("IP address is required."), 400
        result = prepare_system_peq_through(ip)
        return _result_json(result), 200

    @app.route("/api/prepare-from-peq-flat", methods=["POST"])
    def api_prepare_from_peq_flat() -> tuple[dict[str, object], int]:
        ip = _get_ip()
        if not ip:
            return _error_json("IP address is required."), 400
        result = prepare_system_from_peq_flat(ip)
        return _result_json(result), 200

    @app.route("/api/apply-filters", methods=["POST"])
    def api_apply_filters() -> tuple[dict[str, object], int]:
        ip = _get_ip()
        if not ip:
            return _error_json("IP address is required."), 400

        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            return _error_json("No file uploaded."), 400

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as tmp:
            uploaded.save(tmp)
            tmp_path = Path(tmp.name)

        try:
            content = tmp_path.read_text(encoding="utf-8")
        except Exception as exc:
            return _error_json(f"Error reading file: {exc}"), 400
        finally:
            tmp_path.unlink(missing_ok=True)

        try:
            root = build_peq_xml(content)
            xml_bytes = serialize_xml(root)
        except Exception as exc:
            return _error_json(f"Error parsing filters: {exc}"), 400

        try:
            response = send_to_avr(xml_bytes, ip)
        except Exception as exc:
            return _error_json(f"Connection failed: {exc}"), 200

        result: AvrResult = process_avr_response(response, success_msg="PEQ values applied successfully!")
        pretty_xml = prettify_xml(xml_bytes)
        return {
            "ok": result.ok,
            "message": result.message,
            "input": content,
            "output": escape(pretty_xml),
        }, 200

    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_ip() -> str:
    """Extract the AVR IP from form data or JSON body."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return str(data.get("ip", "")).strip()
    return request.form.get("ip", "").strip()


def _error_json(message: str) -> dict[str, object]:
    return {"ok": False, "message": message}


def _result_json(result: AvrResult) -> dict[str, object]:
    return {"ok": result.ok, "message": result.message}


# ---------------------------------------------------------------------------
# Development entry point
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
