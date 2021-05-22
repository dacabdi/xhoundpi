# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from dataclasses import dataclass
from decimal import Decimal as D
from uuid import UUID
from xhoundpi.proto_class import ProtocolClass

from xhoundpi.coordinates_offset import GeoCoordinates
from xhoundpi.direction import CoordAxis, Direction as Dir
from xhoundpi.operator import NMEAOffsetOperator, UBXOffsetOperator, UBXHiResOffsetOperator
from xhoundpi.message import Message

@dataclass
class NMEAPayload:
    lat: str = '9801.12345'
    lon: str = '98701.12345'
    lat_dir: str = 'N'
    lon_dir: str = 'E'
    alt: str = '100.5'
    alt_ref: str = '10.4'

@dataclass
class NMEAPayloadWithoutAlt:
    lat: str = '9801.12345'
    lon: str = '98701.12345'
    lat_dir: str = 'N'
    lon_dir: str = 'E'

@dataclass
class UBXPayload:
    # pylint: disable=too-many-instance-attributes
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33
    height: int = 20
    heightHp: int = 4
    hMSL: int = 30
    hMSLHp: int = 2

@dataclass
class UBXPayloadWithoutHeight:
    # pylint: disable=too-many-instance-attributes
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33

class test_NMEAOffsetOperator(unittest.TestCase):

    @staticmethod
    def create_formatter(hires: bool = False):
        formatter = Mock()
        formatter.is_highpres = Mock(return_value=hires)
        formatter.degmins_to_decdeg = Mock(side_effect=[D('123.45'), D('20.2')])
        formatter.decdeg_to_degmins = Mock(side_effect=[('01010.12345', Dir.N), ('0020.12345', Dir.E)])
        formatter.height_from_field = Mock(side_effect=[D('100.5'), D('10.4')])
        formatter.height_to_field = Mock(side_effect=['101.6', '11.5'])
        return formatter

    @staticmethod
    def create_editor():
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        return editor

    @staticmethod
    def create_offset_provider():
        offset_provider = Mock()
        offset_provider.get_offset = Mock(
            return_value=GeoCoordinates(lat=D('0.5'), lon=D('0.2'), alt=D('1.1')))
        return offset_provider

    @staticmethod
    def create_nmea_message(without_alt: bool = False):
        return Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=NMEAPayloadWithoutAlt() if without_alt else NMEAPayload())

    def test_apply_offset(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_nmea_message()

        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        formatter.is_highpres.assert_called_once_with('9801.12345') # shortcircuit logic
        offset_prov.get_offset.assert_called_once()

        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Dir.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Dir.E)

        formatter.decdeg_to_degmins.assert_any_call(D('123.95'), CoordAxis.LAT, False)
        formatter.decdeg_to_degmins.assert_called_with(D('20.4'), CoordAxis.LON, False)

        formatter.height_from_field.assert_any_call('100.5')
        formatter.height_from_field.assert_called_with('10.4')

        formatter.height_to_field.assert_any_call(D('101.6'))
        formatter.height_to_field.assert_called_with(D('11.5'))

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA,
                payload=NMEAPayload()),
            {
                'lat': '01010.12345',
                'lon': '0020.12345',
                'lat_dir': 'N',
                'lon_dir': 'E',
                'alt': '101.6',
                'alt_ref': '11.5'
            })
        self.assertEqual(result, 'new message')

    def test_apply_offset_no_optional_fields(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_nmea_message(without_alt=True)

        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        formatter.is_highpres.assert_called_once_with('9801.12345') # shortcircuit logic
        offset_prov.get_offset.assert_called_once()

        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Dir.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Dir.E)

        formatter.decdeg_to_degmins.assert_any_call(D('123.95'), CoordAxis.LAT, False)
        formatter.decdeg_to_degmins.assert_called_with(D('20.4'), CoordAxis.LON, False)

        formatter.height_from_field.assert_not_called()
        formatter.height_to_field.assert_not_called()

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA,
                payload=NMEAPayloadWithoutAlt()),
            {
                'lat': '01010.12345',
                'lon': '0020.12345',
                'lat_dir': 'N',
                'lon_dir': 'E',
            })
        self.assertEqual(result, 'new message')

    def test_apply_offset_hi_res(self):
        formatter = self.create_formatter(hires=True)
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_nmea_message()

        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        formatter.is_highpres.assert_any_call('9801.12345')
        formatter.is_highpres.assert_called_with('98701.12345')

        offset_prov.get_offset.assert_called_once()

        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Dir.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Dir.E)

        formatter.decdeg_to_degmins.assert_any_call(D('123.95'), CoordAxis.LAT, True)
        formatter.decdeg_to_degmins.assert_called_with(D('20.4'), CoordAxis.LON, True)

        formatter.height_from_field.assert_any_call('100.5')
        formatter.height_from_field.assert_called_with('10.4')

        formatter.height_to_field.assert_any_call(D('101.6'))
        formatter.height_to_field.assert_called_with(D('11.5'))

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA,
                payload=NMEAPayload()),
            {
                'lat': '01010.12345',
                'lon': '0020.12345',
                'lat_dir': 'N',
                'lon_dir': 'E',
                'alt': '101.6',
                'alt_ref': '11.5'
            })
        self.assertEqual(result, 'new message')

class test_UBXOffsetOperator(unittest.TestCase):

    @staticmethod
    def create_formatter():
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('1.0'), D('2.0')])
        formatter.decdeg_to_integer = Mock(side_effect=[(100, 99), (-10,-30)])
        formatter.height_from_field = Mock(side_effect=[D('3.0'), D('-4')])
        formatter.height_to_field = Mock(side_effect=[(1,2), (3,4)])
        formatter.minimize_correction = Mock(side_effect=[(99, -1), (-10, -30)])
        return formatter

    @staticmethod
    def create_editor():
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        return editor

    @staticmethod
    def create_offset_provider():
        provider = Mock()
        provider.get_offset = Mock(return_value=GeoCoordinates(lat=D("0.5"), lon=D("0.2"), alt=D("0.1")))
        return provider

    @staticmethod
    def create_message(without_height: bool = False):
        return Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayloadWithoutHeight() if without_height else UBXPayload())

    def test_apply_offset(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_message()

        op = UBXOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        offset_prov.get_offset.assert_called_once()

        formatter.integer_to_decdeg.assert_any_call(999)
        formatter.integer_to_decdeg.assert_called_with(111)

        formatter.decdeg_to_integer.assert_any_call(D('1.5'))
        formatter.decdeg_to_integer.assert_called_with(D('2.2'))

        formatter.height_from_field.assert_any_call(20)
        formatter.height_from_field.assert_called_with(30)

        formatter.height_to_field.assert_any_call(D('3.1'))
        formatter.height_to_field.assert_called_with(D('-3.9'))

        formatter.height_to_

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayload()),
            {
                'lat': 100,
                'lon': -10,
                'height' : 99,
                'hMSL' : -10,
            })
        self.assertEqual(result, 'new message')

    def test_apply_offset_no_optional_fields(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_message(without_height=True)

        op = UBXOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        offset_prov.get_offset.assert_called_once()

        formatter.integer_to_decdeg.assert_any_call(999)
        formatter.integer_to_decdeg.assert_called_with(111)

        formatter.decdeg_to_integer.assert_any_call(D('1.5'))
        formatter.decdeg_to_integer.assert_called_with(D('2.2'))

        formatter.height_from_field.assert_not_called()
        formatter.height_to_field.assert_not_called()

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayloadWithoutHeight()),
            {
                'lat': 100,
                'lon': -10,
            })
        self.assertEqual(result, 'new message')

class test_UBXHiResOffsetOperator(unittest.TestCase):

    @staticmethod
    def create_formatter():
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('1.0'), D('2.0')])
        formatter.decdeg_to_integer = Mock(side_effect=[(100, 99), (-10,-30)])
        formatter.height_from_field = Mock(side_effect=[D('3.0'), D('-4')])
        formatter.height_to_field = Mock(side_effect=[(1,2), (3,4)])
        formatter.minimize_correction = Mock(side_effect=[(99, -1), (-10, -30), (2, 1), (4, 3)])
        return formatter

    @staticmethod
    def create_editor():
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        return editor

    @staticmethod
    def create_offset_provider():
        provider = Mock()
        provider.get_offset = Mock(return_value=GeoCoordinates(lat=D("0.5"), lon=D("0.2"), alt=D("0.1")))
        return provider

    @staticmethod
    def create_message(without_height: bool = False):
        return Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayloadWithoutHeight() if without_height else UBXPayload())

    def test_apply_offset(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_message()

        op = UBXHiResOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        offset_prov.get_offset.assert_called_once()

        formatter.integer_to_decdeg.assert_any_call(999, 22)
        formatter.integer_to_decdeg.assert_called_with(111, 33)

        formatter.decdeg_to_integer.assert_any_call(D('1.5'))
        formatter.decdeg_to_integer.assert_called_with(D('2.2'))

        formatter.height_from_field.assert_any_call(20, 4)
        formatter.height_from_field.assert_called_with(30, 2)

        formatter.height_to_field.assert_any_call(D('3.1'))
        formatter.height_to_field.assert_called_with(D('-3.9'))

        formatter.minimize_correction.assert_any_call(100, 99, midpoint=50)
        formatter.minimize_correction.assert_any_call(-10, -30, midpoint=50)
        formatter.minimize_correction.assert_any_call(1, 2, midpoint=5)
        formatter.minimize_correction.assert_called_with(3, 4, midpoint=5)

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayload()),
            {
                'lat': 99,
                'latHp': -1,
                'lon': -10,
                'lonHp': -30,
                'height' : 2,
                'heightHp' : 1,
                'hMSL' : 4,
                'hMSLHp' : 3,
            })
        self.assertEqual(result, 'new message')

    def test_apply_offset_no_optional_fields(self):
        formatter = self.create_formatter()
        editor = self.create_editor()
        offset_prov = self.create_offset_provider()
        msg = self.create_message(without_height=True)

        op = UBXHiResOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_prov)

        result = op.operate(msg)

        offset_prov.get_offset.assert_called_once()

        formatter.integer_to_decdeg.assert_any_call(999, 22)
        formatter.integer_to_decdeg.assert_called_with(111, 33)

        formatter.decdeg_to_integer.assert_any_call(D('1.5'))
        formatter.decdeg_to_integer.assert_called_with(D('2.2'))

        formatter.minimize_correction.assert_any_call(100, 99, midpoint=50)
        formatter.minimize_correction.assert_called_with(-10, -30, midpoint=50)

        formatter.height_from_field.assert_not_called()
        formatter.height_to_field.assert_not_called()

        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayloadWithoutHeight()),
            {
                'lat': 99,
                'latHp': -1,
                'lon': -10,
                'lonHp': -30,
            })
        self.assertEqual(result, 'new message')
