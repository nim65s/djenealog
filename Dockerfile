FROM python:3.7-alpine

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

RUN apk update -q \
 && apk add --no-cache \
    libpq \
 && apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
 && pip3 install --no-cache-dir \
    gunicorn \
    pipenv \
    psycopg2 \
    python-memcached \
    raven \
 && apk del --no-cache .build-deps

ENV PYTHONPATH=/usr/lib/python3.7/site-packages

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi
