# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from decimal import Decimal as D, Inexact, localcontext
from ddt import ddt, data, unpack

from xhoundpi.decimal_math import setup_common_decimal_context
from xhoundpi.distance_angle_converter import ConversionFactor, ConversionFactorProvider
from xhoundpi.geocoordinates import GeoCoordinates

setup_common_decimal_context()

def _data(lat: D, lon: D, alt: D, factor_lat: D, factor_lon: D):
    with localcontext() as ctx:
        # NOTE the ratio multiplication produces inexact results
        ctx.traps[Inexact] = False
        return (GeoCoordinates(lat, lon, alt), ConversionFactor(factor_lat, factor_lon))

@ddt
class test_DistanceAngleConverter(unittest.TestCase):

    TOLERANCE = 12

    @data(
        _data(lat=D("25"), lon=D("-80"), alt=D("0"), factor_lat=D("1"), factor_lon=D("1")),
        _data(lat=D("25"), lon=D("-80"), alt=D("0"), factor_lat=D("1"), factor_lon=D("1")),
    )
    @unpack
    def test_provide(self, locn, expected):
        location_provider = Mock()
        location_provider.get_location = Mock(return_value = locn)
        provider = ConversionFactorProvider(location_provider)
        actual = provider.get_factor()
        with localcontext() as ctx:
            # NOTE we are ok with not having exactitude on this comparison
            ctx.traps[Inexact] = False
            self.assertEqual(round(expected.factor_lat, self.TOLERANCE), round(actual[0], self.TOLERANCE))
            self.assertEqual(round(expected.factor_lon, self.TOLERANCE), round(actual[1], self.TOLERANCE))
        ConversionFactorProvider.get_factor.assert_called_once()
