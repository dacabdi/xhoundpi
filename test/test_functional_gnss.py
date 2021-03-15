import asyncio
import os
import unittest
import pathlib

from asyncio.tasks import wait_for
from io import BytesIO

from structlog import get_logger
from structlog.testing import capture_logs

# parsing libs
import pynmea2
import pyubx2

# local imports
from xhoundpi.serial import StubSerial
from xhoundpi.gnss_client import GnssClient
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.proto_classifier import ProtocolClassifier
from xhoundpi.proto_reader import ProtocolReaderProvider,\
                                  UBXProtocolReader,\
                                  NMEAProtocolReader
from xhoundpi.proto_parser import ProtocolParserProvider,\
                                  UBXProtocolParser,\
                                  NMEAProtocolParser
from xhoundpi.gnss_service import GnssService
from xhoundpi.gnss_service_runner import GnssServiceRunner
from xhoundpi.monkey_patching import add_method
from xhoundpi.async_ext import loop_forever_async, run_sync # pylint: disable=unused-import
from xhoundpi.queue_ext import get_forever_async # pylint: disable=unused-import

from tools.capture_processor.parser import parser

# NOTE patch NMEASentence to include byte
# serialization for uniform message API
@add_method(pynmea2.NMEASentence)
def serialize(self):
    """ Serialize NMEA message to bytes with trailing new line """
    return bytearray(self.render(newline=True), 'ascii')

def setUpModule():
    # parse input file into binary
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

    def test_run(self):

        # open input sample data
        current_dir = pathlib.Path(__file__).parent.absolute()
        filepath = current_dir.joinpath('functional_gnss_input.hex')

        # prepare fake io
        with open(filepath, mode='rb') as transport_rx, BytesIO() as transport_tx:
            gnss_serial = StubSerial(transport_rx, transport_tx)

            gnss_inbound_queue = asyncio.queues.Queue()
            gnss_outbound_queue = asyncio.queues.Queue()
            gnss_client = GnssClient(gnss_serial)

            gnss_protocol_classifier = ProtocolClassifier({
                bytes(b'\x24') : ProtocolClass.NMEA,
                bytes(b'\xb5\x62') : ProtocolClass.UBX
            })

            gnss_ubx_frame_reader = UBXProtocolReader()
            gnss_nmea_frame_reader = NMEAProtocolReader()
            gnss_protocol_reader_provider = ProtocolReaderProvider({
                ProtocolClass.UBX : gnss_ubx_frame_reader,
                ProtocolClass.NMEA : gnss_nmea_frame_reader
            })

            gnss_ubx_frame_parser = UBXProtocolParser(
                lambda frame: pyubx2.UBXReader.parse(frame, validate=True))
            gnss_nmea_frame_parser = NMEAProtocolParser(
                lambda frame: pynmea2.parse(frame.decode(), check=True))
            gnss_protocol_parser_provider = ProtocolParserProvider({
                ProtocolClass.UBX : gnss_ubx_frame_parser,
                ProtocolClass.NMEA : gnss_nmea_frame_parser
            })

            gnss_service = GnssService(
                gnss_client=gnss_client,
                classifier=gnss_protocol_classifier,
                reader_provider=gnss_protocol_reader_provider,
                parser_provider=gnss_protocol_parser_provider)

            gnss_service_runner = GnssServiceRunner(
                gnss_service,
                inbound_queue=gnss_inbound_queue,
                outbound_queue=gnss_outbound_queue)

            with capture_logs() as cap_logs:

                # run and wait for all tasks
                loop = asyncio.get_event_loop()
                task = loop.create_task(gnss_service_runner.run())

                msg1 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg1))
                self.assertEqual(msg1.proto, ProtocolClass.NMEA)
                self.assertEqual(msg1.payload.talker, 'GP')
                self.assertEqual(msg1.payload.sentence_type, 'GSV')
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg1.payload.serialize()))

                msg2 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg2))
                self.assertEqual(msg2.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg2.payload.serialize()))

                msg3 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg3))
                self.assertEqual(msg3.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg3.payload.serialize()))

                msg4 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg4))
                self.assertEqual(msg4.proto, ProtocolClass.NMEA)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg4.payload.serialize()))

                msg5 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg5))
                self.assertEqual(msg5.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg5.payload.serialize()))

                msg6 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg6))
                self.assertEqual(msg6.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg6.payload.serialize()))

                msg7 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg7))
                self.assertEqual(msg7.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg7.payload.serialize()))

                msg8 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg8))
                self.assertEqual(msg8.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg8.payload.serialize()))

                msg9 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg9))
                self.assertEqual(msg9.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg9.payload.serialize()))

                msg10 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg10))
                self.assertEqual(msg10.proto, ProtocolClass.UBX)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg10.payload.serialize()))

                msg11 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg11))
                self.assertEqual(msg11.proto, ProtocolClass.NMEA)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg11.payload.serialize()))

                msg12 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg12))
                self.assertEqual(msg12.proto, ProtocolClass.NMEA)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg12.payload.serialize()))

                msg13 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg13))
                self.assertEqual(msg13.proto, ProtocolClass.NMEA)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg13.payload.serialize()))

                msg14 = run_sync(gnss_inbound_queue.get())
                run_sync(gnss_outbound_queue.put(msg14))
                self.assertEqual(msg14.proto, ProtocolClass.NMEA)
                self.assertFalse(task.done())
                self.assertTrue(transport_tx.getvalue().endswith(msg14.payload.serialize()))

                # should circle back here

                msg15 = run_sync(gnss_inbound_queue.get())
                self.assertEqual(msg15.proto, ProtocolClass.NMEA)
                self.assertEqual(msg1.payload.serialize(), msg15.payload.serialize())

                task.cancel()
                with self.assertRaises(asyncio.exceptions.CancelledError):
                    run_sync(wait_for(task, 1))

            # TODO assert the logs

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

        # prepare fake io
        transport_rx = BytesIO(input_data)
        transport_tx = BytesIO()
        gnss_serial = StubSerial(transport_rx, transport_tx)

        gnss_inbound_queue = asyncio.queues.Queue()
        gnss_outbound_queue = asyncio.queues.Queue()
        gnss_client = GnssClient(gnss_serial)

        gnss_protocol_classifier = ProtocolClassifier({
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX
        })

        gnss_ubx_frame_reader = UBXProtocolReader()
        gnss_nmea_frame_reader = NMEAProtocolReader()
        gnss_protocol_reader_provider = ProtocolReaderProvider({
            ProtocolClass.UBX : gnss_ubx_frame_reader,
            ProtocolClass.NMEA : gnss_nmea_frame_reader
        })

        gnss_ubx_frame_parser = UBXProtocolParser(
            lambda frame: pyubx2.UBXReader.parse(frame, validate=True))
        gnss_nmea_frame_parser = NMEAProtocolParser(
            lambda frame: pynmea2.parse(frame.decode(), check=True))
        gnss_protocol_parser_provider = ProtocolParserProvider({
            ProtocolClass.UBX : gnss_ubx_frame_parser,
            ProtocolClass.NMEA : gnss_nmea_frame_parser
        })

        gnss_service = GnssService(
            gnss_client=gnss_client,
            classifier=gnss_protocol_classifier,
            reader_provider=gnss_protocol_reader_provider,
            parser_provider=gnss_protocol_parser_provider)

        with capture_logs() as cap_logs:

            gnss_service_runner = GnssServiceRunner(
                gnss_service,
                inbound_queue=gnss_inbound_queue,
                outbound_queue=gnss_outbound_queue)

            # run and wait for all tasks
            loop = asyncio.get_event_loop()
            task = loop.create_task(gnss_service_runner.run())

            msg1 = run_sync(gnss_inbound_queue.get())
            run_sync(gnss_outbound_queue.put(msg1))
            self.assertEqual(msg1.proto, ProtocolClass.UBX)
            self.assertFalse(task.done())
            self.assertTrue(transport_tx.getvalue().endswith(msg1.payload.serialize()))

            msg2 = run_sync(gnss_inbound_queue.get())
            run_sync(gnss_outbound_queue.put(msg2))
            self.assertEqual(msg2.proto, ProtocolClass.UBX)
            self.assertFalse(task.done())
            self.assertTrue(transport_tx.getvalue().endswith(msg2.payload.serialize()))

            # should circle back here

            msg3 = run_sync(gnss_inbound_queue.get())
            self.assertEqual(msg3.proto, ProtocolClass.UBX)
            self.assertEqual(msg1.payload.serialize(), msg3.payload.serialize())

            task.cancel()
            with self.assertRaises(asyncio.exceptions.CancelledError):
                run_sync(wait_for(task, 1))

        # TODO aseert logs
