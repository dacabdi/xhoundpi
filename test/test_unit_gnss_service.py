import unittest
from io import BytesIO
from unittest.mock import MagicMock, Mock

from xhoundpi.async_ext import run_sync
from xhoundpi.message import Message
from xhoundpi.serial import StubSerial
from xhoundpi.gnss_client import GnssClient
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import StubProtocolClassifier
from xhoundpi.proto_reader import StubProtocolReaderProvider, StubProtocolReader
from xhoundpi.proto_parser import StubParserProvider, StubProtocolParser
from xhoundpi.gnss_service import GnssService

class test_GnssService(unittest.TestCase):

    def test_read(self):
        reading_stream = BytesIO(bytes.fromhex('01 08 01 FF 01 1F'))
        writing_stream = BytesIO()
        gnss_serial = StubSerial(rx=reading_stream, tx=writing_stream)
        gnss_client = GnssClient(gnss_serial)

        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_reader = StubProtocolReader(message_length=1, expected_header=b'\x01')
        gnss_reader_provider = StubProtocolReaderProvider(gnss_reader)
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider)

        self.assertEqual(run_sync(gnss_service.read_message()), Message(proto=ProtocolClass.NONE, payload=b'\x01\x08'))
        self.assertEqual(run_sync(gnss_service.read_message()), Message(proto=ProtocolClass.NONE, payload=b'\x01\xff'))
        self.assertEqual(run_sync(gnss_service.read_message()), Message(proto=ProtocolClass.NONE, payload=b'\x01\x1f'))

    def test_write(self):
        reading_stream = BytesIO()
        writing_stream = BytesIO()
        gnss_serial = StubSerial(rx=reading_stream, tx=writing_stream)
        gnss_client = GnssClient(gnss_serial)

        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_reader = StubProtocolReader(message_length=1, expected_header=b'\x01')
        gnss_reader_provider = StubProtocolReaderProvider(gnss_reader)
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider)

        mock_payload = Mock()
        mock_payload.serialize = MagicMock(return_value=b'\x01\x0a')

        self.assertEqual(writing_stream.getbuffer().nbytes, 0)
        self.assertEqual(run_sync(gnss_service.write_message(Message(proto=ProtocolClass.NONE, payload=mock_payload))), 2)
        mock_payload.serialize.assert_called_once()

        mock_payload.serialize = MagicMock(return_value=b'\x07\x0b\x00')

        self.assertEqual(writing_stream.getbuffer().nbytes, 2)
        self.assertEqual(run_sync(gnss_service.write_message(Message(proto=ProtocolClass.NONE, payload=mock_payload))), 3)
        mock_payload.serialize.assert_called_once()

        self.assertEqual(writing_stream.getbuffer().nbytes, 5)
        self.assertEqual(writing_stream.getvalue(), b'\x01\x0a\x07\x0b\x00')
