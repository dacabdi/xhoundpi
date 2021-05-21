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
        # TODO add alt and alt_ref (prop ubx)
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
        offset_provider: ICoordinatesOffsetProvider):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__offset_provider = offset_provider

    def operate(self, message: Message) -> Tuple[Status, Message]:
        '''
        Operate on the message and return the transformed version
        '''
        ubx = message.payload

        lat = self.__formatter.integer_to_decdeg(ubx.lat)
        lon = self.__formatter.integer_to_decdeg(ubx.lon)
        height = ubx.height
        hmsl = ubx.hMSL

        offset = self.__offset_provider.get_offset()

        tlat, _ = self.__formatter.decdeg_to_integer(lat + offset.lat)
        tlon, _ = self.__formatter.decdeg_to_integer(lon + offset.lon)
        theight, _ = self.__formatter.height_mm_to_integer(height + offset.alt)
        thmsl, _ = self.__formatter.height_mm_to_integer(hmsl + offset.alt)

        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'height': theight,
            'hMSL': thmsl,
        })

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
        ubx = message.payload

        # get current data
        lat = self.__formatter.integer_to_decdeg(ubx.lat, ubx.latHp)
        lon = self.__formatter.integer_to_decdeg(ubx.lon, ubx.lonHp)
        height = self.__formatter.integer_to_height_mm(ubx.height, ubx.heightHp)
        hmsl = self.__formatter.integer_to_height_mm(ubx.hMSL, ubx.hMSLHp)

        # get offset
        offset = self.__offset_provider.get_offset()

        # calculate offsets
        tlat, tlat_hp = self.__formatter.decdeg_to_integer(lat + offset.lat)
        tlon, tlon_hp = self.__formatter.decdeg_to_integer(lon + offset.lon)
        thei, thei_hp = self.__formatter.height_mm_to_integer(height + offset.alt)
        thms, thms_hp = self.__formatter.height_mm_to_integer(hmsl + offset.alt)

        # minimize hi pres field correction delta
        tlat, tlat_hp = self.__formatter.minimize_correction(tlat, tlat_hp, midpoint=self.LATLON_MP)
        tlon, tlon_hp = self.__formatter.minimize_correction(tlon, tlon_hp, midpoint=self.LATLON_MP)
        thei, thei_hp = self.__formatter.minimize_correction(thei, thei_hp, midpoint=self.HEIGHT_MP)
        thms, thms_hp = self.__formatter.minimize_correction(thms, thms_hp, midpoint=self.HEIGHT_MP)

        # edit message
        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'latHp': tlat_hp,
            'lonHp': tlon_hp,
            'height': thei,
            'heightHp': thei_hp,
            'hMSL': thms,
            'hMSLHp': thms_hp,
        })
