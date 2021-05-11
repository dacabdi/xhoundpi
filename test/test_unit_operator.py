# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from xhoundpi.proto_class import ProtocolClass

from xhoundpi.coordinate_offset import CoordinateOffset
from xhoundpi.direction import CoordAxis, Direction
from xhoundpi.operator import NMEAOffsetOperator, UBXOffsetOperator, UBXHiResOffsetOperator
from xhoundpi.message import Message

@dataclass
class NMEAPayload:
    lat: str = '9801.12345'
    lon: str = '98701.12345'
    lat_dir: str = 'N'
    lon_dir: str = 'E'

@dataclass
class UBXPayload:
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33
    height: int = 20
    heightHp: int = 4
    hMSL: int = 30
    hMSLHp: int = 2

class test_NMEAOffsetOperator(unittest.TestCase):

    def test_apply_offset(self):
        formatter = Mock()
        formatter.is_highpres = Mock(return_value=False)
        formatter.degmins_to_decdeg = Mock(return_value=Decimal("1.0"))
        formatter.decdeg_to_degmins = Mock(return_value=('00010.12345', Direction.N))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        offset_provider = Mock()
        offset_provider.get_offset = Mock(
            return_value=CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("0.2"), alt=Decimal("0.1")))
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=NMEAPayload())
        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_provider)

        result = op.operate(msg)

        formatter.is_highpres.assert_called_once_with('9801.12345') # shortcircuit logic
        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Direction.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Direction.E)
        formatter.decdeg_to_degmins.assert_any_call(Decimal("1.5"), CoordAxis.LAT, False)
        formatter.decdeg_to_degmins.assert_called_with(Decimal('1.2'), CoordAxis.LON, False)
        offset_provider.get_offset.assert_called_once()
        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA,
                payload=NMEAPayload()),
            {
                'lat': '00010.12345',
                'lon': '00010.12345',
                'lat_dir': 'N',
                'lon_dir': 'N',
            })
        self.assertEqual(result, 'new message')

    def test_apply_offset_hi_res(self):
        formatter = Mock()
        formatter.is_highpres = Mock(return_value=True)
        formatter.degmins_to_decdeg = Mock(return_value=Decimal("1.0"))
        formatter.decdeg_to_degmins = Mock(return_value=('00010.12345', Direction.N))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        offset_provider = Mock()
        offset_provider.get_offset = Mock(
            return_value=CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("0.2"), alt=Decimal("0.1")))
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=NMEAPayload())
        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_provider)

        result = op.operate(msg)

        formatter.is_highpres.assert_any_call('9801.12345')
        formatter.is_highpres.assert_called_with('98701.12345')
        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Direction.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Direction.E)
        formatter.decdeg_to_degmins.assert_any_call(Decimal("1.5"), CoordAxis.LAT, True)
        formatter.decdeg_to_degmins.assert_called_with(Decimal("1.2"), CoordAxis.LON, True)
        offset_provider.get_offset.assert_called_once()
        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.NMEA,
                payload=NMEAPayload()),
            {
                'lat': '00010.12345',
                'lon': '00010.12345',
                'lat_dir': 'N',
                'lon_dir': 'N',
            })
        self.assertEqual(result, 'new message')

class test_UBXOffsetOperator(unittest.TestCase):

    def test_apply_offset(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(return_value=Decimal("1.0"))
        formatter.decdeg_to_integer = Mock(return_value=(100, 99))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        offset_provider = Mock()
        offset_provider.get_offset = Mock(
            return_value=CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("0.2"), alt=Decimal("0.1")))
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayload())
        op = UBXOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_provider)

        result = op.operate(msg)

        formatter.integer_to_decdeg.assert_any_call(999)
        formatter.integer_to_decdeg.assert_called_with(111)
        formatter.decdeg_to_integer.assert_any_call(Decimal("1.5"))
        formatter.decdeg_to_integer.assert_called_with(Decimal("1.2"))
        offset_provider.get_offset.assert_called_once()
        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayload()),
            {
                'lat': 100,
                'lon': 100,
            })
        self.assertEqual(result, 'new message')

class test_UBXHiResOffsetOperator(unittest.TestCase):

    def test_apply_offset_hi_res(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(return_value=Decimal("1.0"))
        formatter.decdeg_to_integer = Mock(return_value=(100, 99))
        formatter.minimize_correction = Mock(return_value=(101, -1))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        offset_provider = Mock()
        offset_provider.get_offset = Mock(
            return_value=CoordinateOffset(lat=Decimal("0.5"), lon=Decimal("0.2"), alt=Decimal("0.1")))
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayload())
        op = UBXHiResOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            offset_provider=offset_provider)

        result = op.operate(msg)

        formatter.integer_to_decdeg.assert_any_call(999, 22)
        formatter.integer_to_decdeg.assert_called_with(111, 33)
        formatter.decdeg_to_integer.assert_any_call(Decimal("1.5"))
        formatter.decdeg_to_integer.assert_called_with(Decimal("1.2"))
        formatter.minimize_correction.assert_called_with(100, 99)
        offset_provider.get_offset.assert_called_once()
        editor.set_fields.assert_called_once_with(
            Message(
                message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=UBXPayload()),
            {
                'lat': 101,
                'lon': 101,
                'lonHp': -1,
                'latHp': -1
            })
        self.assertEqual(result, 'new message')
