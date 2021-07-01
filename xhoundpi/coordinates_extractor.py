'''
Module for coordinates extractors and helpers
'''

from .dmath import DECIMAL0 as D0
from .direction import Direction
from .proto_class import ProtocolClass
from .data_formatter import NMEADataFormatter, UBXDataFormatter
from .message import Message
from .coordinates import GeoCoordinates

class CoordinatesExtractor:
    '''
    Extracts coordinates from GNSS messages
    '''

    def __init__(self,
        nmea_formatter: NMEADataFormatter,
        ubx_formatter: UBXDataFormatter):
        self.__nmea = nmea_formatter
        self.__ubx = ubx_formatter

    def extract_coordinates(self, message: Message) -> GeoCoordinates:
        '''
        Extract geo coordinates from a message.
        Will raise an exception is the protocol is unknown
        or the message does not contain geocoordinates.
        '''
        if message.proto == ProtocolClass.NMEA:
            return self.__from_nmea(message)
        if message.proto == ProtocolClass.UBX:
            return self.__from_ubx(message)
        raise ValueError('Cannot extract geo coordinates'
            f' from protocol {message.proto}')

    def __from_nmea(self, msg: Message) -> GeoCoordinates:
        nmea = msg.payload
        lat = self.__nmea.degmins_to_decdeg(nmea.lat, Direction.from_symbol(nmea.lat_dir))
        lon = self.__nmea.degmins_to_decdeg(nmea.lon, Direction.from_symbol(nmea.lon_dir))
        alt = D0 if not hasattr(nmea, 'alt') else self.__nmea.height_from_field(nmea.alt)
        return GeoCoordinates(lat=lat, lon=lon, alt=alt)

    def __from_ubx(self, msg: Message) -> GeoCoordinates:
        ubx = msg.payload
        lat = self.__ubx.integer_to_decdeg(ubx.lat, 0 if not hasattr(ubx, 'latHp') else ubx.latHp)
        lon = self.__ubx.integer_to_decdeg(ubx.lon, 0 if not hasattr(ubx, 'lonHp') else ubx.lonHp)
        alt = D0
        if hasattr(ubx, 'height'):
            alt_hp = 0 if not hasattr(ubx, 'heightHp') else ubx.heightHp
            alt = self.__ubx.height_from_field(ubx.height, alt_hp)
        return GeoCoordinates(lat=lat, lon=lon, alt=alt)
