# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock

from decimal import Decimal

from xhoundpi.direction import (Direction,
                               CoordAxis)
from xhoundpi.data_formatter import (NMEADataFormatter,
                                    UBXDataFormatter)

class test_NMEADataFormatter(unittest.TestCase): # pylint: disable=too-many-public-methods

    # degmins_to_decdeg

    def test_degmins_to_decdeg_and_direction_sign(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('1212.12345', Direction.N),  Decimal(  '12.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('1212.12345', Direction.S),  Decimal( '-12.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('12312.12345', Direction.E), Decimal( '123.2020575'))
        self.assertEqual(converter.degmins_to_decdeg('12312.12345', Direction.W), Decimal('-123.2020575'))

    def test_degmins_to_decdeg_and_direction_sign_hires_inexact(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('1212.1234567', Direction.N),  Decimal(  '12.2020576116666666666666'))
        self.assertEqual(converter.degmins_to_decdeg('1212.1234567', Direction.S),  Decimal( '-12.2020576116666666666666'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234567', Direction.E), Decimal( '123.202057611666666666666'))
        self.assertEqual(converter.degmins_to_decdeg('12312.1234567', Direction.W), Decimal('-123.202057611666666666666'))

    def test_degmins_to_decdeg_inexact_24res(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0004.00000', Direction.N),  Decimal('0.0666666666666666666666666'))

    def test_degmins_to_decdeg_zero(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.00000', Direction.N),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('0000.00000', Direction.S),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00000', Direction.E),  Decimal('0'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00000', Direction.W),  Decimal('0'))

    def test_degmins_to_decdeg_near_zero(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.00001', Direction.N),  Decimal('1.66666666666666666666666E-7'))
        self.assertEqual(converter.degmins_to_decdeg('0000.00001', Direction.S),  Decimal('-1.66666666666666666666666E-7'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00001', Direction.E),  Decimal('1.66666666666666666666666E-7'))
        self.assertEqual(converter.degmins_to_decdeg('00000.00001', Direction.W),  Decimal('-1.66666666666666666666666E-7'))

    def test_degmins_to_decdeg_near_zero_hires(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('0000.0000001', Direction.N),  Decimal('1.66666666666666666666666E-9'))
        self.assertEqual(converter.degmins_to_decdeg('0000.0000001', Direction.S),  Decimal('-1.66666666666666666666666E-9'))
        self.assertEqual(converter.degmins_to_decdeg('00000.0000001', Direction.E),  Decimal('1.66666666666666666666666E-9'))
        self.assertEqual(converter.degmins_to_decdeg('00000.0000001', Direction.W),  Decimal('-1.66666666666666666666666E-9'))

    def test_degmins_to_decdeg_max(self):
        converter = NMEADataFormatter()
        self.assertEqual(converter.degmins_to_decdeg('9999.99999', Direction.N),  Decimal('100.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('9999.99999', Direction.S),  Decimal('-100.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.99999', Direction.E),  Decimal('1000.6666665'))
        self.assertEqual(converter.degmins_to_decdeg('99999.99999', Direction.W),  Decimal('-1000.6666665'))

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

    # minimize hi precision correction

    def test_minimize_correction(self):
        converter = UBXDataFormatter()

        # real life case
        self.assertEqual(( 296421107, -8 ), converter.minimize_correction(296421106,  92))
        self.assertEqual(( 296421107, -8 ), converter.minimize_correction(296421107, -8 ))

        # + / +
        self.assertEqual(( 100000000,   0), converter.minimize_correction(100000000,  0 ))
        self.assertEqual(( 100000000,  49), converter.minimize_correction(100000000,  49))
        self.assertEqual(( 100000000,  50), converter.minimize_correction(100000000,  50))
        self.assertEqual(( 100000001, -49), converter.minimize_correction(100000000,  51))
        self.assertEqual(( 100000001, -1 ), converter.minimize_correction(100000000,  99))

        # - / -
        self.assertEqual((-100000000,   0), converter.minimize_correction(-100000000,  0 ))
        self.assertEqual((-100000000, -49), converter.minimize_correction(-100000000, -49))
        self.assertEqual((-100000000, -50), converter.minimize_correction(-100000000, -50))
        self.assertEqual((-100000001,  49), converter.minimize_correction(-100000000, -51))
        self.assertEqual((-100000001,  1 ), converter.minimize_correction(-100000000, -99))

    def test_minimize_correction_gt50_diff_sign_raises(self):
        converter = UBXDataFormatter()

        with self.assertRaises(ValueError) as context:
            converter.minimize_correction(-100000000, 51)
        self.assertEqual('Operation not defined for not matching signs',
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            converter.minimize_correction(100000000, -51)
        self.assertEqual('Operation not defined for not matching signs',
            str(context.exception))
