"""xHoundPi firmware execution module"""

# standard libs
import signal
import sys
import asyncio
import logging
import logging.config

# external imports
import yaml
import structlog

# parsing libs
import pynmea2
import pyubx2

# local imports
from .config import setup_configparser
from .serial import StubSerial
from .queue_pump import AsyncPump
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_classifier import ProtocolClassifier
from .proto_reader import ProtocolReaderProvider,\
                          UBXProtocolReader,\
                          NMEAProtocolReader
from .proto_parser import ProtocolParserProvider,\
                          UBXProtocolParser,\
                          NMEAProtocolParser
from .gnss_service import GnssService
from .gnss_service_runner import GnssServiceRunner
from .monkey_patching import add_method
from .async_ext import loop_forever_async # pylint: disable=unused-import
from .queue_ext import get_forever_async # pylint: disable=unused-import

# NOTE patch NMEASentence to include byte
# serialization for uniform message API
@add_method(pynmea2.NMEASentence)
def serialize(self):
    """ Serialize NMEA message to bytes with trailing new line """
    return bytearray(self.render(newline=True), 'ascii')

logger = structlog.get_logger('xhoundpi')

def signal_handler(sig, frame): # pylint: disable=unused-argument
    """ Signal handler """
    signal_name = str(signal.Signals(sig)).removeprefix('Signals.') # pylint: disable=no-member
    logger.warning(f'Received termination signal \'{signal_name}\', exiting gracefully')
    sys.exit(0)

#pylint: disable=too-many-locals
async def main_async():
    """xHoundPi entry point"""

    # register to handle termination signals
    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    # setup loggers
    setup_logging(config.log_config_file)
    logger.info('start_application', config=vars(config))

    gnss_inbound_queue = asyncio.queues.Queue(config.buffer_capacity)
    gnss_outbound_queue =  asyncio.queues.Queue(config.buffer_capacity)
    gnss_serial = gnss_serial_provider(config)
    gnss_client = GnssClient(gnss_serial)

    classifications = {
        bytes(b'\x24') : ProtocolClass.NMEA,
        bytes(b'\xb5\x62') : ProtocolClass.UBX
    }
    gnss_protocol_classifier = ProtocolClassifier(classifications)

    gnss_ubx_frame_reader = UBXProtocolReader()
    gnss_nmea_frame_reader = NMEAProtocolReader()
    gnss_protocol_reader_mappings = {
        ProtocolClass.UBX : gnss_ubx_frame_reader,
        ProtocolClass.NMEA : gnss_nmea_frame_reader
    }
    gnss_protocol_reader_provider = ProtocolReaderProvider(gnss_protocol_reader_mappings)

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

    # TODO this is a temporary shortcircuit
    round_trip_pump = AsyncPump(
        input_queue=gnss_inbound_queue,
        output_queue=gnss_outbound_queue)

    # run and wait for all tasks
    await asyncio.gather(
        gnss_service_runner.run(),
        round_trip_pump.run())

def gnss_serial_provider(config):
    """ Resolves the serial comm based on configuration """
    if config.mock_gnss:
        transport_rx = open(config.gnss_mock_input, mode='rb')
        transport_tx = open(config.gnss_mock_output, mode='wb')
        return StubSerial(transport_rx, transport_tx)
    raise NotImplementedError("Currently only supporting GNSS input from mock file")

def setup_logging(config_path):
    """ Setup logging configuration """

    timestamper = structlog.processors.TimeStamper(fmt='iso')
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    # configure logging
    with open(config_path, 'rt') as config_file:
        config = yaml.safe_load(config_file.read())
        # add structlog formatters
        config['formatters'] = {
            "plain": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": pre_chain,
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": pre_chain,
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(indent=1, sort_keys=True),
                "foreign_pre_chain": pre_chain,
            }
        }
        logging.config.dictConfig(config)

    # configure structlog
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False)

def main():
    """ Entry point and async main scheduler """
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    return exit_code

main()
