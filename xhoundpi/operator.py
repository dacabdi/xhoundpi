'''
Message operators
'''

from typing import Any, Dict, Tuple

from .status import Status
from .message import Message
from .message_editor import IMessageEditor
from .operator_iface import IMessageOperator
from .data_formatter import NMEADataFormatter, UBXDataFormatter
from .direction import CoordAxis, Direction
from .coordinates import GeoCoordinates
from .coordinates_offset import ICoordinatesOffsetProvider

class NMEAOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a NMEA message by adding an offset
    '''

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: NMEADataFormatter,
        offset_provider: ICoordinatesOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
        offset =  self.__offset_provider.get_offset()
        edited =  self.__common(message, offset) | self.__optional(message, offset)
        return self.__editor.set_fields(message, edited)

    def __common(self, message: Message, offset: GeoCoordinates) -> Dict[str, str]:
        nmea = message.payload
        hi_res = self.__formatter.is_highpres(nmea.lat) and self.__formatter.is_highpres(nmea.lon)
        lat = self.__formatter.degmins_to_decdeg(nmea.lat, Direction.from_symbol(nmea.lat_dir))
        lon = self.__formatter.degmins_to_decdeg(nmea.lon, Direction.from_symbol(nmea.lon_dir))
        tlat, tlat_d = self.__formatter.decdeg_to_degmins(lat + offset.lat, CoordAxis.LAT, hi_res)
        tlon, tlon_d = self.__formatter.decdeg_to_degmins(lon + offset.lon, CoordAxis.LON, hi_res)
        return {
            'lat': tlat,
            'lon': tlon,
            'lat_dir': tlat_d.name,
            'lon_dir': tlon_d.name,
        }

    def __optional(self, message: Message, offset: GeoCoordinates) -> Dict[str, str]:
        nmea = message.payload
        result = {}
        if hasattr(nmea, 'alt'):
            alt = self.__formatter.height_from_field(nmea.alt)
            talt = self.__formatter.height_to_field(alt + offset.alt)
            result |= { 'alt': talt }
        if hasattr(nmea, 'alt_ref'):
            alt_ref = self.__formatter.height_from_field(nmea.alt_ref)
            talt_ref = self.__formatter.height_to_field(alt_ref + offset.alt)
            result |= { 'alt_ref': talt_ref }
        return result

class UBXOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a UBX message by adding an offset
    '''

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        offset_provider: ICoordinatesOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
        offset = self.__offset_provider.get_offset()
        edited = self.__common(message, offset) | self.__optional(message, offset)
        return self.__editor.set_fields(message, edited)

    def __common(self, message: Message, offset: GeoCoordinates) -> Dict[str, Any]:
        ubx = message.payload
        lat = self.__formatter.integer_to_decdeg(ubx.lat)
        lon = self.__formatter.integer_to_decdeg(ubx.lon)
        tlat, _ = self.__formatter.decdeg_to_integer(lat + offset.lat)
        tlon, _ = self.__formatter.decdeg_to_integer(lon + offset.lon)
        return {
            'lat': tlat,
            'lon': tlon,
        }

    def __optional(self, message: Message, offset: GeoCoordinates) -> Dict[str, Any]:
        ubx = message.payload
        result = {}
        if hasattr(ubx, 'height'):
            height = self.__formatter.height_from_field(ubx.height)
            theight, _ = self.__formatter.height_to_field(height + offset.alt)
            result |= { 'height' : theight }
        if hasattr(ubx, 'hMSL'):
            hmsl = self.__formatter.height_from_field(ubx.hMSL)
            thmsl, _ = self.__formatter.height_to_field(hmsl + offset.alt)
            result |= { 'hMSL' : thmsl }
        return result

class UBXHiResOffsetOperator(IMessageOperator):
    '''
    Correct coordinates of a hi res UBX message by adding an offset
    '''

    LATLON_MP = 50
    HEIGHT_MP = 5

    def __init__(
        self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        offset_provider: ICoordinatesOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    # pylint: disable=too-many-locals
    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed hi res version
        '''
        offset = self.__offset_provider.get_offset()
        edited = self.__common(message, offset) | self.__optional(message, offset)
        return self.__editor.set_fields(message, edited)

    def __common(self, message: Message, offset: GeoCoordinates) -> Dict[str, Any]:
        ubx = message.payload
        # extract data
        lat = self.__formatter.integer_to_decdeg(ubx.lat, ubx.latHp)
        lon = self.__formatter.integer_to_decdeg(ubx.lon, ubx.lonHp)
        # calculate offsets
        tlat, tlat_hp = self.__formatter.decdeg_to_integer(lat + offset.lat)
        tlon, tlon_hp = self.__formatter.decdeg_to_integer(lon + offset.lon)
        # minimize hi pres correction delta
        tlat, tlat_hp = self.__formatter.minimize_correction(tlat, tlat_hp, midpoint=self.LATLON_MP)
        tlon, tlon_hp = self.__formatter.minimize_correction(tlon, tlon_hp, midpoint=self.LATLON_MP)
        return {
            'lat': tlat,
            'lon': tlon,
            'latHp': tlat_hp,
            'lonHp': tlon_hp,
        }

    def __optional(self, message: Message, offset: GeoCoordinates) -> Dict[str, Any]:
        # pylint: disable=line-too-long
        ubx = message.payload
        result = {}
        if hasattr(ubx, 'height') and hasattr(ubx, 'heightHp'):
            height = self.__formatter.height_from_field(ubx.height)
            theight, theight_hp = self.__formatter.height_to_field(height + offset.alt)
            theight, theight_hp = self.__formatter.minimize_correction(theight, theight_hp, midpoint=self.HEIGHT_MP)
            result |= { 'height' : theight, 'heightHp' : theight_hp }
        if hasattr(ubx, 'hMSL') and hasattr(ubx, 'hMSLHp'):
            hmsl = self.__formatter.height_from_field(ubx.hMSL)
            thmsl, thmsl_hp = self.__formatter.height_to_field(hmsl + offset.alt)
            thmsl, thmsl_hp = self.__formatter.minimize_correction(thmsl, thmsl_hp, midpoint=self.HEIGHT_MP)
            result |= { 'hMSL' : thmsl, 'hMSLHp': thmsl_hp }
        return result
