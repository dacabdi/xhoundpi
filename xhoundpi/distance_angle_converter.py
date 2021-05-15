
from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext
from abc import ABC, abstractmethod
from typing import Tuple

from .decimal_math import sin, cos, deg_to_rad
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
        point1 = self.__location.get_location()

        with localcontext() as ctx:
            # NOTE the sin/cos operations can produce irrational values
            #      that cannot guarantee exactitude, we accept it
            ctx.traps[Inexact] = False

            minute = Decimal("1") / Decimal("60")

            point2 = [point1.lat + minute, point1.lon + minute, point1.alt]

            x0, y0, z0 = geodethic_to_ecef(point1)
            x1, y1, z1 = geodethic_to_ecef(point2)

            factor_lat = ( y1 - y0 ) / minute
            factor_lon = ( x1 - x0 ) / minute

        return ConversionFactor(factor_lat, factor_lon)

def geodethic_to_ecef(point: GeoCoordinates) -> Tuple[Decimal, Decimal, Decimal]:

    '''
    Function to convert from Geodethic coordinates to Earth Centered - Earth Fixed (ECEF) coordinate system
    '''
    lat = point.lat
    lon = point.lon
    alt = point.alt

    semi_major_axis = Decimal("6378137"); 'equatorial radius in meters'
    semi_minor_axis = Decimal("6356752.3"); 'polar radius in meters'

    ellipsoid_eccentricity_squared = 1 - ( semi_minor_axis**2 / semi_major_axis**2 )

    earth_prime_vertical_radius = semi_major_axis / ( 1 - ellipsoid_eccentricity_squared * sin(deg_to_rad(lat)) )**0.5

    x_coord = ( earth_prime_vertical_radius + alt ) * cos(deg_to_rad(lat)) * cos(deg_to_rad(lon))
    y_coord = ( earth_prime_vertical_radius + alt ) * cos(deg_to_rad(lat)) * sin(deg_to_rad(lon))
    z_coord = ( ( semi_minor_axis**2 / semi_major_axis**2 ) * earth_prime_vertical_radius + alt ) * sin(deg_to_rad(lat))

    return x_coord, y_coord, z_coord