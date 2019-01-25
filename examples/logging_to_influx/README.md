# Logging RuuviTag

This example shows a rudementary example of collecting measurements from RuuviTags,
storing them to InfluxDB -database and visualizing the data with Grafana.

## Running the example

### Requirements
You're expected to have a working system with Docker and Docker Compose installed.

### Starting up
Start the logger instance by running

```sh
docker-compose up -d
```

After the system has started, browse to
[http://127.0.0.99:3000/d/RuuviTag/ruuvitag](http://127.0.0.99:3000/d/RuuviTag/ruuvitag)
and log in with username `admin` and password `admin`.
