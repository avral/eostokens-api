FROM python:3.6.5

RUN apt-get update && apt-get install -y \
gdal-bin python-gdal python3-gdal

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 8000

WORKDIR /app

CMD ["gunicorn", "eostokens_api.wsgi", "-b", "0.0.0.0:8000", \
    "--workers=4", \
    "--timeout=30", \
    "--log-level=debug"]
