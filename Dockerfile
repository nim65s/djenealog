# getting locale…

FROM alpine:edge AS locale

ENV MUSL_LOCPATH=/usr/local/share/i18n/locales/musl
RUN apk add --update git cmake make musl-dev gcc gettext-dev libintl
RUN cd /tmp && git clone https://github.com/rilian-la-te/musl-locales.git
RUN cd /tmp/musl-locales && cmake . && make && make install

FROM alpine:edge

ARG LANG=fr_FR
ENV LANG=${LANG} LC_ALL=${LANG}.UTF-8 MUSL_LOCPATH=/usr/local/share/i18n/locales/musl

RUN mkdir -p \
    /usr/local/etc/profile.d \
    /usr/local/bin \
    /usr/local/share/locale/${LANG}/LC_MESSAGES \
    /usr/local/share/i18n/locales/musl

COPY --from=locale /usr/local/etc/profile.d/00locale.sh \
                   /usr/local/etc/profile.d
COPY --from=locale /usr/local/bin/locale \
                   /usr/local/bin
COPY --from=locale /usr/local/share/locale/${LANG}/LC_MESSAGES/musl-locales.mo \
                   /usr/local/share/local/${LANG}/LC_MESSAGES
COPY --from=locale /usr/local/share/i18n/locales/musl/${LANG}.UTF-8 \
                   /usr/local/share/i18n/locales/musl

# Now the dockerfile begins.

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories \
 && apk update -q \
 && apk add --no-cache \
    gdal \
    geos \
    postgis \
    proj \
    py3-gunicorn \
    py3-psycopg2 \
    py3-raven \
 && pip3 install --no-cache-dir \
    pipenv \
    python-memcached \
 && ln -s /usr/lib/libproj.so.15 /usr/lib/libproj.so

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --dev

ADD . .
