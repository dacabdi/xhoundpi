# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from ddt import ddt, data, unpack
from decimal import Decimal as D

from xhoundpi.dmath import DECIMAL1 as D1, DECIMAL3 as D3, DECIMAL2 as D2, setup_common_context
from xhoundpi.conversion_factor import ConversionFactor as CF, IConversionFactorProvider
from xhoundpi.coordinates import GeoCoordinates as GC
from xhoundpi.coordinates_offset import ICoordinatesOffsetProvider

import xhoundpi.coordinates_offset_decorators # pylint: disable=unused-import

setup_common_context()

class StubOffsetProvider(ICoordinatesOffsetProvider):

    def __init__(self, offset: GC):
        self.__offset = offset
        self.called = False

    def get_offset(self) -> GC:
        self.called = True
        return self.__offset

class StubFactorProvider(IConversionFactorProvider):

    def __init__(self, factor: CF):
        self.__factor = factor
        self.called = False

    def get_factor(self) -> CF:
        self.called = True
        return self.__factor

@ddt
class test_CoordinatesOffsetProviderWithConversion(unittest.TestCase):

    # TODO determine if more data cases are needed,
    #      we are only really testing the multiplication here
    @data((GC(D2, D2, D1), CF(D3, D3), GC(D(6), D(6), D1)))
    @unpack
    def test_decorator(self, offset, factor, expected):
        factor_provider = StubFactorProvider(factor)
        offset_provider = StubOffsetProvider(offset)

        # pylint: disable=no-member
        decorated = offset_provider.with_conversion(factor_provider) # type: ignore
        # pylint: enable=no-member

        result = decorated.get_offset()
        self.assertTrue(offset_provider.called)
        self.assertTrue(factor_provider.called)
        self.assertEqual(expected, result)

    def test_access_to_decorated_object_props(self):
        factor_provider = StubFactorProvider(CF(D2, D2))
        offset_provider = StubOffsetProvider(GC(D1, D1, D1))

        # pylint: disable=no-member
        decorated = offset_provider.with_conversion(factor_provider) # type: ignore
        # pylint: enable=no-member

        _ = decorated.get_offset()
        self.assertTrue(offset_provider.called)
        self.assertTrue(factor_provider.called)

         # (__getattr__) stub's property, not decorator, should passthrough
        self.assertTrue(hasattr(decorated, 'called'))
        self.assertTrue(decorated.called)
        self.assertTrue(offset_provider.called)

        # (__setattr__) reflects change into decorated
        decorated.called = False
        self.assertFalse(offset_provider.called)

        # (__delattr__) remove property
        del offset_provider.called
        self.assertFalse(hasattr(offset_provider, 'called'))
