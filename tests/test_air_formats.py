"""Official Ruuvi Air format 6 and E1 vectors. No live Bluetooth."""

import math
import unittest

from ruuvitag import RuuviTag

ADDRESS = "aa:bb:cc:dd:ee:ff"

# The published E1 minimum sample has an odd number of X nibbles.
# Reserved fields are zero; measurements are the documented minimums.
# The trailing MAC is ignored by the parser.
E1_MIN = (
    "E1"
    "8001"  # temperature -163.835
    "0000"  # humidity 0
    "0000"  # pressure 500 hPa
    "0000"  # pm1.0
    "0000"  # pm2.5
    "0000"  # pm4.0
    "0000"  # pm10.0
    "0000"  # co2
    "00"  # voc
    "00"  # nox
    "000000"  # luminosity
    "000000"  # reserved
    "000000"  # measurement sequence
    "00"  # flags, calibration off
    "0000000000"  # reserved
    "000000000000"  # mac
)

NAN = float("nan")


def advert(payload_hex):
    """Payloads start at the format byte. XX is one reserved byte."""
    return bytes.fromhex("FF9904" + payload_hex.replace("XX", "00"))


class AirFormatTests(unittest.TestCase):
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

    def test_format6_valid(self):
        tag = self.parse("06170C5668C79E007000C90501D9XXCD004C884F")
        self.assertEqual(tag.protocol, 6)
        self.assert_reading(tag.temperature, 29.5)
        self.assert_reading(tag.humidity, 55.3)
        self.assert_reading(tag.pressure, 1011.02)
        self.assert_reading(tag.pm2_5, 11.2)
        self.assert_reading(tag.co2, 201)
        self.assert_reading(tag.voc, 10)
        self.assert_reading(tag.nox, 2)
        self.assert_reading(tag.luminosity, 13026.67)
        self.assert_reading(tag.measurement_sequence, 205)
        self.assertFalse(tag.calibration_in_progress)
        self.assertTrue(math.isnan(tag.pm1_0))
        self.assertTrue(math.isnan(tag.pm4_0))
        self.assertTrue(math.isnan(tag.pm10_0))

        values = tag.as_dict()
        self.assertNotIn("pm1_0", values)
        self.assertNotIn("pm4_0", values)
        self.assertNotIn("pm10_0", values)
        self.assertNotIn("movement_counter", values)
        self.assertNotIn("tx_power", values)

    def test_format6_max(self):
        tag = self.parse("067FFF9C40FFFE27109C40FAFAFEXXFF074C8F4F")
        self.assertEqual(tag.protocol, 6)
        self.assert_reading(tag.temperature, 163.835)
        self.assert_reading(tag.humidity, 100.0)
        self.assert_reading(tag.pressure, 1155.34)
        self.assert_reading(tag.pm2_5, 1000.0)
        self.assert_reading(tag.co2, 40000)
        self.assert_reading(tag.voc, 500)
        self.assert_reading(tag.nox, 500)
        self.assert_reading(tag.luminosity, 65535.0)
        self.assert_reading(tag.measurement_sequence, 255)
        self.assertTrue(tag.calibration_in_progress)

    def test_format6_min(self):
        tag = self.parse("0680010000000000000000000000XX00004C884F")
        self.assertEqual(tag.protocol, 6)
        self.assert_reading(tag.temperature, -163.835)
        self.assert_reading(tag.humidity, 0.0)
        self.assert_reading(tag.pressure, 500.0)
        self.assert_reading(tag.pm2_5, 0.0)
        self.assert_reading(tag.co2, 0)
        self.assert_reading(tag.voc, 0)
        self.assert_reading(tag.nox, 0)
        self.assert_reading(tag.luminosity, 0.0)
        self.assert_reading(tag.measurement_sequence, 0)
        self.assertFalse(tag.calibration_in_progress)

    def test_format6_invalid(self):
        tag = self.parse("068000FFFFFFFFFFFFFFFFFFFFFFXXFFFFFFFFFF")
        self.assertEqual(tag.protocol, 6)
        for value in (
            tag.temperature,
            tag.humidity,
            tag.pressure,
            tag.pm2_5,
            tag.co2,
            tag.voc,
            tag.nox,
            tag.luminosity,
        ):
            self.assertTrue(math.isnan(value))
        self.assertEqual(tag.measurement_sequence, 255)
        self.assertTrue(tag.calibration_in_progress)

    def test_format_e1_valid(self):
        tag = self.parse(
            "E1170C5668C79E0065007004BD11CA00C90A0213E0AC"
            "XXXXXXDECDEE01XXXXXXXXXXCBB8334C884F"
        )
        self.assertEqual(tag.protocol, 0xE1)
        self.assertIn("VE1", repr(tag))
        self.assert_reading(tag.temperature, 29.5)
        self.assert_reading(tag.humidity, 55.3)
        self.assert_reading(tag.pressure, 1011.02)
        self.assert_reading(tag.pm1_0, 10.1)
        self.assert_reading(tag.pm2_5, 11.2)
        self.assert_reading(tag.pm4_0, 121.3)
        self.assert_reading(tag.pm10_0, 455.4)
        self.assert_reading(tag.co2, 201)
        self.assert_reading(tag.voc, 20)
        self.assert_reading(tag.nox, 4)
        self.assert_reading(tag.luminosity, 13027.0)
        self.assert_reading(tag.measurement_sequence, 14601710)
        self.assertTrue(tag.calibration_in_progress)

        values = tag.as_dict()
        self.assertAlmostEqual(values["pm1_0"], 10.1)
        self.assertAlmostEqual(values["pm4_0"], 121.3)
        self.assertAlmostEqual(values["pm10_0"], 455.4)
        self.assertNotIn("movement_counter", values)
        self.assertNotIn("tx_power", values)

    def test_format_e1_max(self):
        tag = self.parse(
            "E17FFF9C40FFFE27102710271027109C40FAFADC28F0"
            "XXXXXXFFFFFE3FXXXXXXXXXXCBB8334C884F"
        )
        self.assertEqual(tag.protocol, 0xE1)
        self.assert_reading(tag.temperature, 163.835)
        self.assert_reading(tag.humidity, 100.0)
        self.assert_reading(tag.pressure, 1155.34)
        self.assert_reading(tag.pm1_0, 1000.0)
        self.assert_reading(tag.pm2_5, 1000.0)
        self.assert_reading(tag.pm4_0, 1000.0)
        self.assert_reading(tag.pm10_0, 1000.0)
        self.assert_reading(tag.co2, 40000)
        self.assert_reading(tag.voc, 500)
        self.assert_reading(tag.nox, 500)
        self.assert_reading(tag.luminosity, 144284.0)
        self.assert_reading(tag.measurement_sequence, 16777214)
        self.assertTrue(tag.calibration_in_progress)

    def test_format_e1_min(self):
        tag = self.parse(E1_MIN)
        self.assertEqual(tag.protocol, 0xE1)
        self.assert_reading(tag.temperature, -163.835)
        self.assert_reading(tag.humidity, 0.0)
        self.assert_reading(tag.pressure, 500.0)
        self.assert_reading(tag.pm1_0, 0.0)
        self.assert_reading(tag.pm2_5, 0.0)
        self.assert_reading(tag.pm4_0, 0.0)
        self.assert_reading(tag.pm10_0, 0.0)
        self.assert_reading(tag.co2, 0)
        self.assert_reading(tag.voc, 0)
        self.assert_reading(tag.nox, 0)
        self.assert_reading(tag.luminosity, 0.0)
        self.assert_reading(tag.measurement_sequence, 0)
        self.assertFalse(tag.calibration_in_progress)

    def test_format_e1_invalid(self):
        tag = self.parse(
            "E18000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
            "XXXXXXFFFFFFFEXXXXXXXXXXFFFFFFFFFFFF"
        )
        self.assertEqual(tag.protocol, 0xE1)
        for value in (
            tag.temperature,
            tag.humidity,
            tag.pressure,
            tag.pm1_0,
            tag.pm2_5,
            tag.pm4_0,
            tag.pm10_0,
            tag.co2,
            tag.voc,
            tag.nox,
            tag.luminosity,
            tag.measurement_sequence,
        ):
            self.assertTrue(math.isnan(value))
        self.assertFalse(tag.calibration_in_progress)


if __name__ == "__main__":
    unittest.main()
