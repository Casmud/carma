FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV REDIS_URL=redis://redis PYTHONUNBUFFERED=1
ENV DB_URL=sqlite:///db/carma.db

WORKDIR /app
COPY . .

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["reflex", "run", "--env", "prod", "--backend-only", "--loglevel", "debug" ]