import pendulum
from threading import Event

from bluepy import btle
from bitstring import BitArray


class RuuviTag(object):
    '''An instance of RuuviTag. Usually created by RuuviTag.scan().'''
    def __init__(self, address, protocol, temperature=float('nan'),
                 humidity=float('nan'), pressure=float('nan'),
                 acceleration_x=float('nan'), acceleration_y=float('nan'),
                 acceleration_z=float('nan'),
                 battery_voltage=float('nan'), tx_power=float('nan'),
                 movement_counter=0, measurement_sequence=0):
        '''Initialize an instance of RuuviTag.
        Ususally created by RuuviTag.scan().

        Args:
            address (str): the MAC address of the RuuviTag
            protocol (int): protocol version of the message

        Keyword args:
            temperature (float): temperature. Defaults to NaN.
            humidity (float): humidity. Defaults to NaN.
            pressure (float): pressure. Defaults to NaN.
            acceleration_x (float): acceleration_x. Defaults to NaN.
            acceleration_y (float): acceleration_y. Defaults to NaN.
            acceleration_z (float): acceleration_z. Defaults to NaN.
            battery_voltage (float): battery_voltage. Defaults to NaN.
            tx_power (float): tx_power. Defaults to NaN.
            movement_counter (int): movement_counter. Defaults to NaN.
            measurement_sequence (int): measurement_sequence. Defaults to NaN.
        '''

        #: pendulum.instance: datetime of last update
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

        #: Event: event to signify movement detection
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
        '''Update the RuuviTag instance.

        Updates last_seen and sets movement_detected, if value differs from
        previous.

        Keyword args:
            temperature (float): temperature. Defaults to previous value
            humidity (float): humidity. Defaults to previous value
            pressure (float): pressure. Defaults to previous value
            acceleration_x (float): acceleration_x. Defaults to previous
                value
            acceleration_y (float): acceleration_y. Defaults to previous
                value
            acceleration_z (float): acceleration_z. Defaults to previous
                value
            battery_voltage (float): battery_voltage. Defaults to previous
                value
            tx_power (float): tx_power. Defaults to previous value
            movement_counter (int): movement_counter. Defaults to previous
                value
            measurement_sequence (int): measurement_sequence. Defaults to
                previous value
        '''

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
        '''Returns all (significant) values as a dictionary.'''
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
        '''Used to parse data received from RuuviTag.
        Currently supports versions 3 and 5 of the protocol.

        Arguments:
            address (str): MAC address of RuuviTag.
            data (bytes): received data in bytes.
        '''
        b = BitArray(bytes=data)

        # Try to find protocol version 3
        # https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-3-protocol-specification
        if b.find('0xFF990403'):
            # If it's found, parse data
            b = list(b.split('0xFF990403', count=2))[-1]
            _, humidity, temperature, temperature_fraction, pressure, \
                accel_x, accel_y, accel_z, battery_voltage = b.unpack(
                    # Ignore the packet type and manufacturer specs,
                    # as they've been handled before
                    'uint:32,' +
                    # Parse the actual payload
                    'uint:8, int:8, uint:8, uint:16,' +
                    'int:16, int:16, int:16, uint:16')

            # ... and return an instance of the calling class
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

        # Try to find protocol version 3
        # https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-5-protocol-specification
        if b.find('0xFF990405'):
            # If it's found, parse data
            b = list(b.split('0xFF990405', count=2))[-1]
            _, temperature, humidity, pressure, \
                accel_x, accel_y, accel_z, \
                battery_voltage, tx_power, \
                movement_counter, measurement_sequence, mac = b.unpack(
                    # Ignore the packet type and manufacturer specs,
                    # as they've been handled before
                    'uint:32,' +
                    # Parse the actual payload
                    'int:16, uint:16, uint:16,' +
                    'int:16, int:16, int:16,' +
                    'uint:11, uint:5,' +
                    'uint:8, uint:16, uint:48')

            # Not sure what to do with MAC at the moment?
            # Maybe compare it to the one received by btle and
            # raise an exception
            # measurement if it doesn't match?
            mac = '%x' % mac
            mac = ':'.join(mac[i:i + 2] for i in range(0, 12, 2))

            # ... and return an instance of the calling class
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
        '''Scan for RuuviTags. Yields RuuviTags as they're found.

        Keyword arguments:
                interface_index: The index of bluetooth device to use.
                    Defaults to 0
                timeout (float): Timeout for the scan. Defaults to 2.0.
        '''
        for device in btle.Scanner(interface_index).scan(timeout):
            try:
                tag = cls.parse(device.addr, device.rawData)
                if tag:
                    yield tag
            except:
                pass
