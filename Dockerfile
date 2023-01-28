# syntax=docker/dockerfile:1

FROM python:3.9.5-slim

WORKDIR /app

COPY requirements.txt requirements.txt


RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip3 install -r requirements.txt


COPY backend/ .

CMD [ "python3", "manage.py" , "runserver"]