# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from decimal import Decimal as D, Inexact, localcontext
from ddt import ddt, data, unpack

from xhoundpi.decimal_math import deg_to_rad

from xhoundpi.coordinate_offset import (
    CoordinateOffset,
    OrientationOffsetProvider,
    EulerAngles,
    StaticOffsetProvider,
    StaticOrientationProvider,)

class test_StaticOrientationProvider(unittest.TestCase):

    def test_provide(self):
        angles = EulerAngles(yaw=D("-1.5"), pitch=D("0.2"))
        provider = StaticOrientationProvider(angles)

        self.assertEqual(EulerAngles(yaw=D("-1.5"), pitch=D("0.2")),
            provider.get_orientation(), msg = 'Because it must provide the preset angles')

        self.assertEqual(EulerAngles(yaw=D("-1.5"), pitch=D("0.2")),
            provider.get_orientation(), msg = 'Because it must provide the same value across calls')

class test_StaticOffsetProvider(unittest.TestCase):

    def test_provide(self):
        offset = CoordinateOffset(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3"))
        provider = StaticOffsetProvider(offset)

        self.assertEqual(
            CoordinateOffset(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3")),
            provider.get_offset(), msg = 'Because it must provide the preset offset')

        self.assertEqual(
            CoordinateOffset(lat=D("0.5"), lon=D("-0.1"), alt=D("-0.3")),
            provider.get_offset(), msg = 'Because it must provide the same value across calls')


def _data(yaw: D, pitch: D, roll: D, r: D, lat: D, lon: D, alt: D):
    with localcontext() as ctx:
        # NOTE the ratio multiplication produces inexact results
        ctx.traps[Inexact] = False
        return (EulerAngles(deg_to_rad(yaw), deg_to_rad(pitch), deg_to_rad(roll)), r, CoordinateOffset(lat, lon, alt))

@ddt
class test_OrientationOffsetProvider(unittest.TestCase):

    TOLERANCE = 12

    @data(
        _data(yaw=D("0"), pitch=D("0"), roll=D("0"), r=D("10"), lat=D("0"), lon=D("0"), alt=D("10")),
        _data(yaw=D("0"), pitch=D("60"), roll=D("0"), r=D("10"), lat=D("8.6602540378443864676372317075294"), lon=D("0"), alt=D("5")),
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
