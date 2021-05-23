'''
Decorators and extensions for ICoordinatesOffsetProviders contract
'''

from .monkey_patching import add_method
from .coordinates import GeoCoordinates
from .conversion_factor import IConversionFactorProvider
from .coordinates_offset import ICoordinatesOffsetProvider

@add_method(ICoordinatesOffsetProvider)
def with_conversion(self, factor_provider: IConversionFactorProvider):
    '''
    Decorates an offset provider and applies a conversion factor to the offset before returning it
    '''
    return CoordinatesOffsetProviderWithConversion(self, factor_provider)

class CoordinatesOffsetProviderWithConversion(ICoordinatesOffsetProvider):
    '''
    Decorates an offset provider and applies a conversion factor to the offset before returning it
    '''

    def __init__(self,
        inner: ICoordinatesOffsetProvider,
        factor_provider: IConversionFactorProvider):
        self.__class__.__name__ = inner.__class__.__name__
        self._inner = inner
        self._factor_provider = factor_provider

    def get_offset(self) -> GeoCoordinates:
        offset = self._inner.get_offset()
        factor = self._factor_provider.get_factor()
        return GeoCoordinates(
            offset.lat * factor.lat,
            offset.lon * factor.lon,
            offset.alt,)

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_factor_provider'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
