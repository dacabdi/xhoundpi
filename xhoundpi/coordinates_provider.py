'''
Location provider
'''

from abc import ABC, abstractmethod

from .dmath import DECIMAL0 as D0
from .coordinates import GeoCoordinates

class ICoordinatesProvider(ABC):
    '''
    Coordinate provider contract
    '''

    @abstractmethod
    def get_coordinates(self) -> GeoCoordinates:
        '''
        Provides a dynamic or preset coordinate
        '''

class StaticCoordinatesProvider(ICoordinatesProvider):
    '''
    Provides a fixed preset coordinate set
    '''

    def __init__(self, location: GeoCoordinates):
        self.__location = location

    def get_coordinates(self) -> GeoCoordinates:
        return self.__location

class DynamicCoordinatesProvider(ICoordinatesProvider):
    '''
    Updatable coordinates provider
    '''

    def __init__(self):
        self.__coordinates = GeoCoordinates(D0, D0, D0)

    def get_coordinates(self) -> GeoCoordinates:
        return self.__coordinates

    def update(self, coordinates: GeoCoordinates) -> None:
        '''
        Set coordinates
        '''
        self.__coordinates = coordinates
