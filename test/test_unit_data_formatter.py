# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock

from xhoundpi.direction import (Direction,
                               CoordAxis)
from xhoundpi.data_formatter import (NMEADataFormatter,
                                    UBXDataFormatter)

class test_NMEADataFormatter(unittest.TestCase):

    # degmins_to_decdeg

    def test_degmins_to_decdeg_N(self):
        # NOTE this test case does not really verify
        # the conversion for it will be provided from the
        # NMEA library through a functor. We only test that
        # the functor is called with the appropiate arguments
        # and the sign is applied according to direction.
        # See test_unit_proto_parser_libs.py for the actual value test
        degmins_to_decdeg = unittest.mock.Mock(return_value=0.6)
        converter = NMEADataFormatter(degmins_to_decdeg)

        self.assertEqual(converter.degmins_to_decdeg('12319.943281', Direction.N), 0.6)
        degmins_to_decdeg.assert_called_once_with('12319.943281')
        self.assertEqual(converter.degmins_to_decdeg('12319.943281', Direction.S), -0.6)
        degmins_to_decdeg.assert_called_with('12319.943281')
        self.assertEqual(converter.degmins_to_decdeg('12319.943281', Direction.E), 0.6)
        degmins_to_decdeg.assert_called_with('12319.943281')
        self.assertEqual(converter.degmins_to_decdeg('12319.943281', Direction.W), -0.6)
        degmins_to_decdeg.assert_called_with('12319.943281')

    # decdeg_to_degmins (errors)

    def test_decdeg_to_degmins_should_fail_if_degs_higher_than_number_of_digits(self):
        converter = NMEADataFormatter(None)
        with self.assertRaises(ValueError) as context:
            converter.decdeg_to_degmins(123.3323880166666667, CoordAxis.LAT)
        self.assertEqual('Too many digits in decimal degrees result',
            str(context.exception))
        converter.decdeg_to_degmins(23.3323880166666667, CoordAxis.LAT)
        converter.decdeg_to_degmins(123.3323880166666667, CoordAxis.LON)

    # decdeg_to_degmins longitude (3 degree digits)

    def test_decdeg_to_degmins_longitude(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(123.3323880166666667, CoordAxis.LON)
        self.assertEqual(result, ('12319.94328', Direction.E))

    def test_decdeg_to_degmins_longitude_leading_zeros_degs(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(0.3323880166666667, CoordAxis.LON)
        self.assertEqual(result, ('00019.94328', Direction.E))

    def test_decdeg_to_degmins_longitude_leading_zeros_mins(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(123.0, CoordAxis.LON)
        self.assertEqual(result, ('12300.00000', Direction.E))

    def test_decdeg_to_degmins_longitude_zero(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(0., CoordAxis.LON)
        self.assertEqual(result, ('00000.00000', Direction.E))

    def test_decdeg_to_degmins_longitude_hipres(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(123.3323880166666667, CoordAxis.LON, hipres=True)
        self.assertEqual(result, ('12319.9432810', Direction.E))

    # decdeg_to_degmins latitude (2 degree digits)

    def test_decdeg_to_degmins_latitude(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(23.3323880166666667, CoordAxis.LAT)
        self.assertEqual(result, ('2319.94328', Direction.N))

    def test_decdeg_to_degmins_latitude_leading_zeros_degs(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(0.3323880166666667, CoordAxis.LAT)
        self.assertEqual(result, ('0019.94328', Direction.N))

    def test_decdeg_to_degmins_latitude_leading_zeros_mins(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(23.0, CoordAxis.LAT)
        self.assertEqual(result, ('2300.00000', Direction.N))

    def test_decdeg_to_degmins_latitude_zero(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(0., CoordAxis.LAT)
        self.assertEqual(result, ('0000.00000', Direction.N))

    def test_decdeg_to_degmins_latitude_negative(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(-0.000001, CoordAxis.LAT)
        self.assertEqual(result, ('0000.00006', Direction.S))

    def test_decdeg_to_degmins_latitude_hipres(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(23.3323880166666667, CoordAxis.LAT, hipres=True)
        self.assertEqual(result, ('2319.9432810', Direction.N))

    def test_decdeg_to_degmins_latitude_negative_high_pres(self):
        converter = NMEADataFormatter(None)
        result = converter.decdeg_to_degmins(-0.00000001, CoordAxis.LAT, hipres=True)
        self.assertEqual(result, ('0000.0000006', Direction.S))

class test_UBXDataFormatter(unittest.TestCase):

    def test_integer_to_decdeg(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(123456789)
        self.assertEqual(result, 12.3456789)

    def test_integer_to_decdeg_hires(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(1234567891, 12)
        self.assertEqual(result, 123.456789112)

    def test_decdeg_to_integer(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(123.1234567)
        self.assertEqual(result, (1231234567, 00))

    def test_decdeg_to_integer_hires(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(123.123456789)
        self.assertEqual(result, (1231234567, 89))

    def test_decdeg_to_integer_hires_excess_dropped(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(123.1234567899)
        self.assertEqual(result, (1231234567, 89))

    def test_decdeg_to_integer_negative(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(-123.1234567)
        self.assertEqual(result, (-1231234567, 00))

    def test_decdeg_to_integer_negative_hires(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(-123.1234567899)
        self.assertEqual(result, (-1231234567, -89))

    def test_decdeg_to_integer_zero(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(0.)
        self.assertEqual(result, (0, 00))
