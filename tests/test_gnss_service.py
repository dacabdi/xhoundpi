import unittest
import asyncio
from io import BytesIO

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

        self.assertEqual(gnss_inbound_queue.qsize(), 0)
        run_sync(gnss_service.read_message())
        self.assertEqual(gnss_inbound_queue.qsize(), 1)
        self.assertEqual(run_sync(gnss_inbound_queue.get()), Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x08', msg=b'\x01\x08'))

        self.assertEqual(gnss_inbound_queue.qsize(), 0)
        run_sync(gnss_service.read_message())
        run_sync(gnss_service.read_message())
        self.assertEqual(gnss_inbound_queue.qsize(), 2)
        self.assertEqual(run_sync(gnss_inbound_queue.get()), Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\xff', msg=b'\x01\xff'))
        self.assertEqual(run_sync(gnss_inbound_queue.get()), Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x1f', msg=b'\x01\x1f'))
        self.assertEqual(gnss_outbound_queue.qsize(), 0)

    def test_write(self):
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

        self.assertEqual(writing_stream.getbuffer().nbytes, 0, "nothing has been written, outgoing buffer must be empty")
        write_task = asyncio.get_event_loop().create_task(gnss_service.write_message())
        self.assertFalse(write_task.done(), "the task is started but the queue is empty, should be pending")
        run_sync(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x01', frame=b'\x01\x0a', msg=None)))
        run_sync(asyncio.wait_for(write_task, timeout=1))
        self.assertTrue(write_task.done(), "an outbound msg has been enqueued, the read task must have finished within reasonable time")
        self.assertFalse(write_task.cancelled(), "must have finished successfuly, not because of cancellation")
        self.assertEqual(writing_stream.getvalue(), b'\x01\x0a', "the buffer must contain message frame")

