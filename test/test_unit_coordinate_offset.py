# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock
from decimal import Decimal

from xhoundpi.coordinate_offset import CoordinateOffset, StaticOffsetProvider

class test_StaticOffsetProvider(unittest.TestCase):

    def test_provide(self):
        offset = CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("-0.1"))
        provider = StaticOffsetProvider(offset)

        self.assertEqual(
            CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("-0.1")),
            provider.get_offset(), msg = 'Because it must provide the preset offset')

        self.assertEqual(
            CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("-0.1")),
            provider.get_offset(), msg = 'Because it must provide the same value across calls')
