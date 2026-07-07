# syntax=docker/dockerfile:1.7

# ---- base -------------------------------------------------------------
# Shared OS-level setup. libmagic1 is required at *runtime*, not just for
# installing python-magic — DefaultDetector calls into it directly via
# ctypes on every detect_mime() call.
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- builder ------------------------------------------------------------
# Installs the package plus dev dependencies, so lint and tests run against
# the same interpreter and system libraries the runtime image uses.
FROM base AS builder

COPY pyproject.toml ./
COPY common ./common
COPY libs ./libs
COPY backends ./backends
COPY pipelines ./pipelines

# Editable install, not a regular one: docker-compose mounts source as a
# volume for iterative dev, and pytest-cov needs to measure the actual
# source tree (not a copied snapshot in site-packages) for coverage
# numbers to mean anything.
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir pytest pytest-cov ruff

COPY tests ./tests
COPY scripts ./scripts

# ---- test ---------------------------------------------------------------
# `docker build --target test` / CI target: lint, then run the suite with
# coverage. Not used by the runtime image below.
FROM builder AS test

CMD ["sh", "-c", "ruff check . && pytest --cov=common --cov=libs --cov=backends --cov=pipelines --cov-report=term-missing"]

# ---- runtime --------------------------------------------------------------
# Lean production image: no dev dependencies, no test files. There is no
# service entrypoint yet (services/ hasn't shipped code) — this CMD is a
# placeholder smoke test until a real API/worker entrypoint exists.
FROM base AS runtime

COPY pyproject.toml ./
COPY common ./common
COPY libs ./libs
COPY backends ./backends
COPY pipelines ./pipelines
RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 1000 appuser
USER appuser

CMD ["python3", "-c", "import common, libs, backends, pipelines; print('document-ai runtime image OK')"]