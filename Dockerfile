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
 && echo fr_FR.UTF-8 UTF-8 > /etc/locale.gen \
 && /usr/sbin/locale-gen

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --dev

ADD . .
