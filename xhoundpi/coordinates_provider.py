'''
Location provider
'''

from abc import ABC, abstractmethod

from .geocoordinates import GeoCoordinates

class ICoordinatesProvider(ABC):
    '''
    Coordinate provider contract
    '''

    @abstractmethod
    def get_location(self) -> GeoCoordinates:
        '''
        Provides a dynamic or preset coordinate
        '''

class StaticCoordinatesProvider(ICoordinatesProvider):
    '''
    Provides a fixed preset coordinate set
    '''

    def __init__(self, location: GeoCoordinates):
        self.__location = location

    def get_location(self) -> GeoCoordinates:
        return self.__location
