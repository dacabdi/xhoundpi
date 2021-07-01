# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from decimal import Decimal as D

from xhoundpi.dmath import setup_common_context, DECIMAL0 as D0
from xhoundpi.coordinates import GeoCoordinates
from xhoundpi.coordinates_provider import DynamicCoordinatesProvider, StaticCoordinatesProvider

setup_common_context()

class test_StaticCoordinatesProvider(unittest.TestCase):

    def test_provide(self):
        angles = GeoCoordinates(lat=D('-1.5'), lon=D('0.1'), alt=D('0.5'))
        provider = StaticCoordinatesProvider(angles)

        self.assertEqual(GeoCoordinates(lat=D('-1.5'), lon=D('0.1'), alt=D('0.5')),
            provider.get_coordinates(), msg = 'Because it must provide the preset coordinates')

        self.assertEqual(GeoCoordinates(lat=D('-1.5'), lon=D('0.1'), alt=D('0.5')),
            provider.get_coordinates(), msg = 'Because it must provide the same value across calls')

class test_DynamicCoordinatesProvider(unittest.TestCase):

    def test_provide(self):
        provider = DynamicCoordinatesProvider()
        self.assertEqual(GeoCoordinates(D0, D0, D0), provider.get_coordinates())

        provider.update(GeoCoordinates(D('1.3'), D('5.6'), D('2.3')))
        self.assertEqual(GeoCoordinates(D('1.3'), D('5.6'), D('2.3')), provider.get_coordinates())
