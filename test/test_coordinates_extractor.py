# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from unittest.mock import Mock, call
from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal as D
from xhoundpi.direction import Direction
from xhoundpi.coordinates import GeoCoordinates

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.dmath import setup_common_context, DECIMAL0 as D0
from xhoundpi.coordinates_extractor import CoordinatesExtractor

setup_common_context()

@dataclass
class NMEAPayload:
    lat: str = '9801.12345'
    lon: str = '98701.12345'
    lat_dir: str = 'N'
    lon_dir: str = 'E'
    alt: str = '100.5'

@dataclass
class NMEAPayloadWithoutAlt:
    lat: str = '9801.12345'
    lon: str = '98701.12345'
    lat_dir: str = 'N'
    lon_dir: str = 'E'

@dataclass
class UBXPayload:
    lat: int = 999
    lon: int = 111
    height: int = 20

@dataclass
class UBXPayloadWithoutHeight:
    lat: int = 999
    lon: int = 111

@dataclass
class UBXPayloadHighPrec:
    # pylint: disable=too-many-instance-attributes
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33
    height: int = 20
    heightHp: int = 4

@dataclass
class UBXPayloadHighPrecWithoutHeight:
    # pylint: disable=too-many-instance-attributes
    lat: int = 999
    lon: int = 111
    latHp: int = 22
    lonHp: int = 33

class test_CoordinatesExtractor(unittest.TestCase):

    def test_extract_ubx_high_precision(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=Mock(),
            ubx_formatter=formatter)
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayloadHighPrec())

        result = extractor.extract_coordinates(msg)

        formatter.integer_to_decdeg.assert_has_calls([call(999, 22), call(111, 33)])
        formatter.height_from_field.assert_called_once_with(20, 4)
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D('0.3')), result)

    def test_extract_ubx_high_precision_without_height(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=Mock(),
            ubx_formatter=formatter)
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayloadHighPrecWithoutHeight())

        result = extractor.extract_coordinates(msg)

        formatter.integer_to_decdeg.assert_has_calls([call(999, 22), call(111, 33)])
        formatter.height_from_field.assert_not_called()
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D0), result)

    def test_extract_ubx(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=Mock(),
            ubx_formatter=formatter)
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayload())

        result = extractor.extract_coordinates(msg)

        formatter.integer_to_decdeg.assert_has_calls([call(999, 0), call(111, 0)])
        formatter.height_from_field.assert_called_once_with(20, 0)
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D('0.3')), result)

    def test_extract_ubx_without_height(self):
        formatter = Mock()
        formatter.integer_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=Mock(),
            ubx_formatter=formatter)
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.UBX,
            payload=UBXPayloadWithoutHeight())

        result = extractor.extract_coordinates(msg)

        formatter.integer_to_decdeg.assert_has_calls([call(999, 0), call(111, 0)])
        formatter.height_from_field.assert_not_called()
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D0), result)

    def test_extract_nmea(self):
        formatter = Mock()
        formatter.degmins_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=formatter,
            ubx_formatter=Mock())
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=NMEAPayload())

        result = extractor.extract_coordinates(msg)

        formatter.degmins_to_decdeg.assert_has_calls([call('9801.12345', Direction.N), call('98701.12345', Direction.E)])
        formatter.height_from_field.assert_called_once_with('100.5')
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D('0.3')), result)

    def test_extract_nmea_without_alt(self):
        formatter = Mock()
        formatter.degmins_to_decdeg = Mock(side_effect=[D('0.1'), D('0.2')])
        formatter.height_from_field = Mock(return_value=D('0.3'))
        extractor = CoordinatesExtractor(
            nmea_formatter=formatter,
            ubx_formatter=Mock())
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NMEA,
            payload=NMEAPayloadWithoutAlt())

        result = extractor.extract_coordinates(msg)

        formatter.degmins_to_decdeg.assert_has_calls([call('9801.12345', Direction.N), call('98701.12345', Direction.E)])
        formatter.height_from_field.assert_not_called()
        self.assertEqual(GeoCoordinates(D('0.1'), D('0.2'), D0), result)

    def test_non_supported_protocol(self):
        extractor = CoordinatesExtractor(
            nmea_formatter=Mock(),
            ubx_formatter=Mock())
        msg = Message(
            message_id=UUID('{12345678-1234-5678-1234-567812345678}'),
            proto=ProtocolClass.NONE,
            payload='dummy payload')

        with self.assertRaises(ValueError) as ctx:
            extractor.extract_coordinates(msg)

        self.assertEqual(str(ValueError(
            'Cannot extract geo coordinates'
            ' from protocol ProtocolClass.NONE')),
            str(ctx.exception))
