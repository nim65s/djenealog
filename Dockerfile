FROM python:3.12-bullseye

EXPOSE 8000

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && poetry run ./manage.py migrate \
 && poetry run ./manage.py collectstatic --no-input \
 && poetry run gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi

ARG LANG=fr_FR
ENV LANG=${LANG}.UTF-8 LC_ALL=${LANG}.UTF-8

RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,sharing=locked,target=/var/lib/apt \
    --mount=type=cache,sharing=locked,target=/root/.cache \
    apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -qqy --no-install-recommends \
    gcc \
    libexpat1 \
    libpq-dev \
    netcat \
    postgresql-13-postgis \
    postgresql-server-dev-13 \
 && python -m pip install -U pip \
 && python -m pip install -U pipx \
 && python -m pipx install poetry \
 && echo "${LANG} UTF-8" > /etc/locale.gen \
 && /usr/sbin/locale-gen

ADD pyproject.toml poetry.lock ./
RUN --mount=type=cache,sharing=locked,target=/root/.cache \
    poetry install --with prod --no-root --no-interaction --no-ansi

ADD . .
