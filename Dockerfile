FROM python:3.6.5

RUN apt-get update && apt-get install -y \
gdal-bin python-gdal python3-gdal

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

WORKDIR /app/src
