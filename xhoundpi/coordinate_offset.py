'''
Coordinate offset models and providers definition
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass

from decimal import Decimal

@dataclass
class CoordinateOffset:
    '''
    Model for geographic coordinates offsets
    '''
    latitude: Decimal
    longitude: Decimal

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
