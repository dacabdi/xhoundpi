# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock
from decimal import Decimal as D

from xhoundpi.decimal_math import setup_common_decimal_context, normalize_fraction

setup_common_decimal_context()

class test_normalize_fraction(unittest.TestCase):

    def test_normalize_fraction(self):
        self.assertEqual(D('1.0'), normalize_fraction(D('1'), minp=1, maxp=3))
        self.assertEqual(D('1.00'), normalize_fraction(D('1'), minp=2, maxp=3))
        self.assertEqual(D('1.123'), normalize_fraction(D('1.1234'), minp=1, maxp=3))
        self.assertEqual(D('1.12'), normalize_fraction(D('1.1234'), minp=1, maxp=2))
        self.assertEqual(D('1.1'), normalize_fraction(D('1.10'), minp=1, maxp=2))
