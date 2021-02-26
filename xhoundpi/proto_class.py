""" Defines protocol class enumeration """

from enum import Enum

class ProtocolClass(Enum):
    NONE = 0
    UBX = 1
    NMEA = 2