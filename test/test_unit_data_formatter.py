# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock

from decimal import Decimal

from xhoundpi.direction import Direction, CoordAxis
from xhoundpi.data_formatter import NMEADataFormatter, UBXDataFormatter
from xhoundpi.decimal_math import setup_common_decimal_context

setup_common_decimal_context()

class test_NMEADataFormatter(unittest.TestCase): # pylint: disable=too-many-public-methods

    # degmins_to_decdeg

    def test_degmins_to_decdeg_0_or_None(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0', Direction.N),  Decimal(  '0'))
        self.assertEqual(converter.degmins_to_decdeg(None, Direction.S),  Decimal( '0'))

    def test_degmins_to_decdeg_and_direction_sign(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('1212.12345', Direction.N),  Decimal(  '12.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('1212.12345', Direction.S),  Decimal( '-12.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('12312.12345', Direction.E), Decimal( '123.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('12312.12345', Direction.W), Decimal('-123.2020575'))

    def test_degmins_to_decdeg_and_direction_sign_hires_inexact(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('1212.1234567', Direction.N),  Decimal(  '12.2020576116666666666667'))
        self.assertEqual(converter.degmins_to_decdeg('1212.1234567', Direction.S),  Decimal( '-12.2020576116666666666667'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234567', Direction.E), Decimal( '123.202057611666666666667'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234567', Direction.W), Decimal('-123.202057611666666666667'))

    def test_degmins_to_decdeg_and_direction_sign_hires_inexact_below_half_norounding(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('1212.1234565', Direction.N),  Decimal(  '12.2020576083333333333333'))
        self.assertEqual(converter.degmins_to_decdeg('1212.1234565', Direction.S),  Decimal( '-12.2020576083333333333333'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234565', Direction.E), Decimal( '123.202057608333333333333'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234565', Direction.W), Decimal('-123.202057608333333333333'))

    def test_degmins_to_decdeg_inexact_24res(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0004.00000', Direction.N),  Decimal('0.0666666666666666666666667'))

    def test_degmins_to_decdeg_zero(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.00000', Direction.N),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('0000.00000', Direction.S),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00000', Direction.E),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00000', Direction.W),  Decimal('0'))

    def test_degmins_to_decdeg_near_zero(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.00001', Direction.N),  Decimal('1.66666666666666666666667E-7'))
        self.assertEqual(converter.degmins_to_decdeg('0000.00001', Direction.S),  Decimal('-1.66666666666666666666667E-7'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00001', Direction.E),  Decimal('1.66666666666666666666667E-7'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00001', Direction.W),  Decimal('-1.66666666666666666666667E-7'))

    def test_degmins_to_decdeg_near_zero_hires(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.0000001', Direction.N),  Decimal('1.66666666666666666666667E-9'))
        self.assertEqual(converter.degmins_to_decdeg('0000.0000001', Direction.S),  Decimal('-1.66666666666666666666667E-9'))
        self.assertEqual(converter.degmins_to_decdeg('00000.0000001', Direction.E),  Decimal('1.66666666666666666666667E-9'))
        self.assertEqual(converter.degmins_to_decdeg('00000.0000001', Direction.W),  Decimal('-1.66666666666666666666667E-9'))

    def test_degmins_to_decdeg_max(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('9999.99999', Direction.N),  Decimal('100.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('9999.99999', Direction.S),  Decimal('-100.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.99999', Direction.E), Decimal('1000.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.99999', Direction.W), Decimal('-1000.6666665'))

    def test_degmins_to_decdeg_max_hires(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('9999.9999999', Direction.N),  Decimal('100.666666665'))
        self.assertEqual(converter.degmins_to_decdeg('9999.9999999', Direction.S),  Decimal('-100.666666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.9999999', Direction.E),  Decimal('1000.666666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.9999999', Direction.W),  Decimal('-1000.666666665'))

    # decdeg_to_degmins (errors)

    def test_decdeg_to_degmins_should_fail_if_degs_higher_than_number_of_digits(self):
        converter = NMEADataFormatter()
        with self.assertRaises(ValueError) as context:
            converter.decdeg_to_degmins(Decimal('123.3323880166666667'), CoordAxis.LAT)
        self.assertEqual('Too many digits in decimal degrees result',
            str(context.exception))
        with self.assertRaises(ValueError) as context:
            converter.decdeg_to_degmins(Decimal('1234.3323880166666667'), CoordAxis.LON)
        self.assertEqual('Too many digits in decimal degrees result',
            str(context.exception))
        converter.decdeg_to_degmins(Decimal('23.3323880166666667'), CoordAxis.LAT)
        converter.decdeg_to_degmins(Decimal('123.3323880166666667'), CoordAxis.LON)

    # decdeg_to_degmins longitude (3 degree digits)

    def test_decdeg_to_degmins_longitude(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('123.3323880166666667'), CoordAxis.LON)
        self.assertEqual(result, ('12319.94328', Direction.E))

    def test_decdeg_to_degmins_longitude_leading_zeros_degs(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('0.3323880166666667'), CoordAxis.LON)
        self.assertEqual(result, ('00019.94328', Direction.E))

    def test_decdeg_to_degmins_longitude_leading_zeros_mins(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('123.0'), CoordAxis.LON)
        self.assertEqual(result, ('12300.00000', Direction.E))

    def test_decdeg_to_degmins_longitude_zero(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('0'), CoordAxis.LON)
        self.assertEqual(result, ('00000.00000', Direction.E))

    def test_decdeg_to_degmins_longitude_hipres(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('123.3323880166666667'), CoordAxis.LON, hipres=True)
        self.assertEqual(result, ('12319.9432810', Direction.E))

    # decdeg_to_degmins latitude (2 degree digits)

    def test_decdeg_to_degmins_latitude(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('23.3323880166666667'), CoordAxis.LAT)
        self.assertEqual(result, ('2319.94328', Direction.N))

    def test_decdeg_to_degmins_latitude_leading_zeros_degs(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('0.3323880166666667'), CoordAxis.LAT)
        self.assertEqual(result, ('0019.94328', Direction.N))

    def test_decdeg_to_degmins_latitude_leading_zeros_mins(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('23.0'), CoordAxis.LAT)
        self.assertEqual(result, ('2300.00000', Direction.N))

    def test_decdeg_to_degmins_latitude_zero(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('0'), CoordAxis.LAT)
        self.assertEqual(result, ('0000.00000', Direction.N))

    def test_decdeg_to_degmins_latitude_negative(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('-0.000001'), CoordAxis.LAT)
        self.assertEqual(result, ('0000.00006', Direction.S))

    def test_decdeg_to_degmins_latitude_hipres(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('23.3323880166666667'), CoordAxis.LAT, hipres=True)
        self.assertEqual(result, ('2319.9432810', Direction.N))

    def test_decdeg_to_degmins_latitude_negative_high_pres(self):
        converter = NMEADataFormatter()
        result = converter.decdeg_to_degmins(Decimal('-0.00000001'), CoordAxis.LAT, hipres=True)
        self.assertEqual(result, ('0000.0000006', Direction.S))

    # height conversions

    def test_height_field_m_to_height_mm(self):
        converter = NMEADataFormatter()
        self.assertEqual(Decimal('1000'), converter.height_field_m_to_height_mm('1'))
        self.assertEqual(Decimal('0'), converter.height_field_m_to_height_mm('0'))
        self.assertEqual(Decimal('1'), converter.height_field_m_to_height_mm('0.001'))

    def test_height_field_to_height_mm(self):
        converter = NMEADataFormatter()
        self.assertEqual('1000.000', converter.height_mm_to_height_field_m(Decimal('1000000')))
        self.assertEqual('0.000', converter.height_mm_to_height_field_m(Decimal('0')))
        self.assertEqual('0.001', converter.height_mm_to_height_field_m(Decimal('1')))

    # is_highpres

    def test_degmins_to_decdeg_is_highpres(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.is_highpres('9999.9999'),  False)
        self.assertEqual(converter.is_highpres('9999.99999'),  False)
        self.assertEqual(converter.is_highpres('9999.999999'),  False)
        self.assertEqual(converter.is_highpres('9999.9999999'),  True)
        self.assertEqual(converter.is_highpres('9999.99999999'),  True)
        self.assertEqual(converter.is_highpres('999.99999999'),  True)
        self.assertEqual(converter.is_highpres('99.99999999'),  True)
        self.assertEqual(converter.is_highpres('9.99999999'),  True)
        self.assertEqual(converter.is_highpres('.99999999'),  True)

    def test_round_trip(self):
        converter = NMEADataFormatter()
        decdeg = converter.degmins_to_decdeg('4916.45000', Direction.N)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT)
        self.assertEqual(('4916.45000', Direction.N), degmin)

    def test_round_trip_zero(self):
        converter = NMEADataFormatter()
        decdeg = converter.degmins_to_decdeg('0000.00000', Direction.N)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT)
        self.assertEqual(('0000.00000', Direction.N), degmin)

    def test_round_trip_near_zero(self):
        converter = NMEADataFormatter()
        decdeg = converter.degmins_to_decdeg('0000.00001', Direction.N)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT)
        self.assertEqual(('0000.00001', Direction.N), degmin)
        decdeg = converter.degmins_to_decdeg('0000.00001', Direction.S)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT)
        self.assertEqual(('0000.00001', Direction.S), degmin)
        decdeg = converter.degmins_to_decdeg('00000.00001', Direction.E)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LON)
        self.assertEqual(('00000.00001', Direction.E), degmin)
        decdeg = converter.degmins_to_decdeg('00000.00001', Direction.W)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LON)
        self.assertEqual(('00000.00001', Direction.W), degmin)

    def test_round_trip_near_zero_hires(self):
        converter = NMEADataFormatter()
        decdeg = converter.degmins_to_decdeg('0000.0000001', Direction.N)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT, hipres=True)
        self.assertEqual(('0000.0000001', Direction.N), degmin)
        decdeg = converter.degmins_to_decdeg('0000.0000001', Direction.S)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LAT, hipres=True)
        self.assertEqual(('0000.0000001', Direction.S), degmin)
        decdeg = converter.degmins_to_decdeg('00000.0000001', Direction.E)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LON, hipres=True)
        self.assertEqual(('00000.0000001', Direction.E), degmin)
        decdeg = converter.degmins_to_decdeg('00000.0000001', Direction.W)
        degmin = converter.decdeg_to_degmins(decdeg, CoordAxis.LON, hipres=True)
        self.assertEqual(('00000.0000001', Direction.W), degmin)

class test_UBXDataFormatter(unittest.TestCase):

    # ubx lat/lon integer field -> decimal degrees

    def test_integer_to_decdeg(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(123456789)
        self.assertEqual(result, Decimal('12.345678900'))

    def test_integer_to_decdeg_hires(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(1234567891, 12)
        self.assertEqual(result, Decimal('123.456789112'))

    def test_integer_to_decdeg_zero(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(0, 0)
        self.assertEqual(result, Decimal('0'))

    def test_integer_to_decdeg_lowest_non_zero(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(1)
        self.assertEqual(result, Decimal('0.00000010000'))

    def test_integer_to_decdeg_hires_lowest_non_zero(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(0, 1)
        self.assertEqual(result, Decimal('0.00000000100'))

    def test_integer_to_decdeg_highest(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(2147483647)
        self.assertEqual(result, Decimal('214.7483647000'))

    def test_integer_to_decdeg_hires_highest(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(2147483647, 99)
        self.assertEqual(result, Decimal('214.7483647990'))

    def test_integer_to_decdeg_lowest(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(-2147483648)
        self.assertEqual(result, Decimal('-214.7483648000'))

    def test_integer_to_decdeg_hires_lowest(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_decdeg(-2147483648, -99)
        self.assertEqual(result, Decimal('-214.7483648990'))

    # decimal degrees -> ubx lat/lon integer field

    def test_decdeg_to_integer(self):
        converter = UBXDataFormatter()
        result1 = converter.decdeg_to_integer(Decimal('123.1234567'))
        result2 = converter.decdeg_to_integer(Decimal('10.123'))
        result3 = converter.decdeg_to_integer(Decimal('5.123456789'))
        result4 = converter.decdeg_to_integer(Decimal('0.0001'))
        self.assertEqual(result1, (1231234567, 00))
        self.assertEqual(result2, (101230000, 00))
        self.assertEqual(result3, (51234567, 89))
        self.assertEqual(result4, (1000, 00))

    def test_decdeg_to_integer_hires_excess_dropped(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('5.1234567899'))
        self.assertEqual(result, (51234567, 89))

    def test_decdeg_to_integer_negative(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('-123.1234567'))
        self.assertEqual(result, (-1231234567, 00))

    def test_decdeg_to_integer_negative_hires(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('-123.1234567899'))
        self.assertEqual(result, (-1231234567, -89))

    def test_decdeg_to_integer_zero(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('0'))
        self.assertEqual(result, (0, 0))

    def test_decdeg_to_integer_near_zero(self):
        converter = UBXDataFormatter()
        pos_hires_result = converter.decdeg_to_integer(Decimal( '0.000000001'))
        neg_hires_result = converter.decdeg_to_integer(Decimal('-0.000000001'))
        pos_lores_result = converter.decdeg_to_integer(Decimal( '0.0000001'))
        neg_lores_result = converter.decdeg_to_integer(Decimal('-0.0000001'))
        self.assertEqual(pos_hires_result, (0, 1))
        self.assertEqual(neg_hires_result, (0, -1))
        self.assertEqual(pos_lores_result, (1, 0))
        self.assertEqual(neg_lores_result, (-1, 0))

    def test_decdeg_to_integer_lowest(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('-214.7483648990'))
        self.assertEqual(result, (-2147483648, -99))

    def test_decdeg_to_integer_highest(self):
        converter = UBXDataFormatter()
        result = converter.decdeg_to_integer(Decimal('214.7483647990'))
        self.assertEqual(result, (2147483647, 99))

    # decimal height in mm -> ubx height/hMSL integer fields

    def test_integer_to_height_mm_zero(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_height_mm(0)
        self.assertEqual(Decimal('0.0') , result)

    def test_integer_to_height_mm_max(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_height_mm(2147483647)
        self.assertEqual(Decimal('2147483647.0'), result)

    def test_integer_to_height_mm_min(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_height_mm(-2147483648)
        self.assertEqual(Decimal('-2147483648.0'), result)

    def test_integer_to_height_mm_max_hires(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_height_mm(2147483647, 9)
        self.assertEqual(Decimal('2147483647.9'), result)

    def test_integer_to_height_mm_min_hires(self):
        converter = UBXDataFormatter()
        result = converter.integer_to_height_mm(-2147483648, -9)
        self.assertEqual(Decimal('-2147483648.9'), result)


    # ubx height/hMSL integer fields -> decimal height in mm

    def test_height_mm_to_integer_zero(self):
        converter = UBXDataFormatter()
        result = converter.height_mm_to_integer(Decimal('0.0'))
        self.assertEqual((0, 0), result)

    def test_height_mm_to_integer_max(self):
        converter = UBXDataFormatter()
        result = converter.height_mm_to_integer(Decimal('2147483647'))
        self.assertEqual((2147483647, 0), result)

    def test_height_mm_to_integer_min(self):
        converter = UBXDataFormatter()
        result = converter.height_mm_to_integer(Decimal('-2147483648'))
        self.assertEqual((-2147483648, 0), result)

    def test_height_mm_to_integer_max_hires(self):
        converter = UBXDataFormatter()
        result = converter.height_mm_to_integer(Decimal('2147483647.9'))
        self.assertEqual((2147483647, 9), result)

    def test_height_mm_to_integer_min_hires(self):
        converter = UBXDataFormatter()
        result = converter.height_mm_to_integer(Decimal('-2147483648.9'))
        self.assertEqual((-2147483648, -9), result)

    def test_height_mm_to_integer_assorted(self):
        converter = UBXDataFormatter()
        self.assertEqual((0, 1), converter.height_mm_to_integer(Decimal('0.1')))
        self.assertEqual((1, 5), converter.height_mm_to_integer(Decimal('1.5')))
        self.assertEqual((1, 5), converter.height_mm_to_integer(Decimal('1.55')))
        self.assertEqual((-10, 0), converter.height_mm_to_integer(Decimal('-10.01')))
        self.assertEqual((-1, -1), converter.height_mm_to_integer(Decimal('-1.1')))

    # minimize hi precision correction

    def test_minimize_correction_default_100(self):
        converter = UBXDataFormatter()

        # real life case
        self.assertEqual(( 296421107, -8 ), converter.minimize_correction(296421106,  92))
        self.assertEqual(( 296421107, -8 ), converter.minimize_correction(296421107, -8 ))

        # + / +
        self.assertEqual(( 100000000,   0), converter.minimize_correction(100000000,  0 ))
        self.assertEqual(( 100000000,  49), converter.minimize_correction(100000000,  49))
        self.assertEqual(( 100000001, -50), converter.minimize_correction(100000000,  50))
        self.assertEqual(( 100000001, -49), converter.minimize_correction(100000000,  51))
        self.assertEqual(( 100000001, -1 ), converter.minimize_correction(100000000,  99))

        # - / -
        self.assertEqual((-100000000,   0), converter.minimize_correction(-100000000,  0 ))
        self.assertEqual((-100000000, -49), converter.minimize_correction(-100000000, -49))
        self.assertEqual((-100000001,  50), converter.minimize_correction(-100000000, -50))
        self.assertEqual((-100000001,  49), converter.minimize_correction(-100000000, -51))
        self.assertEqual((-100000001,  1 ), converter.minimize_correction(-100000000, -99))

    def test_minimize_correction_default_100_max_min(self):
        converter = UBXDataFormatter()

        # NOTE on the boundaries of the 32 bit fields,
        #      if the correction causes an overflow, we avoid it

        # + / +
        self.assertEqual((2147483647, 99), converter.minimize_correction(2147483647, 99))
        self.assertEqual((2147483647, 50), converter.minimize_correction(2147483647, 50))
        self.assertEqual((2147483647, 49), converter.minimize_correction(2147483647, 49))

        # - / -
        self.assertEqual((-2147483648, -99), converter.minimize_correction(-2147483648, -99))
        self.assertEqual((-2147483648, -50), converter.minimize_correction(-2147483648, -50))
        self.assertEqual((-2147483648, -49), converter.minimize_correction(-2147483648, -49))

    def test_minimize_correction_midpoint_diff_sign_raises(self):
        converter = UBXDataFormatter()

        with self.assertRaises(ValueError) as context:
            converter.minimize_correction(-100000000, 51, midpoint=50)
        self.assertEqual('Operation not defined for not matching signs',
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            converter.minimize_correction(100000000, -51, midpoint=50)
        self.assertEqual('Operation not defined for not matching signs',
            str(context.exception))
