# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from dataclasses import dataclass
from unittest.mock import Mock

from xhoundpi.direction import CoordAxis, Direction
from xhoundpi.operator import (NMEAOffsetOperator,
                              UBXOffsetOperator,
                              UBXHiResOffsetOperator)
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

class test_NMEAOffsetOperator(unittest.TestCase):

    def test_apply_offset(self):
        formatter = Mock()
        formatter.is_highpres = Mock(return_value=False)
        formatter.degmins_to_decdeg = Mock(return_value=1.0)
        # TODO cycle the return values, investigate
        formatter.decdeg_to_degmins = Mock(return_value=('00010.12345', Direction.N))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        msg = Message(message_id=None, proto=None, payload=NMEAPayload())
        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            lat_offset=0.5,
            lon_offset=0.2)

        result = op.operate(msg)

        formatter.is_highpres.assert_called_once_with('9801.12345') # shortcircuit logic
        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Direction.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Direction.E)
        formatter.decdeg_to_degmins.assert_any_call(1.5, CoordAxis.LAT, False)
        formatter.decdeg_to_degmins.assert_called_with(1.2, CoordAxis.LON, False)
        editor.set_fields.assert_called_once_with(
            Message(message_id=None, proto=None, payload=NMEAPayload()),
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
        formatter.degmins_to_decdeg = Mock(return_value=1.0)
        # TODO cycle the return values, investigate
        formatter.decdeg_to_degmins = Mock(return_value=('00010.12345', Direction.N))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        msg = Message(message_id=None, proto=None, payload=NMEAPayload())
        op = NMEAOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            lat_offset=0.5,
            lon_offset=0.2)

        result = op.operate(msg)

        formatter.is_highpres.assert_any_call('9801.12345')
        formatter.is_highpres.assert_called_with('98701.12345')
        formatter.degmins_to_decdeg.assert_any_call('9801.12345', Direction.N)
        formatter.degmins_to_decdeg.assert_called_with('98701.12345', Direction.E)
        formatter.decdeg_to_degmins.assert_any_call(1.5, CoordAxis.LAT, True)
        formatter.decdeg_to_degmins.assert_called_with(1.2, CoordAxis.LON, True)
        editor.set_fields.assert_called_once_with(
            Message(message_id=None, proto=None, payload=NMEAPayload()),
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
        formatter.integer_to_decdeg = Mock(return_value=1.0)
        formatter.decdeg_to_integer = Mock(return_value=(100, 99))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        msg = Message(message_id=None, proto=None, payload=UBXPayload())
        op = UBXOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            lat_offset=0.5,
            lon_offset=0.2)

        result = op.operate(msg)

        formatter.integer_to_decdeg.assert_any_call(999)
        formatter.integer_to_decdeg.assert_called_with(111)
        formatter.decdeg_to_integer.assert_any_call(1.5)
        formatter.decdeg_to_integer.assert_called_with(1.2)
        editor.set_fields.assert_called_once_with(
            Message(message_id=None, proto=None, payload=UBXPayload()),
            {
                'lat': 100,
                'lon': 100,
            })
        self.assertEqual(result, 'new message')

class test_UBXHiResOffsetOperator(unittest.TestCase):

    def test_apply_offset_hi_res(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(return_value=1.0)
        formatter.decdeg_to_integer = Mock(return_value=(100, 99))
        formatter.minimize_correction = Mock(return_value=(101, -1))
        editor = Mock()
        editor.set_fields = Mock(return_value='new message')
        msg = Message(message_id=None, proto=None, payload=UBXPayload())
        op = UBXHiResOffsetOperator(
            msg_editor=editor,
            data_formatter=formatter,
            lat_offset=0.5,
            lon_offset=0.2)

        result = op.operate(msg)

        formatter.integer_to_decdeg.assert_any_call(999, 22)
        formatter.integer_to_decdeg.assert_called_with(111, 33)
        formatter.decdeg_to_integer.assert_any_call(1.5)
        formatter.decdeg_to_integer.assert_called_with(1.2)
        formatter.minimize_correction.assert_called_with(100, 99)
        editor.set_fields.assert_called_once_with(
            Message(message_id=None, proto=None, payload=UBXPayload()),
            {
                'lat': 101,
                'lon': 101,
                'lonHp': -1,
                'latHp': -1
            })
        self.assertEqual(result, 'new message')
