FROM alpine:latest

RUN apk add --no-cache python3 py3-pip git build-base bluez-dev linux-headers glib-dev && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip3 install git+https://github.com/kipe/ruuvitag.git influxdb

ADD initial /app/initial
ADD ruuvilogger.py /app/ruuvilogger.py

ENV PYTHONUNBUFFERED=1

CMD ["/app/venv/bin/python3", "/app/ruuvilogger.py"]
