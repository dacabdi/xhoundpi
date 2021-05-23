'''
Decorators and extensions for IConversionFactorProvider contract
'''

from decimal import Inexact, localcontext

from .dmath import DECIMAL0 as D0, DECIMAL1 as D1
from .monkey_patching import add_method
from .conversion_factor import ConversionFactor, IConversionFactorProvider

@add_method(IConversionFactorProvider)
def with_inversion(self) -> IConversionFactorProvider:
    '''
    Decorates an conversion factor by changing the factors to their inverse
    '''
    return ConversionFactorProviderWithInversion(self)

class ConversionFactorProviderWithInversion(IConversionFactorProvider):
    '''
    Conversion factor decorator that provides result inversion
    '''

    def __init__(self, inner: IConversionFactorProvider):
        self.__class__.__name__ = inner.__class__.__name__
        self._inner = inner

    def get_factor(self) -> ConversionFactor:
        factor = self._inner.get_factor()
        with localcontext() as ctx:
            ctx.traps[Inexact] = False
            # NOTE
            #  1. the inversion is likely to produce periodically infinite values
            #     we tolerate this problem up to the configured precision
            #  2. in theory if the c.f. is 0, its inverse would produce
            #     an infinite value, we clamp to 0 in such cases
            lat = D0 if factor.lat == D0 else D1 / factor.lat
            lon = D0 if factor.lon == D0 else D1 / factor.lon
        return ConversionFactor(lat=lat, lon=lon)

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner',):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
