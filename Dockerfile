FROM python:alpine3.7

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

ADD requirements.txt ./

RUN apk update -q && apk add -q --no-cache \
    py3-psycopg2 \
 && pip3 install --no-cache-dir -r requirements.txt \
    gunicorn \
    python-memcached
ENV PYTHONPATH=/usr/lib/python3.6/site-packages

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi
