from asyncio.futures import Future
import unittest
from io import BytesIO

import asyncio
from xhoundpi.message import Message
from xhoundpi.serial import StubSerial
from xhoundpi.gnss_client import GnssClient
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_parser import StubProtocolClassifier, StubParserProvider, StubProtocolParser
from xhoundpi.gnss_service import GnssService

class test_GnssService(unittest.TestCase):

    def test_read(self):
        # TODO start using unittest.mock's MagicMock
        rx = BytesIO(bytes.fromhex('01 0A 0B FF 0D 1F'))
        tx = BytesIO()
        gnss_serial = StubSerial(rx=rx, tx=tx)
        gnss_inbound_queue = asyncio.queues.Queue(10)
        gnss_outbound_queue = asyncio.queues.Queue(10)
        gnss_client = GnssClient(gnss_serial)
        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            inbound_queue=gnss_inbound_queue,
            outbound_queue=gnss_outbound_queue,
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
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
        self.assertEqual(msg1, Message(proto=ProtocolClass.NONE, header=[0x01], raw=[0x0A], msg=None))
        self.assertEqual(msg2, Message(proto=ProtocolClass.NONE, header=[0x0B], raw=[0xFF], msg=None))
        self.assertEqual(msg3, Message(proto=ProtocolClass.NONE, header=[0x0D], raw=[0x1F], msg=None))

    def test_write(self):
        # TODO start using unittest.mock's MagicMock
        rx = BytesIO(bytes.fromhex('01 0A 0B FF 0D 1F'))
        tx = BytesIO()
        gnss_serial = StubSerial(rx=rx, tx=tx)
        gnss_inbound_queue = asyncio.queues.Queue(10)
        gnss_outbound_queue = asyncio.queues.Queue(10)
        gnss_client = GnssClient(gnss_serial)
        gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
        gnss_parser_stub = StubProtocolParser()
        gnss_parser_provider = StubParserProvider(gnss_parser_stub)
        gnss_service = GnssService(
            inbound_queue=gnss_inbound_queue,
            outbound_queue=gnss_outbound_queue,
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            parser_provider=gnss_parser_provider)

        # act
        loop = asyncio.get_event_loop()
        initial_outbound_size = gnss_outbound_queue.qsize()
        service = loop.create_task(gnss_service.run())
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x01', raw=b'\x0a', msg=None)))
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x0b', raw=b'\xff', msg=None)))
        loop.run_until_complete(gnss_outbound_queue.put(Message(proto=ProtocolClass.NONE, header=b'\x0d', raw=b'\x1f', msg=None)))
        service.cancel()

        #assert
        self.assertTrue(service.cancelled)
        self.assertEqual(gnss_outbound_queue.qsize(), 0)
        self.assertEqual(initial_outbound_size, 0)
        self.assertEqual(b'\x01\x0a\x0b\xff\x0d\x1f', tx.getvalue())
