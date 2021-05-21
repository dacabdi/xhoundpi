'''
Surface distance to lat/long angle factor calculator
'''

from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext
from abc import ABC, abstractmethod
from .dmath import MINUTE, geodethic_to_ecef, distance
from .coordinates import GeoCoordinates
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

class DistAngleFactorProvider(IConversionFactorProvider):
    '''
    Converion factor provider;
    translates surface distance to latitude/longitude increments
    '''

    def __init__(self, location: ICoordinatesProvider):
        self.__location = location

    def get_factor(self) -> ConversionFactor:
        p0_geo = self.__location.get_coordinates()

        with localcontext() as ctx:
            # NOTE the sin/cos operations can produce irrational values
            #      that cannot guarantee exactitude, we accept it
            ctx.traps[Inexact] = False

            p1_geo = GeoCoordinates(p0_geo.lat + MINUTE, p0_geo.lon, p0_geo.alt)
            p2_geo = GeoCoordinates(p0_geo.lat, p0_geo.lon + MINUTE, p0_geo.alt)

            # pylint: disable=invalid-name
            p0_ecef = geodethic_to_ecef(p0_geo)
            p1_ecef = geodethic_to_ecef(p1_geo)
            p2_ecef = geodethic_to_ecef(p2_geo)

            factor_lat = distance(p0_ecef, p1_ecef) / MINUTE
            factor_lon = distance(p0_ecef, p2_ecef) / MINUTE

        return ConversionFactor(factor_lat, factor_lon)
