FROM debian:buster-slim

EXPOSE 8000

RUN mkdir /app
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
    pipenv \
    postgresql-11-postgis \
    postgresql-server-dev-11 \
    python3-memcache \
    python3-psycopg2 \
    python3-setuptools \
 && rm -rf /var/lib/apt/lists/* \
 && echo "${LANG} UTF-8" > /etc/locale.gen \
 && /usr/sbin/locale-gen

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --dev

ADD . .
