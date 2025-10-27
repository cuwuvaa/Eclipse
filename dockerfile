FROM python:3.13-alpine

WORKDIR /Eclipse

COPY requirements.txt .
RUN apk add --no-cache build-base && pip install -r requirements.txt

COPY . .