"""xHoundPi firmware execution module"""

from asyncio.queues import Queue
from xhoundpi.proto_reader import StubProtocolReader, StubProtocolReaderProvider

# local imports
from .config import setup_configparser
from .serial import StubSerial
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_classifier import StubProtocolClassifier
from .proto_parser import StubParserProvider, StubProtocolParser
from .gnss_service import GnssService

async def main():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    # create and run gnss service
    # TODO create a facade to setup the services
    gnss_inbound_queue = Queue(config.buffer_capacity)
    gnss_outbound_queue = Queue(config.buffer_capacity)
    gnss_serial = gnss_serial_provider(config)
    gnss_client = GnssClient(gnss_serial)
    gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
    gnss_protocol_reader = StubProtocolReader()
    gnss_protocol_reader_provider = StubProtocolReaderProvider(gnss_protocol_reader)
    gnss_parser = StubProtocolParser()
    gnss_parser_provider = StubParserProvider(gnss_parser)

    gnss_service = GnssService(
        inbound_queue=gnss_inbound_queue,
        outbound_queue=gnss_outbound_queue,
        gnss_client=gnss_client,
        classifier=gnss_protocol_classifier,
        reader_provider=gnss_protocol_reader_provider,
        parser_provider=gnss_parser_provider)

    await gnss_service.run()

def gnss_serial_provider(config):
    """ Resolves the serial comm based on configuration """
    if config.mock_gnss:
        transport_rx = open(config.gnss_mock_input, mode='rb')
        transport_tx = open(config.gnss_mock_output, mode='+wb')
        return StubSerial(transport_rx, transport_tx)
    raise "Not implemented"

main()
