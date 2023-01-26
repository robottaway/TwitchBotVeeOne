from python:3.9-slim-bullseye

WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt