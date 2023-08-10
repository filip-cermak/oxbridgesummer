FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
COPY ./app /app

RUN pip install --no-cache-dir -r /tmp/requirements.txt 

CMD uvicorn main:app --port=8000 --host=0.0.0.0