FROM python:3.13-slim

ENV UV_PYTHON_DOWNLOADS=never

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates libmagic1 gettext && rm -rf /var/lib/apt/lists/*
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
COPY site .
COPY .env .
COPY pyproject.toml .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY uv.lock .

RUN uv sync --frozen --no-dev
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "labelserver.wsgi:application"]

