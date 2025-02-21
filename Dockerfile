FROM python:3.11.4-slim-bookworm

RUN mkdir /app

COPY . /app

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN python -m venv .venv && \
    . .venv/bin/activate && \
    uv pip install --upgrade pip setuptools wheel && \
    uv pip install -r pyproject.toml

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD ["uv", "run", "main.py"]
