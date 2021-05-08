# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from dataclasses import dataclass
from ddt import ddt, data, unpack

from decimal import Decimal as D

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
        offset = CoordinateOffset(lat=D("0.5"), lon=D("-0.1"))
        provider = StaticOffsetProvider(offset)

        self.assertEqual(
            CoordinateOffset(lat=D("0.5"), lon=D("-0.1")),
            provider.get_offset(), msg = 'Because it must provide the preset offset')

        self.assertEqual(
            CoordinateOffset(lat=D("0.5"), lon=D("-0.1")),
            provider.get_offset(), msg = 'Because it must provide the same value across calls')


def _data(yaw: D, pitch: D, roll: D, r: D, lat: D, lon: D):
    return (EulerAngles(yaw, pitch, roll), r, CoordinateOffset(lat, lon))

@ddt
class test_OrientationOffsetProvider(unittest.TestCase):

    @data(
        _data(yaw=D("0.5"), pitch=D("0.5"), roll=D("0.4"), r=D("10"), lat=D("10.5"), lon=D("10.5")),
        _data(yaw=D("0.5"), pitch=D("0.5"), roll=D("0.4"), r=D("10"), lat=D("10.5"), lon=D("11.5")),
        _data(yaw=D("0.5"), pitch=D("0.5"), roll=D("0.4"), r=D("10"), lat=D("10.5"), lon=D("10.5"))
    )
    @unpack
    def test_provide(self, angles, radius, offset):
        orientation_provider = Mock()
        orientation_provider.get_orientation = Mock(return_value=angles)
        provider = OrientationOffsetProvider(orientation_provider, radius)
        self.assertEqual(offset, provider.get_offset())
        orientation_provider.get_orientation.assert_called_once()
