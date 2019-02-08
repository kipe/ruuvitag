from math import isnan
from ruuvitag import RuuviDaemon
from influxdb import InfluxDBClient


class RuuviLogger(RuuviDaemon):
    def __init__(self, *args, **kwargs):
        super(RuuviLogger, self).__init__(*args, **kwargs)
        self.influx = InfluxDBClient(host='127.0.0.99', database='ruuvitag')

        print(self.influx.get_list_database())
        if 'ruuvitag' not in [x['name'] for x in self.influx.get_list_database()]:
            self.initial_setup()

    def initial_setup(self):
        import requests
        from requests.auth import HTTPBasicAuth

        import initial

        print('Running initial setup!')
        r = requests.post(
            'http://127.0.0.99:3000/api/datasources',
            auth=HTTPBasicAuth('admin', 'admin'),
            json=initial.DATASOURCE
        )
        try:
            r.raise_for_status()
        except Exception as e:
            print(r.content)
            raise

        r = requests.post(
            'http://127.0.0.99:3000/api/dashboards/db',
            auth=HTTPBasicAuth('admin', 'admin'),
            json=initial.DASHBOARD
        )
        try:
            r.raise_for_status()
        except Exception as e:
            print(r.content)
            raise

        # Create 'ruuvitag' database
        self.influx.create_database('ruuvitag')

    def callback(self, tag, is_new=False):
        tag_as_dict = tag.as_dict()

        measurement_tags = {
            'address': tag_as_dict.pop('address'),
            'protocol': str(tag_as_dict.pop('protocol')),
            'movement_detected': 'true' if tag.movement_detected.is_set() else 'false',
        }
        tag.movement_detected.clear()

        self.influx.write_points(
            [{
                'measurement': 'ruuvitag',
                'time': tag_as_dict.pop('last_seen'),
                'fields': {
                    key: value
                    for key, value in tag_as_dict.items()
                    # Filter out NaN -values, as InfluxDB doesn't like them
                    if not isnan(value)
                },
            }],
            tags=measurement_tags
        )


if __name__ == '__main__':
    import time

    ruuvilogger = RuuviLogger()
    ruuvilogger.start()

    while ruuvilogger.is_alive():
        time.sleep(1)

    ruuvilogger.stop()
