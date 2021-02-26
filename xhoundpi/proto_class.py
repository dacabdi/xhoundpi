""" Defines protocol class enumeration """

from enum import Enum

class ProtocolClass(Enum):
    """ GNSS Protocol classes enumeration """
    NONE = 0
    UBX = 1
    NMEA = 2
