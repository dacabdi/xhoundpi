'''
Defines orientation types, providers contracts, and implementations
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

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
