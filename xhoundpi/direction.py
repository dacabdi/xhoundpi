""" Defines cardinal directions as an enumeration """

from enum import Enum
from typing import Any

class Direction(Enum):
    """ Cardinal directions """
    N = 0
    S = 1
    W = 2
    E = 3

    @classmethod
    def from_symbol(cls, symbol: str):
        """
        Create Direction enum from string symbol
        """
        symbol = symbol.lower()
        # TODO use `match` when updating to Python 3.10
        if symbol in ('n', 'north'):
            return Direction.N
        if symbol in ('s', 'south'):
            return Direction.S
        if symbol in ('w', 'west'):
            return Direction.W
        if symbol in ('e', 'east'):
            return Direction.E
        raise ValueError(f'Cannot convert {symbol} '
                          'symbol to a direction')

class CoordAxis(Enum):
    """ Coordinate axis enumeration """
    LON = 1
    LAT = 2

    @classmethod
    def from_symbol(cls, symbol: Any):
        """
        Create Coordinate enum from string symbol or direction
        """
        # TODO use `match` when updating to Python 3.10
        symbol = (symbol.name
            if isinstance(symbol, Direction)
            else str(symbol)).lower()
        if symbol in (
            'lat', 'latitude', 'dir_lat',
            'n', 'north',
            's', 'south'):
            return CoordAxis.LAT
        if symbol in (
            'lon', 'long', 'longitude', 'dir_lon',
            'e', 'east',
            'w', 'west'):
            return CoordAxis.LON
        raise ValueError(f'Cannot convert \'{symbol}\' '
                          'symbol to a coordinate axis')
