'''
xHoundPi program module facade
'''

# standard libs
import signal
import sys
import asyncio
import uuid
import decimal

# external imports
import structlog
import numpy as np
from PIL import Image, ImageFont, ImageDraw

# parsing libs
import pyubx2
import pynmea2

# extensions and decorators (patch types on load)
# pylint: disable=unused-import
import xhoundpi.gnss_service_decorators
import xhoundpi.gnss_client_decorators
import xhoundpi.queue_decorators
import xhoundpi.processor_decorators
# pylint: enable=unused-import

# submodules
from .panel.geometry import Geometry
from .panel.framebuffer import FrameBuffer
from .panel.fakepanel import GifDisplay, PyGameDisplay

# local imports
# pylint: disable=line-too-long
from .config import display_mode
from .time import StopWatch
from .serial import StubSerialBinary
from .queue_pump import AsyncPump
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_classifier import ProtocolClassifier
from .proto_reader import ProtocolReaderProvider, UBXProtocolReader, NMEAProtocolReader
from .proto_parser import ProtocolParserProvider, UBXProtocolParser, NMEAProtocolParser
from .proto_serializer import ProtocolSerializerProvider, UBXProtocolSerializer, NMEAProtocolSerializer
from .gnss_service import GnssService
from .gnss_service_runner import GnssServiceRunner
from .data_formatter import NMEADataFormatter, UBXDataFormatter
from .message_editor import NMEAMessageEditor, UBXMessageEditor
from .orientation import EulerAngles, StaticOrientationProvider
from .coordinates_offset import GeoCoordinates, ICoordinatesOffsetProvider, OrientationOffsetProvider, StaticOffsetProvider
from .operator import NMEAOffsetOperator, UBXOffsetOperator, UBXHiResOffsetOperator
from .operator_provider import CoordinateOperationProvider
from .message_policy_provider import OnePolicyProvider
from .message_policy import HasLocationPolicy
from .processor import CompositeProcessor, NullProcessor, GenericProcessor
from .events import AppEvent, MetricsReport
from .metric import LatencyMetric, ValueMetric, SuccessCounterMetric, MetricsCollection
from .async_ext import loop_forever_async
from .dmath import DECIMAL1, setup_common_context, DECIMAL0
# pylint: enable=line-too-long

logger = structlog.get_logger('xhoundpi')

# pylint: disable=too-many-instance-attributes,too-many-public-methods
class XHoundPi:
    '''
    XHoundPi program class
    '''

    def __init__(self, config):
        self._config = config
        self._tasks = []
        self._tasks_gather = None
        self._setup_signals()
        self._setup_decimal_context()
        self._setup_queues()
        self._setup_metrics()
        self._setup_metrics_logger()
        self._setup_display()
        self._setup_gnss_service()
        self._setup_processors()
        self._setup_msg_pump()

    async def run(self):
        '''
        Run and wait for all tasks
        '''
        self._tasks_gather = asyncio.gather(*self._tasks)
        try:
            await self._tasks_gather
        except asyncio.exceptions.CancelledError:
            if self._signal and self._signal_frame:
                signal_name = str(signal.Signals(self._signal)).removeprefix('Signals.') # pylint: disable=no-member
                logger.warning(AppEvent(f'Received signal \'{signal_name}\', exiting now'))
                return 0
            logger.exception(AppEvent('Running tasks unexpectedly cancelled'))
            return 1

    def _setup_signals(self):
        '''
        Subscribe to OS process signals
        '''
        self._signal = None
        self._signal_frame = None
        signal.signal(signal.SIGINT, self.signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self.signal_handler)

    # pylint: disable=attribute-defined-outside-init
    def signal_handler(self, sig, frame):
        '''
        Handle signals
        '''
        # pylint: disable=line-too-long
        # NOTE do not add non-reentrant functions to this
        #      signal handler; keep it simple, stupid (KISS)
        #      https://stackoverflow.com/questions/4604634/which-functions-are-re-entrant-in-python-for-signal-library-processing
        # pylint: enable=line-too-long
        self._signal = sig
        self._signal_frame = frame
        if self._tasks_gather:
            self._tasks_gather.cancel()

    @staticmethod
    def _setup_decimal_context():
        '''
        Setup default Decimal context for all threads
        '''
        setup_common_context()

    def _setup_display(self):
        '''
        Configure display
        '''
        if self._config.display_driver == 'none':
            self._frame_buff = None
            self._display = None
        else:
            self.setup_frame_buffer()
            self._gnss_processed_queue = (self._gnss_processed_queue
                .with_callback(self.update_frame)) # type: ignore
            if self._config.display_driver == 'pygame':
                self.setup_display_pygame()
            elif self._config.display_driver == 'gif':
                self.setup_display_gif()
            else:
                raise NotImplementedError(
                    "Currently only 'none', 'gif', and 'pygame'"
                    "display modes are supported")

    def setup_frame_buffer(self):
        '''
        Setup frame buffer
        '''
        self._display_mode = display_mode(self._config.display_mode)
        self._display_geometry = Geometry(
            rows=self._config.display_height,
            cols=self._config.display_width,
            channels=self._display_mode.channels, # type: ignore
            depth=self._display_mode.depth) # type: ignore
        self._frame_buff = FrameBuffer(self._display_geometry)

    def setup_display_pygame(self):
        '''
        Configure and start pygame fake display
        '''
        self._display = PyGameDisplay(self._frame_buff, scale=self._config.display_scale)
        self._tasks.append(self._display.mainloop())

    def setup_display_gif(self):
        '''
        Configure and setup a GIF output display
        '''
        self._display = GifDisplay(self._display_mode, self._frame_buff)

    def update_frame(self, message):
        '''
        POC method to update frame, used as a callback after changes
        '''
        if HasLocationPolicy().qualifies(message):
            geometry = self._frame_buff.geometry
            text_im = self._make_text(geometry,
                f'lat:{message.payload.lat}\n'
                f'lon:{message.payload.lon}')
            np.copyto(self._frame_buff.canvas, text_im)
            self._frame_buff.update()

    def _make_text(self, geometry: Geometry, text):
        '''
        Generate text
        '''
        image = Image.new(self._display_mode.pilmode, geometry.col_major, color='black')
        font = ImageFont.truetype('fonts/clacon.ttf', 18)
        draw = ImageDraw.Draw(image)
        draw.text((0,0), text, font=font, fill='red', align='left')
        return np.array(image)

    # pylint: disable=line-too-long
    def _setup_metrics(self):
        '''
        Setup program metrics
        '''
        self._metric_hooks = []
        self._metrics = MetricsCollection([
            # gnss service
            ValueMetric('gnss_client_read_bytes', self._metric_hooks),
            ValueMetric('gnss_client_written_bytes', self._metric_hooks),
            SuccessCounterMetric('gnss_service_read_counter', self._metric_hooks),
            SuccessCounterMetric('gnss_service_write_counter', self._metric_hooks),
            LatencyMetric('gnss_service_read_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('gnss_service_write_latency', StopWatch(), self._metric_hooks),
            # processors
            SuccessCounterMetric('null_processor_counter', self._metric_hooks),
            SuccessCounterMetric('zero_offset_processor_counter', self._metric_hooks),
            SuccessCounterMetric('positive_offset_processor_counter', self._metric_hooks),
            SuccessCounterMetric('negative_offset_processor_counter', self._metric_hooks),
            SuccessCounterMetric('zero_offset_orientation_processor_counter', self._metric_hooks),
            SuccessCounterMetric('positive_offset_orientation_processor_counter', self._metric_hooks),
            LatencyMetric('null_processor_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('zero_offset_processor_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('positive_offset_processor_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('negative_offset_processor_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('zero_offset_orientation_processor_latency', StopWatch(), self._metric_hooks),
            LatencyMetric('positive_offset_orientation_processor_latency', StopWatch(), self._metric_hooks),
        ])

    def _setup_metrics_logger(self):
        ''' Setup periodic metrics logger '''
        async def periodic_report():
            logger.info(MetricsReport(
                frequency=self._config.metrics_logger_freq,
                report_id=uuid.uuid4(),
                metrics=self._metrics.mappify()))
            await asyncio.sleep(self._config.metrics_logger_freq)
        self._metrics_logger = (loop_forever_async(periodic_report)
            if self._config.metrics_logger_freq != 0
            else None)
        if self._metrics_logger:
            self._tasks.append(asyncio.create_task(
                self._metrics_logger, name='metrics_logger'))

    def _setup_queues(self):
        '''
        Setup program queues
        '''
        self._gnss_inbound_queue = asyncio.queues.Queue(self._config.buffer_capacity)
        self._gnss_outbound_queue = asyncio.queues.Queue(self._config.buffer_capacity)
        self._gnss_processed_queue = asyncio.queues.Queue(self._config.buffer_capacity)

    def _setup_gnss_service(self):
        '''
        Ensure all GNSS service dependencies are setup
        '''
        self._gnss_client = self._create_gnss_client()
        self._gnss_protocol_classifier = self._create_protocol_classifier()
        self._gnss_protocol_reader_provider = self._create_protocol_reader_provider()
        self._gnss_protocol_parser_provider = self._create_protocol_parser_provider()
        self._gnss_protocol_serializer_provider = self._create_protocol_serializer_provider()
        self._gnss_service = (GnssService( # pylint: disable=no-member
            gnss_client=self._gnss_client,
            classifier=self._gnss_protocol_classifier,
            reader_provider=self._gnss_protocol_reader_provider,
            parser_provider=self._gnss_protocol_parser_provider,
            serializer_provider=self._gnss_protocol_serializer_provider)
            .with_events(logger=logger) # type: ignore
            .with_metrics(
                # pylint: disable=no-member
                rcounter=self._metrics.gnss_service_read_counter, # type: ignore
                wcounter=self._metrics.gnss_service_write_counter, # type: ignore
                rlatency=self._metrics.gnss_service_read_latency, # type: ignore
                wlatency=self._metrics.gnss_service_write_latency)) # type: ignore
        self._gnss_service_runner = GnssServiceRunner(
            gnss_service=self._gnss_service,
            inbound_queue=self._gnss_inbound_queue,
            outbound_queue=self._gnss_outbound_queue)
        self._tasks.append(asyncio.create_task(
            self._gnss_service_runner.run(), name='gnss_service'))

    def _create_gnss_client(self):
        '''
        Create a GNSS client
        '''
        gnss_serial = self._create_gnss_serial()
        return (GnssClient(gnss_serial) # pylint: disable=no-member
            .with_metrics( # type: ignore
                # pylint: disable=no-member
                cbytes_read=self._metrics.gnss_client_read_bytes, # type: ignore
                cbytes_written=self._metrics.gnss_client_written_bytes)) # type: ignore

    def _create_gnss_serial(self):
        '''
        Resolves the GNSS serial com based on configuration
        '''
         # pylint: disable=consider-using-with,bad-option-value
        if self._config.mock_gnss:
            transport_rx = open(self._config.gnss_mock_input, mode='rb')
            transport_tx = open(self._config.gnss_mock_output, mode='wb')
            return StubSerialBinary(transport_rx, transport_tx) # type: ignore
        raise NotImplementedError("Currently only supporting GNSS input from mock file")

    def _create_protocol_classifier(self): # pylint: disable=no-self-use
        '''
        Wire up a protocol classifier
        '''
        classifications = {
            bytes(b'\x24') : ProtocolClass.NMEA,
            bytes(b'\xb5\x62') : ProtocolClass.UBX
        }
        return ProtocolClassifier(classifications)

    def _create_protocol_reader_provider(self): # pylint: disable=no-self-use
        '''
        Wire up and return the protocol readers inside a reader provider
        '''
        gnss_ubx_frame_reader = UBXProtocolReader()
        gnss_nmea_frame_reader = NMEAProtocolReader()
        gnss_protocol_reader_mappings = {
            ProtocolClass.UBX : gnss_ubx_frame_reader,
            ProtocolClass.NMEA : gnss_nmea_frame_reader
        }
        return ProtocolReaderProvider(gnss_protocol_reader_mappings)

    def _create_protocol_parser_provider(self): # pylint: disable=no-self-use
        '''
        Wire up and return the protocol parsers inside a parser provider
        '''
        gnss_ubx_frame_parser = UBXProtocolParser(
            lambda frame: pyubx2.UBXReader.parse(frame, validate=True))
        gnss_nmea_frame_parser = NMEAProtocolParser(
            lambda frame: pynmea2.parse(frame.decode(), check=True))
        return ProtocolParserProvider({
            ProtocolClass.UBX : gnss_ubx_frame_parser,
            ProtocolClass.NMEA : gnss_nmea_frame_parser
        })

    def _create_protocol_serializer_provider(self): # pylint: disable=no-self-use
        '''
        Wire up and return the protocol serializers inside a serializers provider
        '''
        gnss_ubx_serializer = UBXProtocolSerializer(
            lambda message: message.payload.serialize())
        gnss_nmea_serializer = NMEAProtocolSerializer(
            lambda message: bytearray(message.payload.render(newline=True), 'ascii'))
        return ProtocolSerializerProvider({
            ProtocolClass.UBX : gnss_ubx_serializer,
            ProtocolClass.NMEA : gnss_nmea_serializer
        })

    def _setup_processors(self):
        '''
        Setup GNSS processors pipeline
        '''
        # pylint: disable=no-member
        zero_offset = DECIMAL0
        pos_offset = decimal.Decimal('0.005')
        neg_offset = decimal.Decimal('-0.005')
        orientation_zero = StaticOrientationProvider(EulerAngles(yaw=DECIMAL0, pitch=DECIMAL0, roll=DECIMAL0))
        orientation_non_zero = StaticOrientationProvider(EulerAngles(yaw=DECIMAL1, pitch=DECIMAL1, roll=DECIMAL1))
        self._processors = CompositeProcessor([
            NullProcessor()
                .with_events(logger=logger) # type: ignore
                .with_metrics(
                    counter=self._metrics.null_processor_counter, # type: ignore
                    latency=self._metrics.null_processor_latency), # type: ignore
            self._make_offset_generic_processor(
                name='ZeroOffsetProcessor',
                offset_provider=StaticOffsetProvider(GeoCoordinates(lat=zero_offset, lon=zero_offset, alt=zero_offset)),
                counter=self._metrics.zero_offset_processor_counter, # type: ignore
                latency=self._metrics.zero_offset_processor_latency), # type: ignore
            '''self._make_offset_generic_processor(
                name='PositiveOffsetProcessor',
                offset_provider=StaticOffsetProvider(GeoCoordinates(lat=pos_offset, lon=pos_offset, alt=pos_offset)),
                counter=self._metrics.positive_offset_processor_counter, # type: ignore
                latency=self._metrics.positive_offset_processor_latency), # type: ignore
            self._make_offset_generic_processor(
                name='NegativeOffsetProcessor',
                offset_provider=StaticOffsetProvider(GeoCoordinates(lat=neg_offset, lon=neg_offset, alt=neg_offset)),
                counter=self._metrics.negative_offset_processor_counter, # type: ignore
                latency=self._metrics.negative_offset_processor_latency), # type: ignore
            self._make_offset_generic_processor(
                name='ZeroOffsetOrientationBasedProcessor',
                offset_provider=OrientationOffsetProvider(orientation_zero, DECIMAL0),
                counter=self._metrics.zero_offset_orientation_processor_counter, # type: ignore
                latency=self._metrics.zero_offset_orientation_processor_latency), # type: ignore
            self._make_offset_generic_processor(
                name='PositiveOffsetOrientationBasedProcessor',
                offset_provider=OrientationOffsetProvider(orientation_non_zero, DECIMAL1),
                counter=self._metrics.positive_offset_orientation_processor_counter, # type: ignore
                latency=self._metrics.positive_offset_orientation_processor_latency), # type: ignore'''
            #self._make_offset_generic_processor(
            #    name='NegativeOffsetOrientationBasedProcessor',
            #    offset_provider=OrientationOffsetProvider(orientation_non_zero, -DECIMAL1),
            #    counter=self._metrics.negative_offset_processor_counter, # type: ignore
            #    latency=self._metrics.negative_offset_processor_latency), # type: ignore
        ])
        self.processors_pipeline = AsyncPump(
             # pylint: disable=no-member
            input_queue=(self._gnss_inbound_queue
                .with_transform(self._processors.process) # type: ignore
                .with_transform(lambda result: result[1])),
            output_queue=self._gnss_processed_queue)
        self._tasks.append(asyncio.create_task(
            self.processors_pipeline.run(), name='processors_pipeline'))

    # pylint: disable=too-many-arguments, no-self-use
    def _make_offset_generic_processor(
        self,
        name: str,
        offset_provider: ICoordinatesOffsetProvider,
        counter: SuccessCounterMetric,
        latency: LatencyMetric):
        # pylint: disable=no-member
        '''
        Composes a generic processor
        that uses fixed offsets operators
        '''
        return (GenericProcessor(
                name=name,
                policy_provider=OnePolicyProvider(HasLocationPolicy()),
                operator_provider=CoordinateOperationProvider(
                    nmea_operator=NMEAOffsetOperator(
                        msg_editor=NMEAMessageEditor(),
                        data_formatter=NMEADataFormatter(),
                        offset_provider=offset_provider),
                    ubx_operator=UBXOffsetOperator(
                        msg_editor=UBXMessageEditor(),
                        data_formatter=UBXDataFormatter(),
                        offset_provider=offset_provider),
                    ubx_hires_operator=UBXHiResOffsetOperator(
                        msg_editor=UBXMessageEditor(),
                        data_formatter=UBXDataFormatter(),
                        offset_provider=offset_provider),))
                .with_events(logger=logger) # type: ignore
                .with_metrics(
                    # TODO use separate metrics
                    counter=counter,
                    latency=latency))

    def _setup_msg_pump(self):
        ''' Temporary msg pump '''
        self._message_pump = AsyncPump(
            input_queue=self._gnss_processed_queue,
            output_queue=self._gnss_outbound_queue)
        self._tasks.append(asyncio.create_task(
            self._message_pump.run(), name='message_pump'))
