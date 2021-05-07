'''
Message operators
'''

from typing import Tuple

from .status import Status
from .message import Message
from .message_editor import IMessageEditor
from .operator_iface import IMessageOperator
from .data_formatter import NMEADataFormatter, UBXDataFormatter
from .direction import CoordAxis, Direction
from .coordinate_offset import ICoordinateOffsetProvider

class NMEAOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a NMEA message by adding an offset
    '''

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: NMEADataFormatter,
        offset_provider: ICoordinateOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
        nmea = message.payload
        offset = self.__offset_provider.get_offset()
        hi_res = self.__formatter.is_highpres(nmea.lat) and self.__formatter.is_highpres(nmea.lon)
        lat = self.__formatter.degmins_to_decdeg(nmea.lat, Direction.from_symbol(nmea.lat_dir))
        lon = self.__formatter.degmins_to_decdeg(nmea.lon, Direction.from_symbol(nmea.lon_dir))
        tlat, tlat_d = self.__formatter.decdeg_to_degmins(lat + offset.lat, CoordAxis.LAT, hi_res)
        tlon, tlon_d = self.__formatter.decdeg_to_degmins(lon + offset.lon, CoordAxis.LON, hi_res)
        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'lat_dir': tlat_d.name,
            'lon_dir': tlon_d.name,
        })

class UBXOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a UBX message by adding an offset
    '''

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        offset_provider: ICoordinateOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
        ubx = message.payload
        offset = self.__offset_provider.get_offset()
        src_lat = self.__formatter.integer_to_decdeg(ubx.lat)
        src_lon = self.__formatter.integer_to_decdeg(ubx.lon)
        target_lat, _ = self.__formatter.decdeg_to_integer(src_lat + offset.lat)
        target_lon, _ = self.__formatter.decdeg_to_integer(src_lon + offset.lon)
        return self.__editor.set_fields(message, {
            'lat': target_lat,
            'lon': target_lon,
        })

class UBXHiResOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a hi res UBX message by adding an offset
    '''

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        offset_provider: ICoordinateOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed hi res version
        '''
        ubx = message.payload
        offset = self.__offset_provider.get_offset()
        lat = self.__formatter.integer_to_decdeg(ubx.lat, ubx.latHp)
        lon = self.__formatter.integer_to_decdeg(ubx.lon, ubx.lonHp)
        tlat, tlat_hp = self.__formatter.decdeg_to_integer(lat + offset.lat)
        tlon, tlon_hp = self.__formatter.decdeg_to_integer(lon + offset.lon)
        tlat, tlat_hp = self.__formatter.minimize_correction(tlat, tlat_hp)
        tlon, tlon_hp = self.__formatter.minimize_correction(tlon, tlon_hp)
        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'latHp': tlat_hp,
            'lonHp': tlon_hp
        })
