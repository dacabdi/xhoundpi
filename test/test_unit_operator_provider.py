# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock
from dataclasses import dataclass

from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.operator_provider import CoordinateOperationProvider

@dataclass
class UBXPayload:
    lat: int = 999
    lon: int = 111

@dataclass
class UBXHiResPayload:
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33

class test_CoordinateOperationProvider(unittest.TestCase):

    def test_get_operator(self):
        nmea_op = Mock()
        ubx_op = Mock()
        ubx_hires_op = Mock()
        provider = CoordinateOperationProvider(
            nmea_operator=nmea_op,
            ubx_operator=ubx_op,
            ubx_hires_operator=ubx_hires_op)
        self.assertEqual(nmea_op, provider.get_operator(Message(message_id=None, proto=ProtocolClass.NMEA, payload=None)))
        self.assertEqual(ubx_op, provider.get_operator(Message(message_id=None, proto=ProtocolClass.UBX, payload=UBXPayload())))
        self.assertEqual(ubx_hires_op, provider.get_operator(Message(message_id=None, proto=ProtocolClass.UBX, payload=UBXHiResPayload())))

    def test_get_operator_throws_if_impossible_protocol(self):
        operator = Mock()
        provider = CoordinateOperationProvider(
            nmea_operator=operator,
            ubx_operator=operator,
            ubx_hires_operator=operator)

        with self.assertRaises(ValueError) as context:
            provider.get_operator(Message(message_id=None, proto=ProtocolClass.NONE, payload=None))

        self.assertEqual("Cannot provide operator for protocol class 'ProtocolClass.NONE'",
            str(context.exception))
