FROM python:bullseye

EXPOSE 8000

WORKDIR /app

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && poetry run ./manage.py migrate \
 && poetry run ./manage.py collectstatic --no-input \
 && poetry run gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi

ARG LANG=fr_FR
ENV LANG=${LANG}.UTF-8 LC_ALL=${LANG}.UTF-8

RUN --mount=type=cache,sharing=locked,target=/root/.cache \
    --mount=type=cache,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,sharing=locked,target=/var/lib/apt \
    apt-get update -qqy && DEBIAN_FRONTEND=noninteractive apt-get install -qqy --no-install-recommends \
    netcat-openbsd \
    postgresql-13-postgis \
    postgresql-server-dev-13 \
 && python -m pip install -U pip \
 && python -m pip install -U pipx \
 && python -m pipx install poetry \
 && echo "${LANG} UTF-8" > /etc/locale.gen \
 && /usr/sbin/locale-gen

ENV PATH=/root/.local/bin:$PATH
ADD pyproject.toml poetry.lock ./
RUN --mount=type=cache,sharing=locked,target=/root/.cache \
    python -m venv .venv \
 && poetry install --no-dev --no-root --no-interaction --no-ansi

ADD . .
