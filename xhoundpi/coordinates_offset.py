'''
Coordinate offset models and providers definition
'''

from abc import ABC, abstractmethod
from decimal import Decimal, Inexact, localcontext

from .dmath import sin, cos
from .coordinates import GeoCoordinates
from .orientation import IOrientationProvider

class ICoordinatesOffsetProvider(ABC):
    '''
    Coordinate offset provider for dynamically sourced
    manipulation of geographic coordinate messages
    '''

    @abstractmethod
    def get_offset(self) -> GeoCoordinates:
        '''
        Returns a coordinate offset object
        '''

class StaticOffsetProvider(ICoordinatesOffsetProvider):
    '''
    Fixed offset provider
    '''

    def __init__(self, offset: GeoCoordinates):
        self.__offset = offset

    def get_offset(self) -> GeoCoordinates:
        return self.__offset


class OrientationOffsetProvider(ICoordinatesOffsetProvider):
    '''
    Geographic coordinates dynamic offset provider
    based off euler angles orientation and radius
    '''

    def __init__(self, orientation: IOrientationProvider, radius: Decimal):
        self.__orientation = orientation
        self.__radius = radius

    def get_offset(self) -> GeoCoordinates:
        angles = self.__orientation.get_orientation()
        radius = self.__radius

        yaw = angles.yaw
        pitch = angles.pitch
        roll = angles.roll

        with localcontext() as ctx:
            # NOTE the sin/cos operations can produce irrational values
            #      that cannot guarantee exactitude, we accept it
            ctx.traps[Inexact] = False
            delta_latitude = radius * (sin(roll) * sin(yaw) + cos(roll) * cos(yaw) * sin(pitch))
            delta_longitude = -radius * (sin(roll) * cos(yaw) - cos(roll) * sin(pitch) * sin(yaw))
            delta_alt = radius * cos(roll) * cos(pitch)

        return GeoCoordinates(delta_latitude, delta_longitude, delta_alt)
