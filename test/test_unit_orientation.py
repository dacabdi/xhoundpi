# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from decimal import Decimal as D

from xhoundpi.dmath import setup_common_context
from xhoundpi.orientation import EulerAngles, StaticOrientationProvider

setup_common_context()

class test_StaticOrientationProvider(unittest.TestCase):

    def test_provide(self):
        angles = EulerAngles(yaw=D("-1.5"), pitch=D("0.2"))
        provider = StaticOrientationProvider(angles)

        self.assertEqual(EulerAngles(yaw=D("-1.5"), pitch=D("0.2")),
            provider.get_orientation(), msg = 'Because it must provide the preset angles')

        self.assertEqual(EulerAngles(yaw=D("-1.5"), pitch=D("0.2")),
            provider.get_orientation(), msg = 'Because it must provide the same value across calls')
