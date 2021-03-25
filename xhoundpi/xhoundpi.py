""" xHoundPi program module facade """

# standard libs
import signal
import sys
import asyncio
import uuid

# external imports
import structlog

# parsing libs
import pynmea2
import pyubx2

# extensions and decorators (patch types on load)
import xhoundpi.gnss_service_decorators # pylint: disable=unused-import
import xhoundpi.gnss_client_decorators # pylint: disable=unused-import
import xhoundpi.queue_decorators # pylint: disable=unused-import
import xhoundpi.processor_decorators # pylint: disable=unused-import

# local imports
from .time import StopWatch
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
from .processor import NullProcessor
from .events import (AppEvent,
                    MetricsReport,)
from .metric import (LatencyMetric,
                    ValueMetric,
                    SuccessCounterMetric,
                    MetricsCollection)
from .async_ext import loop_forever_async

logger = structlog.get_logger('xhoundpi')

class XHoundPi: # pylint: disable=too-many-instance-attributes
    """ XHoundPi program class """

    def __init__(self, config):
        self.config = config
        self.tasks = []
        self.tasks_gather = None
        self.setup_signals()
        self.setup_metrics()
        self.setup_metrics_logger()
        self.setup_queues()
        self.setup_gnss_service()
        self.setup_processors()
        self.setup_msg_pump()

    async def run(self):
        """ Run and wait for all tasks """
        self.tasks_gather = asyncio.gather(*self.tasks)
        try:
            await self.tasks_gather
        except asyncio.exceptions.CancelledError:
            if self.signal and self.signal_frame:
                signal_name = str(signal.Signals(self.signal)).removeprefix('Signals.') # pylint: disable=no-member
                logger.warning(AppEvent(f'Received signal \'{signal_name}\', exiting now'))
                return 0
            logger.exception(AppEvent('Running tasks unexpectedly cancelled'))
            return 1

    def setup_signals(self):
        """ Subscribe to signals """
        self.signal = None
        self.signal_frame = None
        signal.signal(signal.SIGINT, self.signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self.signal_handler)

    # pylint: disable=attribute-defined-outside-init
    def signal_handler(self, sig, frame):
        """ Handle signals """
        # NOTE do not add non-reentrant functions to this
        # signal handler; keep it simple, stupid (KISS)
        # https://stackoverflow.com/questions/4604634/which-functions-are-re-entrant-in-python-for-signal-library-processing
        self.signal = sig
        self.signal_frame = frame
        if self.tasks_gather:
            self.tasks_gather.cancel()

    # pylint: disable=line-too-long
    def setup_metrics(self):
        """ Setup program metrics """
        self.metric_hooks = []
        self.metrics = MetricsCollection([
            ValueMetric('gnss_client_read_bytes', self.metric_hooks),
            ValueMetric('gnss_client_written_bytes', self.metric_hooks),
            SuccessCounterMetric('gnss_service_read_counter', self.metric_hooks),
            SuccessCounterMetric('gnss_service_write_counter', self.metric_hooks),
            LatencyMetric('gnss_service_read_latency', StopWatch(), self.metric_hooks),
            LatencyMetric('gnss_service_write_latency', StopWatch(), self.metric_hooks),
            SuccessCounterMetric('gnss_processors_counter', self.metric_hooks),
            LatencyMetric('gnss_processors_latency', StopWatch(), self.metric_hooks),
        ])

    def setup_metrics_logger(self):
        """ Setup periodic metrics logger """
        async def periodic_report():
            logger.info(MetricsReport(
                frequency=self.config.metrics_logger_freq,
                report_id=uuid.uuid4(),
                metrics=self.metrics.mappify()))
            await asyncio.sleep(self.config.metrics_logger_freq)
        self.metrics_logger = (loop_forever_async(periodic_report)
            if self.config.metrics_logger_freq != 0
            else None)
        if self.metrics_logger:
            self.tasks.append(asyncio.create_task(
                self.metrics_logger, name='metrics_logger'))

    def setup_queues(self):
        """ Setup program queues """
        self.gnss_inbound_queue = asyncio.queues.Queue(self.config.buffer_capacity)
        self.gnss_outbound_queue = asyncio.queues.Queue(self.config.buffer_capacity)
        self.gnss_processed_queue = asyncio.queues.Queue(self.config.buffer_capacity)

    def setup_gnss_service(self):
        """ Ensure all GNSS service dependencies are setup """
        self.gnss_client = self.create_gnss_client()
        self.gnss_protocol_classifier = self.create_protocol_classifier()
        self.gnss_protocol_reader_provider = self.create_protocol_reader_provider()
        self.gnss_protocol_parser_provider = self.create_protocol_parser_provider()
        self.gnss_protocol_serializer_provider = self.create_protocol_serializer_provider()
        self.gnss_service = (GnssService( # pylint: disable=no-member
            gnss_client=self.gnss_client,
            classifier=self.gnss_protocol_classifier,
            reader_provider=self.gnss_protocol_reader_provider,
            parser_provider=self.gnss_protocol_parser_provider,
            serializer_provider=self.gnss_protocol_serializer_provider)
            .with_events(logger=logger)
            .with_metrics(
                # pylint: disable=no-member
                rcounter=self.metrics.gnss_service_read_counter,
                wcounter=self.metrics.gnss_service_write_counter,
                rlatency=self.metrics.gnss_service_read_latency,
                wlatency=self.metrics.gnss_service_write_latency))
        self.gnss_service_runner = GnssServiceRunner(
            gnss_service=self.gnss_service,
            inbound_queue=self.gnss_inbound_queue,
            outbound_queue=self.gnss_outbound_queue)
        self.tasks.append(asyncio.create_task(
            self.gnss_service_runner.run(), name='gnss_service'))

    def create_gnss_client(self):
        """ Create a GNSS client """
        gnss_serial = self.create_gnss_serial()
        return (GnssClient(gnss_serial) # pylint: disable=no-member
            .with_metrics(
                # pylint: disable=no-member
                cbytes_read=self.metrics.gnss_client_read_bytes,
                cbytes_written=self.metrics.gnss_client_written_bytes))

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

    def setup_processors(self):
        """ Setup GNSS processors pipeline """
        # pylint: disable=no-member
        self.processors = (NullProcessor()
            .with_events(logger=logger)
            .with_metrics(
                counter=self.metrics.gnss_processors_counter,
                latency=self.metrics.gnss_processors_latency))
        self.processors_pipeline = AsyncPump(
             # pylint: disable=no-member
            input_queue=(self.gnss_inbound_queue
                .with_transform(self.processors.process)
                .with_transform(lambda result: result[1])),
            output_queue=self.gnss_processed_queue)
        self.tasks.append(asyncio.create_task(
            self.processors_pipeline.run(), name='processors_pipeline'))

    def setup_msg_pump(self):
        """ Temporary msg pump """
        self.message_pump = AsyncPump(
            input_queue=self.gnss_processed_queue,
            output_queue=self.gnss_outbound_queue)
        self.tasks.append(asyncio.create_task(
            self.message_pump.run(), name='message_pump'))
