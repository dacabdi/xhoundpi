'''
Coordinate offset models and providers definition
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, Inexact, localcontext

from .decimal_math import sin, cos, pi

@dataclass
class EulerAngles:
    '''
    Model for Euler angles orientation
    '''
    # pylint: disable=invalid-name
    yaw: Decimal = Decimal("0")
    pitch: Decimal = Decimal("0")
    roll: Decimal = Decimal("0")


class IOrientationProvider(ABC):
    '''
    Orientation provider in Euler angles
    '''

    @abstractmethod
    def get_orientation(self) -> EulerAngles:
        '''
        Returns the orientation in euler angles
        '''

class StaticOrientationProvider(IOrientationProvider):
    '''
    Static orientation provider in Euler angles
    '''

    def __init__(self, angles: EulerAngles):
        self.__angles = angles

    def get_orientation(self) -> EulerAngles:
        return self.__angles

@dataclass
class CoordinateOffset:
    '''
    Model for geographic coordinates offsets
    '''
    lat: Decimal
    lon: Decimal
    alt: Decimal

class ICoordinateOffsetProvider(ABC):
    '''
    Coordinate offset provider for dynamically sourced
    manipulation of geographic coordinate messages
    '''

    @abstractmethod
    def get_offset(self) -> CoordinateOffset:
        '''
        Returns a coordinate offset object
        '''

class StaticOffsetProvider(ICoordinateOffsetProvider):
    '''
    Fixed offset provider
    '''

    def __init__(self, offset: CoordinateOffset):
        self.__offset = offset

    def get_offset(self) -> CoordinateOffset:
        return self.__offset


class OrientationOffsetProvider(ICoordinateOffsetProvider):
    '''
    Geographic coordinates dynamic offset provider
    based off euler angles orientation and radius
    '''

    PI = pi()
    DEG180 = Decimal("180")

    def __init__(self, orientation: IOrientationProvider, radius: Decimal):
        self.__orientation = orientation
        self.__radius = radius

    def get_offset(self) -> CoordinateOffset:
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

        return CoordinateOffset(delta_latitude, delta_longitude, delta_alt)
