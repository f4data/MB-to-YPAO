# MB-to-YPAO

Convert the Magic Beans calibration output format to YPAO format and push it to the AVR.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Astral's Python package manager)
- Docker (optional, for container deployment)

## Installation

### Local development

```bash
# Clone the repository
git clone https://github.com/f4data/MB-to-YPAO.git
cd MB-to-YPAO

# Install all dependencies (including dev tools)
uv sync --dev

# Run the application
uv run python -m mb_to_ypao.app
```

The app will be available at `http://localhost:5002`.

### Docker

```bash
# Build the image
docker build -t mb-to-ypao .

# Run the container
docker run \
  --name mb-to-ypao \
  -p 5002:5002 \
  mb-to-ypao
```

Or pull the pre-built image:

```bash
docker run \
  --name mb-to-ypao \
  -p 5002:5002 \
  ghcr.io/f4data/mb-to-ypao:latest
```

## Usage

1. Run Magic Beans and store the calibration file(s)
2. Open a web browser and navigate to `http://localhost:5002` or `http://<docker_server_ip>:5002`
3. Switch ON your Yamaha AVR
4. Provide the IP Address of your Yamaha AVR
5. Select the file you want to upload
6. Done

## Development

### Run tests

```bash
uv run pytest tests/ -v
```

### Lint and format

```bash
# Check for lint issues
uv run ruff check src/ tests/

# Auto-fix fixable issues
uv run ruff check --fix src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Apply formatting
uv run ruff format src/ tests/
```

### Type checking

```bash
uv run mypy src/
```

## Project Structure

```
MB-to-YPAO/
├── pyproject.toml              # Project config (deps, ruff, mypy, pytest)
├── Dockerfile                  # Multi-stage build with uv
├── src/
│   └── mb_to_ypao/
│       ├── __init__.py
│       ├── constants.py        # Mapping tables and static XML payloads
│       ├── parser.py           # MB text → XML parsing
│       ├── yamaha.py           # XML generation and AVR communication
│       ├── app.py              # Flask app and routes
│       ├── templates/          # Jinja2 HTML templates
│       └── data/               # Sample calibration files
└── tests/
    ├── test_parser.py
    ├── test_yamaha.py
    └── test_app.py
```
