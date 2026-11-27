"""Official RAWv1 (format 3) and RAWv2 (format 5) vectors. No live Bluetooth."""

import math
import sys
import unittest

from ruuvitag import RuuviDaemon, RuuviTag

ADDRESS = "aa:bb:cc:dd:ee:ff"


def advert(payload_hex):
    """Payloads start at the format byte."""
    return bytes.fromhex("FF9904" + payload_hex)


class ImportTests(unittest.TestCase):
    def test_import_does_not_load_bluepy(self):
        loaded = [
            name
            for name in sys.modules
            if name == "bluepy" or name.startswith("bluepy.")
        ]
        self.assertEqual(loaded, [])
        self.assertTrue(callable(RuuviTag.scan))
        self.assertTrue(callable(RuuviDaemon.run))


class RawFormatTests(unittest.TestCase):
    def parse(self, payload_hex):
        tag = RuuviTag.parse(ADDRESS, advert(payload_hex))
        self.assertIsNotNone(tag)
        self.assertEqual(tag.address, ADDRESS)
        return tag

    def assert_reading(self, actual, expected):
        if isinstance(expected, float) and math.isnan(expected):
            self.assertTrue(math.isnan(actual))
            return
        if isinstance(expected, float):
            self.assertAlmostEqual(actual, expected)
            return
        self.assertEqual(actual, expected)

    def test_format3_valid(self):
        tag = self.parse("03291A1ECE1EFC18F94202CA0B53")
        self.assertEqual(tag.protocol, 3)
        self.assert_reading(tag.temperature, 26.3)
        self.assert_reading(tag.humidity, 20.5)
        self.assert_reading(tag.pressure, 1027.66)
        self.assert_reading(tag.acceleration_x, -1.0)
        self.assert_reading(tag.acceleration_y, -1.726)
        self.assert_reading(tag.acceleration_z, 0.714)
        self.assert_reading(tag.battery_voltage, 2.899)

    def test_format3_max(self):
        tag = self.parse("03FF7F63FFFF7FFF7FFF7FFFFFFF")
        self.assertEqual(tag.protocol, 3)
        self.assert_reading(tag.temperature, 127.99)
        self.assert_reading(tag.humidity, 127.5)
        self.assert_reading(tag.pressure, 1155.35)
        self.assert_reading(tag.acceleration_x, 32.767)
        self.assert_reading(tag.acceleration_y, 32.767)
        self.assert_reading(tag.acceleration_z, 32.767)
        self.assert_reading(tag.battery_voltage, 65.535)

    def test_format3_min(self):
        tag = self.parse("0300FF6300008001800180010000")
        self.assertEqual(tag.protocol, 3)
        self.assert_reading(tag.temperature, -127.99)
        self.assert_reading(tag.humidity, 0.0)
        self.assert_reading(tag.pressure, 500.0)
        self.assert_reading(tag.acceleration_x, -32.767)
        self.assert_reading(tag.acceleration_y, -32.767)
        self.assert_reading(tag.acceleration_z, -32.767)
        self.assert_reading(tag.battery_voltage, 0.0)

    def test_format5_valid(self):
        tag = self.parse("0512FC5394C37C0004FFFC040CAC364200CDCBB8334C884F")
        self.assertEqual(tag.protocol, 5)
        self.assert_reading(tag.temperature, 24.3)
        self.assert_reading(tag.humidity, 53.49)
        self.assert_reading(tag.pressure, 1000.44)
        self.assert_reading(tag.acceleration_x, 0.004)
        self.assert_reading(tag.acceleration_y, -0.004)
        self.assert_reading(tag.acceleration_z, 1.036)
        self.assert_reading(tag.battery_voltage, 2.977)
        self.assert_reading(tag.tx_power, 4.0)
        self.assertEqual(tag.movement_counter, 66)
        self.assertEqual(tag.measurement_sequence, 205)
        values = tag.as_dict()
        self.assertEqual(values["movement_counter"], 66)
        self.assertEqual(values["tx_power"], 4)

    def test_format5_max(self):
        tag = self.parse("057FFFFFFEFFFE7FFF7FFF7FFFFFDEFEFFFECBB8334C884F")
        self.assertEqual(tag.protocol, 5)
        self.assert_reading(tag.temperature, 163.835)
        self.assert_reading(tag.humidity, 163.835)
        self.assert_reading(tag.pressure, 1155.34)
        self.assert_reading(tag.acceleration_x, 32.767)
        self.assert_reading(tag.acceleration_y, 32.767)
        self.assert_reading(tag.acceleration_z, 32.767)
        self.assert_reading(tag.battery_voltage, 3.646)
        self.assert_reading(tag.tx_power, 20.0)
        self.assertEqual(tag.movement_counter, 254)
        self.assertEqual(tag.measurement_sequence, 65534)

    def test_format5_min(self):
        tag = self.parse("058001000000008001800180010000000000CBB8334C884F")
        self.assertEqual(tag.protocol, 5)
        self.assert_reading(tag.temperature, -163.835)
        self.assert_reading(tag.humidity, 0.0)
        self.assert_reading(tag.pressure, 500.0)
        self.assert_reading(tag.acceleration_x, -32.767)
        self.assert_reading(tag.acceleration_y, -32.767)
        self.assert_reading(tag.acceleration_z, -32.767)
        self.assert_reading(tag.battery_voltage, 1.6)
        self.assert_reading(tag.tx_power, -40.0)
        self.assertEqual(tag.movement_counter, 0)
        self.assertEqual(tag.measurement_sequence, 0)

    def test_format5_invalid(self):
        tag = self.parse("058000FFFFFFFF800080008000FFFFFFFFFFFFFFFFFFFFFF")
        self.assertEqual(tag.protocol, 5)
        for value in (
            tag.temperature,
            tag.humidity,
            tag.pressure,
            tag.acceleration_x,
            tag.acceleration_y,
            tag.acceleration_z,
            tag.battery_voltage,
            tag.tx_power,
            tag.movement_counter,
            tag.measurement_sequence,
        ):
            self.assertTrue(math.isnan(value))


if __name__ == "__main__":
    unittest.main()
