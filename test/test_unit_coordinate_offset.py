# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from decimal import Decimal as D, Inexact, localcontext
from ddt import ddt, data, unpack

from xhoundpi.dmath import deg2rad, setup_common_context
from xhoundpi.orientation import EulerAngles
from xhoundpi.coordinates_offset import GeoCoordinates, OrientationOffsetProvider, StaticOffsetProvider

setup_common_context()

class test_StaticOffsetProvider(unittest.TestCase):

    def test_provide(self):
        offset = GeoCoordinates(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3"))
        provider = StaticOffsetProvider(offset)

        self.assertEqual(
            GeoCoordinates(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3")),
            provider.get_offset(), msg = 'Because it must provide the preset offset')

        self.assertEqual(
            GeoCoordinates(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3")),
            provider.get_offset(), msg = 'Because it must provide the same value across calls')

# pylint: disable=too-many-arguments
def _data(yaw: D, pitch: D, roll: D, r: D, lat: D, lon: D, alt: D):
    with localcontext() as ctx:
        # NOTE the ratio multiplication produces inexact results
        ctx.traps[Inexact] = False
        return (EulerAngles(deg2rad(yaw), deg2rad(pitch), deg2rad(roll)), r, GeoCoordinates(lat, lon, alt))

@ddt
class test_OrientationOffsetProvider(unittest.TestCase):

    TOLERANCE = 12

    @data(
        _data(yaw=D("0"), pitch=D("0"), roll=D("0"), r=D("10"), lat=D("0"), lon=D("0"), alt=D("10")),
        _data(yaw=D("0"), pitch=D("60"), roll=D("0"), r=D("10"), lat=D("8.6602540378443864676372317075294"), lon=D("0"), alt=D("5")),
        _data(yaw=D("0"), pitch=D("30"), roll=D("0"), r=D("10"), lat=D("5"), lon=D("0"), alt=D("8.6602540378443864676372317075294")),
        _data(yaw=D("30"), pitch=D("30"), roll=D("0"), r=D("10"), lat=D("4.33012701892219"), lon=D("2.5"), alt=D("8.6602540378443864676372317075294")),
        _data(yaw=D("0"), pitch=D("45"), roll=D("0"), r=D("10"), lat=D("7.07106781186547"), lon=D("0"), alt=D("7.07106781186547")),
        _data(yaw=D("45"), pitch=D("45"), roll=D("0"), r=D("10"), lat=D("5"), lon=D("5"), alt=D("7.07106781186547")),
        _data(yaw=D("45"), pitch=D("45"), roll=D("90"), r=D("10"), lat=D("7.07106781186547"), lon=D("-7.07106781186547"), alt=D("0")),
    )
    @unpack
    def test_provide(self, angles, radius, expected):
        orientation_provider = Mock()
        orientation_provider.get_orientation = Mock(return_value=angles)
        provider = OrientationOffsetProvider(orientation_provider, radius)
        actual = provider.get_offset()
        with localcontext() as ctx:
            # NOTE we are ok with not having exactitude on this comparison
            ctx.traps[Inexact] = False
            self.assertEqual(round(expected.lat, self.TOLERANCE), round(actual.lat, self.TOLERANCE))
            self.assertEqual(round(expected.lon, self.TOLERANCE), round(actual.lon, self.TOLERANCE))
            self.assertEqual(round(expected.alt, self.TOLERANCE), round(actual.alt, self.TOLERANCE))
        orientation_provider.get_orientation.assert_called_once()
