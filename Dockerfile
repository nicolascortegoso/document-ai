FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml ./
COPY common/ common/
COPY libs/ libs/
COPY backends/ backends/
COPY pipelines/ pipelines/
COPY infrastructure/ infrastructure/
COPY services/ services/

RUN uv sync
