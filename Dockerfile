FROM debian:buster-slim

EXPOSE 8000

WORKDIR /app

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn3 \
    --bind 0.0.0.0 \
    testproject.wsgi

ARG LANG=fr_FR
ENV LANG=${LANG}.UTF-8 LC_ALL=${LANG}.UTF-8

RUN apt update -qqy \
 && apt install -qqy --no-install-recommends \
    gunicorn3 \
    netcat-openbsd \
    postgresql-11-postgis \
    postgresql-server-dev-11 \
    python3-memcache \
    python3-pip \
    python3-psycopg2 \
    python3-setuptools \
    python3-venv \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --no-cache-dir poetry \
 && echo "${LANG} UTF-8" > /etc/locale.gen \
 && /usr/sbin/locale-gen

ADD pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local \
 && poetry install --no-dev --no-root --no-interaction --no-ansi

ADD . .
