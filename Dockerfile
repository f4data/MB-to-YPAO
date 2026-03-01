# ── Stage 1: Build with uv ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv (Astral's fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency metadata first (layer-cache friendly)
COPY pyproject.toml uv.lock* ./

# Install runtime dependencies only (no dev deps)
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# Copy the rest of the source code
COPY src/ src/
COPY README.md ./

# Install the project itself
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual env and source from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Put the venv on PATH so gunicorn is directly available
ENV PATH="/app/.venv/bin:$PATH"

# Creates a non-root user for security
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "mb_to_ypao.app:app"]
