import math

import arrow
from threading import Event

from bitstring import BitArray


class RuuviTag(object):
    """An instance of RuuviTag. Usually created by RuuviTag.scan()."""

    def __init__(
        self,
        address,
        protocol,
        temperature=float("nan"),
        humidity=float("nan"),
        pressure=float("nan"),
        acceleration_x=float("nan"),
        acceleration_y=float("nan"),
        acceleration_z=float("nan"),
        battery_voltage=float("nan"),
        tx_power=float("nan"),
        movement_counter=0,
        measurement_sequence=0,
        pm1_0=float("nan"),
        pm2_5=float("nan"),
        pm4_0=float("nan"),
        pm10_0=float("nan"),
        co2=float("nan"),
        voc=float("nan"),
        nox=float("nan"),
        luminosity=float("nan"),
        calibration_in_progress=None,
    ):
        """Initialize an instance of RuuviTag.
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
            pm1_0 (float): pm1_0. Defaults to NaN.
            pm2_5 (float): pm2_5. Defaults to NaN.
            pm4_0 (float): pm4_0. Defaults to NaN.
            pm10_0 (float): pm10_0. Defaults to NaN.
            co2 (int): co2. Defaults to NaN.
            voc (int): voc. Defaults to NaN.
            nox (int): nox. Defaults to NaN.
            luminosity (float): luminosity. Defaults to NaN.
            calibration_in_progress (bool): calibration_in_progress.
                Defaults to None.
        """

        self.last_seen = arrow.utcnow()
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
        self.pm1_0 = pm1_0
        self.pm2_5 = pm2_5
        self.pm4_0 = pm4_0
        self.pm10_0 = pm10_0
        self.co2 = co2
        self.voc = voc
        self.nox = nox
        self.luminosity = luminosity
        self.calibration_in_progress = calibration_in_progress

        #: Event: event to signify movement detection
        self.movement_detected = Event()

    def __repr__(self):
        # Format E1 is stored as 0xE1 (225). Print the spec name.
        protocol = "E1" if self.protocol == 0xE1 else self.protocol
        return "<RuuviTag V%s %s %.02fc, %.02f%%, %s>" % (
            protocol,
            self.address,
            self.temperature,
            self.humidity,
            self.last_seen.isoformat(),
        )

    def update(
        self,
        temperature=None,
        humidity=None,
        pressure=None,
        acceleration_x=None,
        acceleration_y=None,
        acceleration_z=None,
        battery_voltage=None,
        tx_power=None,
        movement_counter=None,
        measurement_sequence=None,
        pm1_0=None,
        pm2_5=None,
        pm4_0=None,
        pm10_0=None,
        co2=None,
        voc=None,
        nox=None,
        luminosity=None,
        calibration_in_progress=None,
        **kwargs
    ):
        """Update the RuuviTag instance.

        Updates last_seen. Sets movement_detected when a movement_counter
        is passed and the value differs from previous. Formats without a
        counter (6 and E1) leave the counter and the event unchanged.

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
            pm1_0 (float): pm1_0. Defaults to previous value
            pm2_5 (float): pm2_5. Defaults to previous value
            pm4_0 (float): pm4_0. Defaults to previous value
            pm10_0 (float): pm10_0. Defaults to previous value
            co2 (int): co2. Defaults to previous value
            voc (int): voc. Defaults to previous value
            nox (int): nox. Defaults to previous value
            luminosity (float): luminosity. Defaults to previous value
            calibration_in_progress (bool): calibration_in_progress.
                Defaults to previous value
        """

        self.last_seen = arrow.utcnow()

        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.acceleration_z = acceleration_z
        self.battery_voltage = battery_voltage
        self.tx_power = tx_power
        self.measurement_sequence = measurement_sequence
        self.pm1_0 = pm1_0
        self.pm2_5 = pm2_5
        self.pm4_0 = pm4_0
        self.pm10_0 = pm10_0
        self.co2 = co2
        self.voc = voc
        self.nox = nox
        self.luminosity = luminosity
        self.calibration_in_progress = calibration_in_progress

        # None and NaN mean this packet has no counter. NaN != NaN,
        # so a missing counter must not be stored or treated as motion.
        if movement_counter is not None and not (
            isinstance(movement_counter, float) and math.isnan(movement_counter)
        ):
            if movement_counter != self.movement_counter:
                self.movement_detected.set()

            self.movement_counter = movement_counter

    def as_dict(self):
        """Returns all (significant) values as a dictionary.

        Core readings are always included. Protocol 5 also includes
        tx_power, movement_counter and measurement_sequence. Protocol 6
        also includes pm2_5, co2, voc, nox, luminosity,
        measurement_sequence and calibration_in_progress. Protocol E1
        includes those plus pm1_0, pm4_0 and pm10_0.
        """
        values = {
            "address": self.address,
            "protocol": self.protocol,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "acceleration_x": self.acceleration_x,
            "acceleration_y": self.acceleration_y,
            "acceleration_z": self.acceleration_z,
            "battery_voltage": self.battery_voltage,
            "last_seen": self.last_seen,
        }
        if self.protocol == 5:
            values.update(
                {
                    "tx_power": self.tx_power,
                    "movement_counter": self.movement_counter,
                    "measurement_sequence": self.measurement_sequence,
                }
            )
        elif self.protocol in (6, 0xE1):
            values.update(
                {
                    "pm2_5": self.pm2_5,
                    "co2": self.co2,
                    "voc": self.voc,
                    "nox": self.nox,
                    "luminosity": self.luminosity,
                    "measurement_sequence": self.measurement_sequence,
                    "calibration_in_progress": self.calibration_in_progress,
                }
            )
            if self.protocol == 0xE1:
                values.update(
                    {
                        "pm1_0": self.pm1_0,
                        "pm4_0": self.pm4_0,
                        "pm10_0": self.pm10_0,
                    }
                )
        return values

    @classmethod
    def parse(cls, address, data):
        """Used to parse data received from RuuviTag.
        Currently supports versions 3, 5, 6 and E1 of the protocol.

        Arguments:
            address (str): MAC address of RuuviTag.
            data (bytes): received data in bytes.
        """
        b = BitArray.from_bytes(data)

        # Try to find protocol version 3
        # https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-3-protocol-specification
        # bitstring 5+: find() returns int | None (bit 0 is a valid match)
        if b.find("0xFF990403") is not None:
            # If it's found, parse data
            b = list(b.split("0xFF990403", count=2))[-1]
            (
                _,
                humidity,
                temperature_sign,
                temperature,
                temperature_fraction,
                pressure,
                accel_x,
                accel_y,
                accel_z,
                battery_voltage,
            ) = b.unpack(
                # Ignore the packet type and manufacturer specs,
                # as they've been handled before
                "uint:32,"
                +
                # Parse the actual payload
                "uint:8, int:1, uint:7, uint:8, uint:16,"
                + "int:16, int:16, int:16, uint:16"
            )

            temperature_sign = -1 if temperature_sign == -1 else 1

            # ... and return an instance of the calling class
            return cls(
                address,
                3,
                temperature=temperature_sign
                * (float(temperature) + temperature_fraction / 100.0),
                humidity=humidity / 2.0,
                pressure=(pressure + 50000) / 100.0,
                acceleration_x=accel_x / 1000.0,
                acceleration_y=accel_y / 1000.0,
                acceleration_z=accel_z / 1000.0,
                battery_voltage=battery_voltage / 1000.0,
            )

        # Try to find protocol version 5
        # https://github.com/ruuvi/ruuvi-sensor-protocols#data-format-5-protocol-specification
        if b.find("0xFF990405") is not None:
            # If it's found, parse data
            b = list(b.split("0xFF990405", count=2))[-1]
            (
                _,
                temperature,
                humidity,
                pressure,
                accel_x,
                accel_y,
                accel_z,
                battery_voltage,
                tx_power,
                movement_counter,
                measurement_sequence,
                mac,
            ) = b.unpack(
                # Ignore the packet type and manufacturer specs,
                # as they've been handled before
                "uint:32,"
                +
                # Parse the actual payload
                "int:16, uint:16, uint:16,"
                + "int:16, int:16, int:16,"
                + "uint:11, uint:5,"
                + "uint:8, uint:16, uint:48"
            )

            # Not sure what to do with MAC at the moment?
            # Maybe compare it to the one received by btle and
            # raise an exception if doesn't match?
            mac = "%x" % mac
            mac = ":".join(mac[i : i + 2] for i in range(0, 12, 2))

            # Most-negative signed and all-bits unsigned mean not available.
            # Payload MAC is ignored.
            if temperature == -32768:
                temperature = float("nan")
            else:
                temperature = float(temperature) * 0.005

            if humidity == 0xFFFF:
                humidity = float("nan")
            else:
                humidity = humidity * 0.0025

            if pressure == 0xFFFF:
                pressure = float("nan")
            else:
                pressure = (pressure + 50000) / 100.0

            if accel_x == -32768:
                accel_x = float("nan")
            else:
                accel_x = accel_x / 1000.0

            if accel_y == -32768:
                accel_y = float("nan")
            else:
                accel_y = accel_y / 1000.0

            if accel_z == -32768:
                accel_z = float("nan")
            else:
                accel_z = accel_z / 1000.0

            # 11 bits above 1.6 V. 2047 is not available.
            if battery_voltage == 0x7FF:
                battery_voltage = float("nan")
            else:
                battery_voltage = (battery_voltage + 1600) / 1000.0

            # 5 bits, 2 dBm steps above -40 dBm. 31 is not available.
            if tx_power == 0x1F:
                tx_power = float("nan")
            else:
                tx_power = -40 + (tx_power * 2)

            if movement_counter == 0xFF:
                movement_counter = float("nan")

            if measurement_sequence == 0xFFFF:
                measurement_sequence = float("nan")

            # ... and return an instance of the calling class
            return cls(
                address,
                5,
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                acceleration_x=accel_x,
                acceleration_y=accel_y,
                acceleration_z=accel_z,
                battery_voltage=battery_voltage,
                tx_power=tx_power,
                movement_counter=movement_counter,
                measurement_sequence=measurement_sequence,
            )

        # Try to find protocol version 6
        # https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-6
        if b.find("0xFF990406") is not None:
            # If it's found, parse data
            b = list(b.split("0xFF990406", count=2))[-1]
            (
                _,
                temperature,
                humidity,
                pressure,
                pm2_5,
                co2,
                voc_byte,
                nox_byte,
                luminosity,
                _,
                measurement_sequence,
                flags,
                _,
            ) = b.unpack(
                # Ignore the packet type and manufacturer specs,
                # as they've been handled before
                "uint:32,"
                +
                # Parse the actual payload
                "int:16, uint:16, uint:16,"
                + "uint:16, uint:16,"
                + "uint:8, uint:8, uint:8, uint:8,"
                + "uint:8, uint:8, uint:24"
            )

            # Most-negative signed and all-bits unsigned mean not available.
            # Payload MAC is ignored, same as format 5.
            if temperature == -32768:
                temperature = float("nan")
            else:
                temperature = float(temperature) * 0.005

            if humidity == 0xFFFF:
                humidity = float("nan")
            else:
                humidity = humidity * 0.0025

            if pressure == 0xFFFF:
                pressure = float("nan")
            else:
                pressure = (pressure + 50000) / 100.0

            if pm2_5 == 0xFFFF:
                pm2_5 = float("nan")
            else:
                pm2_5 = pm2_5 / 10.0

            if co2 == 0xFFFF:
                co2 = float("nan")

            # LSB of the 9-bit index lives in the flags byte.
            voc = (voc_byte << 1) | ((flags >> 6) & 1)
            nox = (nox_byte << 1) | ((flags >> 7) & 1)
            if voc == 0x1FF:
                voc = float("nan")
            if nox == 0x1FF:
                nox = float("nan")

            # 8-bit logarithmic lux. Code 255 is not available.
            if luminosity == 0xFF:
                luminosity = float("nan")
            else:
                luminosity = round(
                    math.exp(luminosity * math.log(65536) / 254) - 1, 2
                )

            # ... and return an instance of the calling class
            return cls(
                address,
                6,
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                pm2_5=pm2_5,
                co2=co2,
                voc=voc,
                nox=nox,
                luminosity=luminosity,
                measurement_sequence=measurement_sequence,
                calibration_in_progress=bool(flags & 1),
            )

        # Try to find protocol version E1
        # https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-e1
        if b.find("0xFF9904E1") is not None:
            # If it's found, parse data
            b = list(b.split("0xFF9904E1", count=2))[-1]
            (
                _,
                temperature,
                humidity,
                pressure,
                pm1_0,
                pm2_5,
                pm4_0,
                pm10_0,
                co2,
                voc_byte,
                nox_byte,
                luminosity,
                _,
                _,
                _,
                measurement_sequence,
                flags,
                _,
                _,
            ) = b.unpack(
                # Ignore the packet type and manufacturer specs,
                # as they've been handled before
                "uint:32,"
                +
                # Parse the actual payload
                "int:16, uint:16, uint:16,"
                + "uint:16, uint:16, uint:16, uint:16,"
                + "uint:16, uint:8, uint:8, uint:24,"
                + "uint:8, uint:8, uint:8,"
                + "uint:24, uint:8, uint:40, uint:48"
            )

            # Most-negative signed and all-bits unsigned mean not available.
            # Payload MAC is ignored, same as format 5.
            if temperature == -32768:
                temperature = float("nan")
            else:
                temperature = float(temperature) * 0.005

            if humidity == 0xFFFF:
                humidity = float("nan")
            else:
                humidity = humidity * 0.0025

            if pressure == 0xFFFF:
                pressure = float("nan")
            else:
                pressure = (pressure + 50000) / 100.0

            if pm1_0 == 0xFFFF:
                pm1_0 = float("nan")
            else:
                pm1_0 = pm1_0 / 10.0

            if pm2_5 == 0xFFFF:
                pm2_5 = float("nan")
            else:
                pm2_5 = pm2_5 / 10.0

            if pm4_0 == 0xFFFF:
                pm4_0 = float("nan")
            else:
                pm4_0 = pm4_0 / 10.0

            if pm10_0 == 0xFFFF:
                pm10_0 = float("nan")
            else:
                pm10_0 = pm10_0 / 10.0

            if co2 == 0xFFFF:
                co2 = float("nan")

            # LSB of the 9-bit index lives in the flags byte.
            voc = (voc_byte << 1) | ((flags >> 6) & 1)
            nox = (nox_byte << 1) | ((flags >> 7) & 1)
            if voc == 0x1FF:
                voc = float("nan")
            if nox == 0x1FF:
                nox = float("nan")

            # 24-bit lux in 0.01 steps. All bits set is not available.
            if luminosity == 0xFFFFFF:
                luminosity = float("nan")
            else:
                luminosity = luminosity / 100.0

            # 24-bit counter. All bits set is not available.
            if measurement_sequence == 0xFFFFFF:
                measurement_sequence = float("nan")

            # ... and return an instance of the calling class
            return cls(
                address,
                0xE1,
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                pm1_0=pm1_0,
                pm2_5=pm2_5,
                pm4_0=pm4_0,
                pm10_0=pm10_0,
                co2=co2,
                voc=voc,
                nox=nox,
                luminosity=luminosity,
                measurement_sequence=measurement_sequence,
                calibration_in_progress=bool(flags & 1),
            )

    @classmethod
    def scan(cls, interface_index=0, timeout=2):
        """Scan for RuuviTags. Yields RuuviTags as they're found.

        Keyword arguments:
                interface_index: The index of bluetooth device to use.
                    Defaults to 0
                timeout (float): Timeout for the scan. Defaults to 2.0.
        """
        # Imported here so parse() and the unit tests do not need bluepy.
        from bluepy import btle

        for device in btle.Scanner(interface_index).scan(timeout):
            try:
                tag = cls.parse(device.addr, device.rawData)
                if tag:
                    yield tag
            except:
                pass
