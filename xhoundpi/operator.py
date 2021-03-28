""" Message operators """

from .message import Message
from .message_editor import IMessageEditor
from .operator_iface import IMessageOperator
from .data_formatter import (NMEADataFormatter,
                            UBXDataFormatter)
from .direction import (CoordAxis,
                       Direction)

class NMEAOffsetOperator(IMessageOperator):
    """
    Correct coordinates of a NMEA message by adding an offset
    """

    def __init__(self,
        msg_editor: IMessageEditor,
        data_formatter: NMEADataFormatter,
        lat_offset: float,
        lon_offset: float):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__lat = lat_offset
        self.__lon = lon_offset

    def operate(self, message: Message) -> Message:
        """
        Operate on the message and return the transformed version
        """
        nmea = message.payload
        hi_res = self.__formatter.is_highpres(nmea.lat) and self.__formatter.is_highpres(nmea.lon)
        lat = self.__formatter.degmins_to_decdeg(nmea.lat, Direction.from_symbol(nmea.lat_dir))
        lon = self.__formatter.degmins_to_decdeg(nmea.lon, Direction.from_symbol(nmea.lon_dir))
        tlat, tlat_d = self.__formatter.decdeg_to_degmins(lat + self.__lat, CoordAxis.LAT, hi_res)
        tlon, tlon_d = self.__formatter.decdeg_to_degmins(lon + self.__lon, CoordAxis.LON, hi_res)
        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'lat_dir': tlat_d.name,
            'lon_dir': tlon_d.name,
        })

class UBXOffsetOperator(IMessageOperator):
    """
    Correct coordinates of a UBX message by adding an offset
    """

    def __init__(self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        lat_offset: float,
        lon_offset: float):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__lat = lat_offset
        self.__lon = lon_offset

    def operate(self, message: Message) -> Message:
        """
        Operate on the message and return the transformed version
        """
        ubx = message.payload
        src_lat = self.__formatter.integer_to_decdeg(ubx.lat)
        src_lon = self.__formatter.integer_to_decdeg(ubx.lon)
        target_lat, _ = self.__formatter.decdeg_to_integer(src_lat + self.__lat)
        target_lon, _ = self.__formatter.decdeg_to_integer(src_lon + self.__lon)
        return self.__editor.set_fields(message, {
            'lat': target_lat,
            'lon': target_lon,
        })

class UBXHiResOffsetOperator(IMessageOperator):
    """
    Correct coordinates of a hi res UBX message by adding an offset
    """

    def __init__(self,
        msg_editor: IMessageEditor,
        data_formatter: UBXDataFormatter,
        lat_offset: float,
        lon_offset: float):
        self.__editor = msg_editor
        self.__formatter = data_formatter
        self.__lat = lat_offset
        self.__lon = lon_offset

    def operate(self, message: Message) -> Message:
        """
        Operate on the message and return the transformed hi res version
        """
        ubx = message.payload
        lat = self.__formatter.integer_to_decdeg(ubx.lat, ubx.latHp)
        lon = self.__formatter.integer_to_decdeg(ubx.lon, ubx.lonHp)
        tlat, tlat_hp = self.__formatter.decdeg_to_integer(lat + self.__lat)
        tlon, tlon_hp = self.__formatter.decdeg_to_integer(lon + self.__lon)
        return self.__editor.set_fields(message, {
            'lat': tlat,
            'lon': tlon,
            'latHp': tlon_hp,
            'lonHp': tlat_hp
        })
