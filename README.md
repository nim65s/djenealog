# Djenealog
[![Build Status](https://travis-ci.org/nim65s/djenealog.svg?branch=master)](https://travis-ci.org/nim65s/djenealog)
[![Coverage Status](https://coveralls.io/repos/github/nim65s/djenealog/badge.svg?branch=master)](https://coveralls.io/github/nim65s/djenealog?branch=master)

This app gives you a svg of a family, and can import csv files from Gramps

## Reverse Proxy

This app needs a reverse proxy, like [proxyta.net](https://framagit.org/nim65s/proxyta.net)

## Dev

```
echo POSTGRES_PASSWORD=$(openssl rand -base64 32) >> .env
echo SECRET_KEY=$(openssl rand -base64 32) >> .env
echo DEBUG=True >> .env
. .env
docker-compose up -d --build
```

You may then want to create an admin: `docker-compose exec djenealog ./manage.py createsuperuser`

## Load json

```
docker cp djenealog.json djenealog_djenealog_1:/djenealog.json
docker exec -it djenealog_djenealog_1 ./manage.py loaddata /djenealog.json
```
