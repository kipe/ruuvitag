FROM alpine:latest

RUN apk add --no-cache python3 git build-base bluez-dev linux-headers glib-dev && \
    pip3 install git+https://github.com/kipe/ruuvitag.git influxdb

ADD initial /usr/src/bin/initial
ADD ruuvilogger.py /usr/src/bin/ruuvilogger.py

ENV PYTHONUNBUFFERED=1

CMD ["python3", "/usr/src/bin/ruuvilogger.py"]
