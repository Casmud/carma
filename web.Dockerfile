FROM python:3.13-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .


RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update -y && \
    apt-get install zip unzip && \
    apt-get -y install curl

RUN reflex export --frontend-only --no-zip

FROM nginx

COPY --from=builder /app/.web/_static /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf