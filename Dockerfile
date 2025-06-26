FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY back/ ./back/

RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "back.cli"]
