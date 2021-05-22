# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-locals

import asyncio
import os
import unittest
import pathlib

from io import BytesIO
from unittest.mock import patch
from asyncio.tasks import wait_for

import structlog
from structlog.testing import capture_logs

# parsing libs
import pynmea2
import pyubx2

# local imports
from xhoundpi.serial import StubSerialBinary
from xhoundpi.gnss_client import GnssClient
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import ProtocolClassifier
from xhoundpi.proto_reader import ProtocolReaderProvider, UBXProtocolReader, NMEAProtocolReader
from xhoundpi.proto_parser import ProtocolParserProvider, UBXProtocolParser, NMEAProtocolParser
from xhoundpi.proto_serializer import NMEAProtocolSerializer, ProtocolSerializerProvider, UBXProtocolSerializer
from xhoundpi.gnss_service import GnssService
from xhoundpi.gnss_service_runner import GnssServiceRunner
from xhoundpi.async_ext import run_sync
import xhoundpi.gnss_service_decorators # pylint: disable=unused-import

from tools.hermes.parser import parser

from test.log_utils import setup_test_event_logger

def setUpModule():
    # parse input file into binary
    setup_test_event_logger()
    current_dir = pathlib.Path(__file__).parent.absolute()
    input_capture = current_dir.joinpath('../data/mixed_nmea_ubx_sample.cap')
    with input_capture.open('r') as capture, \
         current_dir.joinpath('functional_gnss_input.hex').open('wb') as output:
        parser(capture, output)

def tearDownModule():
    # remove parsed binary file
    current_dir = pathlib.Path(__file__).parent.absolute()
    filepath = current_dir.joinpath('functional_gnss_input.hex')
    if os.path.exists(filepath):
        os.remove(filepath)

class test_Functional_Gnss(unittest.TestCase):

    def create_service(self, inbound_queue, outbound_queue, transport_rx, transport_tx):
        self.maxDiff = None
        logger = structlog.get_logger()
        gnss_serial = StubSerialBinary(transport_rx, transport_tx)
        gnss_client = GnssClient(gnss_serial)
        gnss_protocol_classifier = ProtocolClassifier({
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX
        })
        gnss_protocol_reader_provider = ProtocolReaderProvider({
            ProtocolClass.UBX : UBXProtocolReader(),
            ProtocolClass.NMEA : NMEAProtocolReader()
        })
        gnss_protocol_parser_provider = ProtocolParserProvider({
            ProtocolClass.UBX : UBXProtocolParser(lambda frame: pyubx2.UBXReader.parse(frame, validate=True)),
            ProtocolClass.NMEA : NMEAProtocolParser(lambda frame: pynmea2.parse(frame.decode(), check=True))
        })
        gnss_serializer_provider = ProtocolSerializerProvider({
            ProtocolClass.UBX : UBXProtocolSerializer(lambda message: message.payload.serialize()),
            ProtocolClass.NMEA : NMEAProtocolSerializer(lambda message: bytearray(message.payload.render(newline=True), 'ascii'))
        })
        gnss_service = GnssService( # pylint: disable=no-member
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_protocol_reader_provider,
            parser_provider=gnss_protocol_parser_provider,
            serializer_provider=gnss_serializer_provider)\
            .with_events(logger)
        return GnssServiceRunner(
            gnss_service,
            inbound_queue=inbound_queue,
            outbound_queue=outbound_queue), gnss_serializer_provider

    def test_run(self):

        gnss_inbound_queue = asyncio.queues.Queue()
        gnss_outbound_queue = asyncio.queues.Queue()

        # open input sample data
        current_dir = pathlib.Path(__file__).parent.absolute()
        filepath = current_dir.joinpath('functional_gnss_input.hex')

        with open(filepath, mode='rb') as transport_rx, BytesIO() as transport_tx:
            service, deserializer_provider = self.create_service(gnss_inbound_queue, gnss_outbound_queue, transport_rx, transport_tx)
            test_uuids = [f'10000000-2000-3000-4000-500000000{str(d).zfill(3)}' for d in range(999)]
            with capture_logs() as cap_logs, patch('uuid.uuid4', side_effect=test_uuids):
                # run and wait for all tasks
                loop = asyncio.get_event_loop()
                task = loop.create_task(service.run())

                # msg1
                msg1 = run_sync(gnss_inbound_queue.get())
                raw1 = deserializer_provider.get_serializer(msg1.proto).serialize(msg1)
                run_sync(gnss_outbound_queue.put(msg1))
                self.assertEqual(msg1.proto, ProtocolClass.NMEA)
                self.assertEqual(msg1.payload.talker, 'GP')
                self.assertEqual(msg1.payload.sentence_type, 'GSV')
                self.assertTrue(transport_tx.getvalue().endswith(raw1))
                self.assertFalse(task.done())

                # msg2
                msg2 = run_sync(gnss_inbound_queue.get())
                raw2 = deserializer_provider.get_serializer(msg2.proto).serialize(msg2)
                run_sync(gnss_outbound_queue.put(msg2))
                self.assertEqual(msg2.proto, ProtocolClass.UBX)
                self.assertTrue(transport_tx.getvalue().endswith(raw2))
                self.assertFalse(task.done())

                # msg3
                msg3 = run_sync(gnss_inbound_queue.get())
                raw3 = deserializer_provider.get_serializer(msg3.proto).serialize(msg3)
                run_sync(gnss_outbound_queue.put(msg3))
                self.assertEqual(msg3.proto, ProtocolClass.UBX)
                self.assertTrue(transport_tx.getvalue().endswith(raw3))
                self.assertFalse(task.done())

                task.cancel()
                with self.assertRaises(asyncio.exceptions.CancelledError):
                    run_sync(wait_for(task, 1))

        # TODO do better logs outpout assertions
        self.assertGreaterEqual(len(cap_logs), 1)

    def test_run_on_corrupt_stream(self):

        # input sample data
        input_data = bytearray.fromhex(
                # packet 1 (nmea bad)
                '24 47 50 47 53 56 2C 33 2C 31 2C 30 39 2C 30 34'
                '2C 35 32 2C 31 38 38 2C 32 30 2C 30 37 2C 33 37'
                '2C 33 31 39 2C 32 37 2C 30 38 2C 37 31 2C 31 36'
                '31 2C 32 36 2C 30 39 2C 36 30 2C 32 36 35 2C 33'
                '31 2C 31 2A 36 31 0D 0A                        ' # wrong NMEA checksum, will trigger parser exception
                '                                               '
                # packet 2 (ubx good)
                'B5 62 01 01 14 00 B0 19 B9 1D 87 26 60 04 34 DB'
                '38 DF 91 1A B1 12 7D 07 00 00 DE 36            '
                # packet 3 (nmea bad)
                '24 47 4E 47 42 53 2C 31 38 33 32 34 36 2E 30 30'
                '2C 34 2E 32 2C 33 2E 39 2C 31 34 2E 36 2C 2C 2C'
                '2C 2C 2C 2A 36 41 0D 0D                        ' # wrong NMEA end marker, with trigger reader
                # packet 4 (ubx bad)
                'B5 62 01 13 1D 00 00 00 00 00 B0 19 B9 1D 87 26' # +1 byte size, will cause miss next message
                '60 04 34 DB 38 DF 91 1A B1 12 E7 EC F8 00 DF EC' # TODO: this is ill conceived, UBX messages could
                '02 00 0C CB                                    ' # contain '$' chars... work around this!
                # packet 5 (good but will be missed)
                'B5 62 01 01 14 00 B0 19 B9 1D 87 26 60 04 34 DB'
                '38 DF 91 1A B1 12 7D 07 00 00 DE 36            '
                # packet 5 (good, wont be missed)
                'B5 62 01 01 14 00 B0 19 B9 1D 87 26 60 04 34 DB'
                '38 DF 91 1A B1 12 7D 07 00 00 DE 36            ')

        gnss_inbound_queue = asyncio.queues.Queue()
        gnss_outbound_queue = asyncio.queues.Queue()
        transport_rx = BytesIO(input_data)
        transport_tx = BytesIO()
        service, deserializer_provider = self.create_service(gnss_inbound_queue, gnss_outbound_queue, transport_rx, transport_tx)

        test_uuids = [f'10000000-2000-3000-4000-500000000{str(d).zfill(3)}' for d in range(999)]
        with capture_logs() as cap_logs, patch('uuid.uuid4', side_effect=test_uuids):
            # run and wait for all tasks
            loop = asyncio.get_event_loop()
            task = loop.create_task(service.run())

            # msg1
            msg1 = run_sync(gnss_inbound_queue.get())
            raw1 = deserializer_provider.get_serializer(msg1.proto).serialize(msg1)
            run_sync(gnss_outbound_queue.put(msg1))
            self.assertEqual(msg1.proto, ProtocolClass.UBX)
            self.assertTrue(transport_tx.getvalue().endswith(raw1))
            self.assertFalse(task.done())

            # msg2
            msg2 = run_sync(gnss_inbound_queue.get())
            raw2 = deserializer_provider.get_serializer(msg2.proto).serialize(msg2)
            run_sync(gnss_outbound_queue.put(msg2))
            self.assertEqual(msg2.proto, ProtocolClass.UBX)
            self.assertTrue(transport_tx.getvalue().endswith(raw2))
            self.assertFalse(task.done())

            # should circle back here
            msg3 = run_sync(gnss_inbound_queue.get())
            raw3 = deserializer_provider.get_serializer(msg3.proto).serialize(msg3)
            self.assertEqual(msg3.proto, ProtocolClass.UBX)
            self.assertEqual(raw1, raw3)

            task.cancel()
            with self.assertRaises(asyncio.exceptions.CancelledError):
                run_sync(wait_for(task, 1))

        # TODO do better logs outpout assertions
        self.assertGreaterEqual(len(cap_logs), 1)
