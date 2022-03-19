# syntax=docker/dockerfile:1
FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
#RUN apk update && apk add bash
#RUN apk add g++ jpeg-dev zlib-dev libjpeg make
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/
