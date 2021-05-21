# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from decimal import Decimal as D
from ddt import ddt, unpack, data

from xhoundpi.dmath import setup_common_context, adjust, dec_to_str

setup_common_context()

@ddt
class test_adjust(unittest.TestCase):

    @data(
        # out, in, leftexp, rightexp
        ('1.0', '1', -1, -3),
        ('1.00', '1', -2, -3),
        ('1.000', '1', -3, -3),
        ('1.23', '1.230', -1, -3),
        ('1.2', '1.200', -1, -3),
        ('1.0', '1.0', -1, -3),
        ('123.4507', '123.45078', -1, -4),
        ('123.45', '123.45008', -1, -4),
        ('123.45', '123.45008', -1, -3),
        ('1', '1', 0, -3),
        ('1.2', '1.234', -1, -1),
        ('1.00', '1.001', -2, -2),
        ('1.001', '1.001', -2, -3),
        ('100', '101.1', 1, 1),
        ('110', '111.1', 1, 1),
    )
    @unpack
    def test_adjust(self, _out, _in, leftexp, rightexp):
        self.assertEqual(_out,
            dec_to_str(
                adjust(D(_in),
                leftexp=leftexp,
                rightexp=rightexp)))
