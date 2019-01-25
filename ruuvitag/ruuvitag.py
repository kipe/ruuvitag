import pendulum
from threading import Event

from bluepy import btle
from bitstring import BitArray


class RuuviTag(object):
    def __init__(self, address, protocol, temperature=float('nan'),
                 humidity=float('nan'), pressure=float('nan'),
                 acceleration_x=float('nan'), acceleration_y=float('nan'),
                 acceleration_z=float('nan'),
                 battery_voltage=float('nan'), tx_power=float('nan'),
                 movement_counter=0, measurement_sequence=0):

        self.last_seen = pendulum.now()
        self.address = address
        self.protocol = protocol
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.acceleration_z = acceleration_z
        self.battery_voltage = battery_voltage
        self.tx_power = tx_power
        self.movement_counter = movement_counter
        self.measurement_sequence = measurement_sequence

        self.movement_detected = Event()

    def __repr__(self):
        return '<RuuviTag V%i %s %.02fc, %.02f%%, %s>' % (
            self.protocol,
            self.address,
            self.temperature,
            self.humidity,
            self.last_seen.isoformat()
        )

    def update(self, temperature=None, humidity=None, pressure=None,
               acceleration_x=None, acceleration_y=None, acceleration_z=None,
               battery_voltage=None, tx_power=None,
               movement_counter=None, measurement_sequence=None, **kwargs):

        self.last_seen = pendulum.now()

        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.acceleration_z = acceleration_z
        self.battery_voltage = battery_voltage
        self.tx_power = tx_power

        if movement_counter != self.movement_counter:
            self.movement_detected.set()

        self.movement_counter = movement_counter
        self.measurement_sequence = measurement_sequence

    def as_dict(self):
        return {
            'address': self.address,
            'protocol': self.protocol,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'acceleration_x': self.acceleration_x,
            'acceleration_y': self.acceleration_y,
            'acceleration_z': self.acceleration_z,
            'battery_voltage': self.battery_voltage,
            'tx_power': self.tx_power,
            'movement_counter': self.movement_counter,
            'measurement_sequence': self.measurement_sequence,
            'last_seen': self.last_seen,
        }

    @classmethod
    def parse(cls, address, data):
        b = BitArray(bytes=data)

        if b.find('0xFF990403'):
            b = list(b.split('0xFF990403', count=2))[-1]
            _, humidity, temperature, temperature_fraction, pressure, \
                accel_x, accel_y, accel_z, battery_voltage = b.unpack(
                    'uint:32, uint:8, int:8, uint:8, uint:16,' +
                    'int:16, int:16, int:16, uint:16')

            return cls(
                address,
                3,
                temperature=float(temperature) + temperature_fraction / 100.0,
                humidity=humidity / 2.0,
                pressure=(pressure + 50000) / 100.0,
                acceleration_x=accel_x / 1000.0,
                acceleration_y=accel_y / 1000.0,
                acceleration_z=accel_z / 1000.0,
                battery_voltage=battery_voltage / 1000.0
            )

        if b.find('0xFF990405'):
            b = list(b.split('0xFF990405', count=2))[-1]
            _, temperature, humidity, pressure, \
                accel_x, accel_y, accel_z, \
                battery_voltage, tx_power, \
                movement_counter, measurement_sequence, mac = b.unpack(
                    'uint:32, int:16, uint:16, uint:16,' +
                    'int:16, int:16, int:16,' +
                    'uint:11, uint:5,' +
                    'uint:8, uint:16, uint:48')

            mac = '%x' % mac
            mac = ':'.join(mac[i:i + 2] for i in range(0, 12, 2))

            return cls(
                address,
                5,
                temperature=float(temperature) * 0.005,
                humidity=humidity * 0.0025,
                pressure=(pressure + 50000) / 100.0,
                acceleration_x=accel_x / 1000.0,
                acceleration_y=accel_y / 1000.0,
                acceleration_z=accel_z / 1000.0,
                battery_voltage=(battery_voltage + 1600) / 1000.0,
                tx_power=-40 + tx_power,
                movement_counter=movement_counter,
                measurement_sequence=measurement_sequence
            )

    @classmethod
    def scan(cls, interface_index=0, timeout=2):
        for device in btle.Scanner(interface_index).scan(timeout):
            try:
                tag = cls.parse(device.addr, device.rawData)
                if tag:
                    yield tag
            except:
                pass
