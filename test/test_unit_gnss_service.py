# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import uuid

from unittest.mock import Mock, patch
from xhoundpi.status import Status

from xhoundpi.async_ext import run_sync
from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.gnss_service import GnssService

class test_GnssService(unittest.TestCase):

    def test_read(self):
        gnss_client = Mock()
        gnss_protocol_classifier = Mock()
        gnss_protocol_classifier.classify = Mock(return_value=(b'\x24', ProtocolClass.NMEA))
        gnss_reader = Mock()
        gnss_reader.read_frame = Mock(return_value=b'\x24\x01\x08')
        gnss_parser = Mock()
        gnss_parser.parse = Mock(return_value='payload message')
        gnss_reader_provider = Mock()
        gnss_reader_provider.get_reader = Mock(return_value=gnss_reader)
        gnss_parser_provider = Mock()
        gnss_parser_provider.get_parser = Mock(return_value=gnss_parser)
        gnss_serializer_provider = Mock()

        with patch('uuid.uuid4', return_value=uuid.UUID('{12345678-1234-5678-1234-567812345678}')):
            gnss_service = GnssService(
                gnss_client=gnss_client,
                classifier=gnss_protocol_classifier,
                reader_provider=gnss_reader_provider,
                parser_provider=gnss_parser_provider,
                serializer_provider=gnss_serializer_provider)

            status, message = run_sync(gnss_service.read_message())
            expected = Message(proto=ProtocolClass.NMEA,
                payload='payload message',
                message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'))

        self.assertTrue(status.ok)
        self.assertEqual(status.error, None)
        self.assertEqual(message, expected)
        gnss_protocol_classifier.classify.assert_called_once_with(gnss_client)
        gnss_reader_provider.get_reader.assert_called_once_with(ProtocolClass.NMEA)
        gnss_parser_provider.get_parser.assert_called_once_with(ProtocolClass.NMEA)
        gnss_reader.read_frame.assert_called_once_with(b'\x24', gnss_client)
        gnss_parser.parse.assert_called_once_with(b'\x24\x01\x08')

    def test_read_error(self):
        gnss_client = Mock()
        gnss_protocol_classifier = Mock()
        gnss_protocol_classifier.classify = Mock(return_value=(b'\x24', ProtocolClass.NMEA))
        gnss_reader = Mock()
        gnss_reader.read_frame = Mock(return_value=b'\x24\x01\x08')
        gnss_parser = Mock()
        gnss_parser.parse = Mock(side_effect=Exception('Whoops!'))
        gnss_reader_provider = Mock()
        gnss_reader_provider.get_reader = Mock(return_value=gnss_reader)
        gnss_parser_provider = Mock()
        gnss_parser_provider.get_parser = Mock(return_value=gnss_parser)
        gnss_serializer_provider = Mock()
        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider,
            serializer_provider=gnss_serializer_provider)

        status, message = run_sync(gnss_service.read_message())

        self.assertEqual(status, Status(Exception('Whoops!')))
        self.assertEqual(message, None)
        gnss_protocol_classifier.classify.assert_called_once_with(gnss_client)
        gnss_reader_provider.get_reader.assert_called_once_with(ProtocolClass.NMEA)
        gnss_parser_provider.get_parser.assert_called_once_with(ProtocolClass.NMEA)
        gnss_reader.read_frame.assert_called_once_with(b'\x24', gnss_client)
        gnss_parser.parse.assert_called_once_with(b'\x24\x01\x08')

    def test_write(self):
        gnss_client = Mock()
        gnss_client.write = Mock(return_value=1)
        gnss_protocol_classifier = Mock()
        gnss_reader_provider = Mock()
        gnss_parser_provider = Mock()
        gnss_serializer = Mock()
        gnss_serializer.serialize = Mock(return_value=b'\x24\x23')
        gnss_serializer_provider = Mock()
        gnss_serializer_provider.get_serializer = Mock(return_value=gnss_serializer)
        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider,
            serializer_provider=gnss_serializer_provider)

        status, bytes_written = run_sync(gnss_service.write_message(Message(
            proto=ProtocolClass.UBX,
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            payload='test payload')))

        self.assertTrue(status.ok)
        self.assertEqual(status.error, None)
        self.assertEqual(bytes_written, 1)
        gnss_serializer_provider.get_serializer.assert_called_once_with(ProtocolClass.UBX)
        gnss_serializer.serialize.assert_called_once_with(
            Message(message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                    proto=ProtocolClass.UBX, payload='test payload'))
        gnss_client.write.assert_called_once_with(b'\x24\x23')

    def test_write_error(self):
        gnss_client = Mock()
        gnss_client.write = Mock(side_effect=Exception('Whoops!'))
        gnss_protocol_classifier = Mock()
        gnss_reader_provider = Mock()
        gnss_parser_provider = Mock()
        gnss_serializer = Mock()
        gnss_serializer.serialize = Mock(return_value=b'\x24\x23')
        gnss_serializer_provider = Mock()
        gnss_serializer_provider.get_serializer = Mock(return_value=gnss_serializer)
        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider,
            serializer_provider=gnss_serializer_provider)

        status, bytes_written = run_sync(gnss_service.write_message(Message(
            proto=ProtocolClass.UBX,
            message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
            payload='test payload')))

        self.assertEqual(Status(Exception('Whoops!')), status)
        self.assertEqual(bytes_written, 0)
        gnss_serializer_provider.get_serializer.assert_called_once_with(ProtocolClass.UBX)
        gnss_serializer.serialize.assert_called_once_with(
            Message(message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                    proto=ProtocolClass.UBX, payload='test payload'))
        gnss_client.write.assert_called_once_with(b'\x24\x23')
