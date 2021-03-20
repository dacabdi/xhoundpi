""" xHoundPi program module facade """

# standard libs
import signal
import sys
import asyncio

# external imports
import structlog

# parsing libs
import pynmea2
import pyubx2

# local imports
from .serial import StubSerial
from .queue_pump import AsyncPump
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_classifier import ProtocolClassifier
from .proto_reader import (ProtocolReaderProvider,
                          UBXProtocolReader,
                          NMEAProtocolReader,)
from .proto_parser import (ProtocolParserProvider,
                          UBXProtocolParser,
                          NMEAProtocolParser,)
from .proto_serializer import (ProtocolSerializerProvider,
                              UBXProtocolSerializer,
                              NMEAProtocolSerializer,)
from .gnss_service import GnssService
from .gnss_service_runner import GnssServiceRunner
from .gnss_service_decorators import with_events # pylint: disable=unused-import
from .events import AppEvent

logger = structlog.get_logger('xhoundpi')

class XHoundPi: # pylint: disable=too-many-instance-attributes
    """ XHoundPi program class """

    def __init__(self, config):
        self.config = config
        self.signal = None
        self.signal_frame = None
        self.tasks = None

        self.subscribe_signals()

        self.gnss_inbound_queue = asyncio.queues.Queue(self.config.buffer_capacity)
        self.gnss_outbound_queue = asyncio.queues.Queue(self.config.buffer_capacity)

        self.gnss_client = self.create_gnss_client()
        self.gnss_protocol_classifier = self.create_protocol_classifier()
        self.gnss_protocol_reader_provider = self.create_protocol_reader_provider()
        self.gnss_protocol_parser_provider = self.create_protocol_parser_provider()
        self.gnss_protocol_serializer_provider = self.create_protocol_serializer_provider()

        self.gnss_service = GnssService( # pylint: disable=no-member
            gnss_client=self.gnss_client,
            classifier=self.gnss_protocol_classifier,
            reader_provider=self.gnss_protocol_reader_provider,
            parser_provider=self.gnss_protocol_parser_provider,
            serializer_provider=self.gnss_protocol_serializer_provider
        ).with_events(logger)

        self.gnss_service_runner = GnssServiceRunner(
            gnss_service=self.gnss_service,
            inbound_queue=self.gnss_inbound_queue,
            outbound_queue=self.gnss_outbound_queue)

        # TODO temporary shortcircuit that pumps all
        # inbound messages back into the outbound queue
        self.message_pump = AsyncPump(
            input_queue=self.gnss_inbound_queue,
            output_queue=self.gnss_outbound_queue)

    async def run(self):
        """ Run and wait for all tasks """
        self.tasks = asyncio.gather(
            self.gnss_service_runner.run(),
            self.message_pump.run())
        try:
            await self.tasks
        except asyncio.exceptions.CancelledError:
            if self.signal and self.signal_frame:
                signal_name = str(signal.Signals(self.signal)).removeprefix('Signals.') # pylint: disable=no-member
                logger.warning(AppEvent(f'Received signal \'{signal_name}\', exiting now'))
                return 0

            logger.exception(AppEvent('Running tasks unexpectedly cancelled'))
            return 1

    def subscribe_signals(self):
        """ Subscribe to signals """
        signal.signal(signal.SIGINT, self.signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        """ Handle signals """
        # NOTE do not add non-reentrant functions to this
        # signal handler; keep it simple, stupid (KISS)
        # https://stackoverflow.com/questions/4604634/which-functions-are-re-entrant-in-python-for-signal-library-processing
        self.signal = sig
        self.signal_frame = frame
        if self.tasks:
            self.tasks.cancel()

    def create_gnss_client(self):
        """ Create a GNSS client """
        gnss_serial = self.create_gnss_serial()
        return GnssClient(gnss_serial)

    def create_gnss_serial(self):
        """ Resolves the GNSS serial com based on configuration """
        if self.config.mock_gnss:
            transport_rx = open(self.config.gnss_mock_input, mode='rb')
            transport_tx = open(self.config.gnss_mock_output, mode='wb')
            return StubSerial(transport_rx, transport_tx)
        raise NotImplementedError("Currently only supporting GNSS input from mock file")

    def create_protocol_classifier(self): # pylint: disable=no-self-use
        """ Wire up a protocol classifier """
        classifications = {
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX
        }
        return ProtocolClassifier(classifications)

    def create_protocol_reader_provider(self): # pylint: disable=no-self-use
        """ Wire up and return the protocol readers inside a reader provider """
        gnss_ubx_frame_reader = UBXProtocolReader()
        gnss_nmea_frame_reader = NMEAProtocolReader()
        gnss_protocol_reader_mappings = {
            ProtocolClass.UBX : gnss_ubx_frame_reader,
            ProtocolClass.NMEA : gnss_nmea_frame_reader
        }
        return ProtocolReaderProvider(gnss_protocol_reader_mappings)

    def create_protocol_parser_provider(self): # pylint: disable=no-self-use
        """ Wire up and return the protocol parsers inside a parser provider """
        gnss_ubx_frame_parser = UBXProtocolParser(
            lambda frame: pyubx2.UBXReader.parse(frame, validate=True))
        gnss_nmea_frame_parser = NMEAProtocolParser(
            lambda frame: pynmea2.parse(frame.decode(), check=True))
        return ProtocolParserProvider({
            ProtocolClass.UBX : gnss_ubx_frame_parser,
            ProtocolClass.NMEA : gnss_nmea_frame_parser
        })

    def create_protocol_serializer_provider(self): # pylint: disable=no-self-use
        """ Wire up and return the protocol serializers inside a serializers provider """
        gnss_ubx_serializer = UBXProtocolSerializer(
            lambda message: message.payload.serialize())
        gnss_nmea_serializer = NMEAProtocolSerializer(
            lambda message: bytearray(message.payload.render(newline=True), 'ascii'))
        return ProtocolSerializerProvider({
            ProtocolClass.UBX : gnss_ubx_serializer,
            ProtocolClass.NMEA : gnss_nmea_serializer
        })
