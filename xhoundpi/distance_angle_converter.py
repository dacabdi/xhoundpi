'''
Surface distance to lat/long angle factor calculator
'''

from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext
from abc import ABC, abstractmethod
from .decimal_math import MINUTE, geodethic_to_ecef
from .geocoordinates import GeoCoordinates
from .coordinates_provider import ICoordinatesProvider

@dataclass
class ConversionFactor:
    '''
    Model for conversion between surface distance and latitude/longitude increments
    '''
    lat: Decimal
    lon: Decimal

class IConversionFactorProvider(ABC):
    '''
    Conversion factor provider for converting offsets to latitude/longitude increments
    '''

    @abstractmethod
    def get_factor(self) -> ConversionFactor:
        '''
        Returns a conversion factor object
        '''

class ConversionFactorProvider(IConversionFactorProvider):
    '''
    Converion factor provider;
    translates surface distance to latitude/longitude increments
    '''

    def __init__(self, location: ICoordinatesProvider):
        self.__location = location

    def get_factor(self) -> ConversionFactor:
        point0 = self.__location.get_location()

        with localcontext() as ctx:
            # NOTE the sin/cos operations can produce irrational values
            #      that cannot guarantee exactitude, we accept it
            ctx.traps[Inexact] = False

            point1 = GeoCoordinates(point0.lat + MINUTE, point0.lon, point0.alt)
            point2 = GeoCoordinates(point0.lat, point0.lon + MINUTE, point0.alt)

            # pylint: disable=invalid-name
            x0, y0, z0 = geodethic_to_ecef(point0)
            x1, y1, z1 = geodethic_to_ecef(point1)
            x2, y2, z2 = geodethic_to_ecef(point2)

            factor_lat = Decimal.sqrt((y1 - y0)**2 + (x1 - x0)**2 + (z1 - z0)**2) / MINUTE
            factor_lon = Decimal.sqrt((y2 - y0)**2 + (x2 - x0)**2 + (z2 - z0)**2) / MINUTE

        return ConversionFactor(factor_lat, factor_lon)
