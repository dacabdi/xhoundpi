# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from ddt import ddt, data, unpack
from decimal import Decimal as D

import xhoundpi.conversion_factor_decorators
from xhoundpi.dmath import DECIMAL0_1 as D0_1, DECIMAL0 as D0, DECIMAL1 as D1, DECIMAL2 as D2, DECIMAL3 as D3, setup_common_context
from xhoundpi.conversion_factor import ConversionFactor as CF, IConversionFactorProvider
from xhoundpi.coordinates import GeoCoordinates as GC

import xhoundpi.coordinates_offset_decorators # pylint: disable=unused-import

setup_common_context()

class StubFactorProvider(IConversionFactorProvider):

    def __init__(self, factor: CF):
        self.__factor = factor
        self.called = False

    def get_factor(self) -> CF:
        self.called = True
        return self.__factor

@ddt
class test_ConversionFactorProviderWithInversion(unittest.TestCase):

    # TODO determine if more data cases are needed,
    #      we are only really testing the multiplication here
    @data(
        (CF(D1, D1), CF(D1, D1)), # identity
        (CF(D0, D0), CF(D0, D0)), # zero
        (CF(D(10), D(10)), CF(D0_1, D0_1)),
        (CF(D3, D3), CF(D('0.333333333333333333333333'), D('0.333333333333333333333333'))),
    )
    @unpack
    def test_decorator(self, factor, expected):
        factor_provider = StubFactorProvider(factor)

        # pylint: disable=no-member
        decorated = factor_provider.with_inversion() # type: ignore
        # pylint: enable=no-member

        result = decorated.get_factor()
        self.assertTrue(factor_provider.called)
        self.assertEqual(expected, result)

    def test_access_to_decorated_object_props(self):
        factor_provider = StubFactorProvider(CF(D2, D2))

        # pylint: disable=no-member
        decorated = factor_provider.with_inversion() # type: ignore
        # pylint: enable=no-member

        _ = decorated.get_factor()
        self.assertTrue(factor_provider.called)

         # (__getattr__) stub's property, not decorator, should passthrough
        self.assertTrue(hasattr(decorated, 'called'))
        self.assertTrue(decorated.called)
        self.assertTrue(factor_provider.called)

        # (__setattr__) reflects change into decorated
        decorated.called = False
        self.assertFalse(factor_provider.called)

        # (__delattr__) remove property
        del factor_provider.called
        self.assertFalse(hasattr(factor_provider, 'called'))
