FROM python:3.9.6-alpine

WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN apk update \
     && apk add linux-headers build-base libffi-dev openssl-dev postgresql-dev python3-dev musl-dev cargo
#    && apk add linux-headers build-base postgresql-dev gcc python3-dev musl-dev libffi-dev openssl-dev libressl-dev g++
RUN pip install --upgrade pip
COPY requirements-docker.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

