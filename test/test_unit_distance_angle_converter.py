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

    TOLERANCE = 6

    @data(
        _data(lat=D("25"), lon=D("-88"), alt=D("0"), factor_lat=D("110863.588408447"), factor_lon=D("101032.741490611")),
        _data(lat=D("90"), lon=D("-88"), alt=D("0"), factor_lat=D("111693.9791457850"), factor_lon=D("0.0000000000")),
        _data(lat=D("0.0"), lon=D("-88.0"), alt=D("0"), factor_lat=D("110574.9563383210"), factor_lon=D("111319.4904007660")),
        _data(lat=D("89.0"), lon=D("-88.0"), alt=D("0"), factor_lat=D("111693.6982589560"), factor_lon=D("1949.3277206142")),
        _data(lat=D("-89.0"), lon=D("-88.0"), alt=D("0"), factor_lat=D("110948.5729163590"), factor_lon=D("1936.3235426595")),
        _data(lat=D("-90.0"), lon=D("-88.0"), alt=D("0"), factor_lat=D("110948.7433106710"), factor_lon=D("0.0000000000")),
        _data(lat=D("45.0"), lon=D("0.0"), alt=D("0"), factor_lat=D("111209.7227700660"), factor_lon=D("78901.7343263512")),
        _data(lat=D("45.0"), lon=D("180.0"), alt=D("0"), factor_lat=D("111209.7227700660"), factor_lon=D("78901.7343263864")),
        _data(lat=D("45.0"), lon=D("-180.0"), alt=D("0"), factor_lat=D("111209.7227700660"), factor_lon=D("78901.7343263864")),
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
            self.assertEqual(round(expected.lat, self.TOLERANCE), round(actual.lat, self.TOLERANCE))
            self.assertEqual(round(expected.lon, self.TOLERANCE), round(actual.lon, self.TOLERANCE))
        location_provider.get_location.assert_called_once()
