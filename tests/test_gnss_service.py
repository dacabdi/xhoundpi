import unittest
from io import BytesIO

import asyncio
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
        # arrange
        reading_stream = BytesIO(bytes.fromhex('01 08 01 FF 01 1F'))
        writing_stream = BytesIO()
        gnss_serial = StubSerial(rx=reading_stream, tx=writing_stream)
        gnss_client = GnssClient(gnss_serial)

        gnss_inbound_queue = asyncio.queues.Queue(3)
        gnss_outbound_queue = asyncio.queues.Queue(3)
        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_reader = StubProtocolReader(message_length=1, expected_header=b'\x01')
        gnss_reader_provider = StubProtocolReaderProvider(gnss_reader)
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            inbound_queue=gnss_inbound_queue,
            outbound_queue=gnss_outbound_queue,
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider)

        # act
        loop = asyncio.get_event_loop()
        initial_inbound_size = gnss_inbound_queue.qsize()
        service = loop.create_task(gnss_service.run())
        msg1 = loop.run_until_complete(gnss_inbound_queue.get())
        msg2 = loop.run_until_complete(gnss_inbound_queue.get())
        msg3 = loop.run_until_complete(gnss_inbound_queue.get())
        service.cancel()

        #assert
        self.assertEqual(gnss_outbound_queue.qsize(), 0)
        self.assertTrue(service.cancelled)
        self.assertEqual(initial_inbound_size, 0)
        self.assertEqual(msg1, Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x08', msg=b'\x01\x08'))
        self.assertEqual(msg2, Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\xff', msg=b'\x01\xff'))
        self.assertEqual(msg3, Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x1f', msg=b'\x01\x1f'))

    def test_write(self):
        # arrange
        reading_stream = BytesIO()
        writing_stream = BytesIO()
        gnss_serial = StubSerial(rx=reading_stream, tx=writing_stream)
        gnss_client = GnssClient(gnss_serial)

        gnss_inbound_queue = asyncio.queues.Queue(3)
        gnss_outbound_queue = asyncio.queues.Queue(3)
        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_reader = StubProtocolReader(message_length=1, expected_header=b'\x01')
        gnss_reader_provider = StubProtocolReaderProvider(gnss_reader)
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            inbound_queue=gnss_inbound_queue,
            outbound_queue=gnss_outbound_queue,
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_reader_provider,
            parser_provider=gnss_parser_provider)

        # act
        loop = asyncio.get_event_loop()
        initial_outbound_size = gnss_outbound_queue.qsize()
        service = loop.create_task(gnss_service.run())
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x0a', msg=None)))
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\xff', msg=None)))
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x1f', msg=None)))
        service.cancel()

        #assert
        self.assertTrue(service.cancelled)
        self.assertEqual(gnss_outbound_queue.qsize(), 0)
        self.assertEqual(initial_outbound_size, 0)
        self.assertEqual(b'\x01\x0a\x01\xff\x01\x1f', writing_stream.getvalue())
