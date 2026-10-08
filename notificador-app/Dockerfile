
FROM python:3.8.13-alpine3.15

WORKDIR /notificador-app

RUN apk add gcc musl-dev librdkafka-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD python app.py
