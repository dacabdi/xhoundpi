
from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext
from abc import ABC, abstractmethod

@dataclass
class Coordinates:
    '''
    Model for coordinates
    '''
    # pylint: disable=invalid-name
    latitude: Decimal = Decimal("0")
    longitude: Decimal = Decimal("0")
    altitude: Decimal = Decimal("0")


class ICoordinatesProvider(ABC):
    '''
    Coordinates provider
    '''

    @abstractmethod
    def get_coordinates(self) -> Coordinates:
        '''
        Returns the coordinates
        '''

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

    PI = pi()
    DEG180 = Decimal("180")

    def __init__(self, location: ICoordinatesProvider):
        self.__location = location

    def get_factor(self) -> ConversionFactor:
        coordinates = self.__location.get_coordinates()

        lat = coordinates.latitude
        long = coordinates.longitude
        alt = coordinates.altitude

        with localcontext() as ctx:
            # NOTE the sin/cos operations can produce irrational values
            #      that cannot guarantee exactitude, we accept it
            ctx.traps[Inexact] = False
            factor_lat = Decimal("1")
            factor_lon = -Decimal("1")

        return ConversionFactor(factor_lat, factor_lon)