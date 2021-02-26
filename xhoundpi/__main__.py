"""xHoundPi firmware execution module"""

from asyncio.queues import Queue

# local imports
from .config import setup_configparser
from .serial import StubSerial
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_parser import StubProtocolClassifier, StubParserProvider
from .gnss_service import GnssService

async def main():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    # create and run gnss service
    gnss_inbound_queue = Queue(config.buffer_capacity)
    gnss_outbound_queue = Queue(config.buffer_capacity)
    gnss_serial = gnss_serial_provider(config)
    gnss_client = GnssClient(gnss_serial)
    gnss_protocol_classifier = StubProtocolClassifier(ProtocolClass.NONE)
    gnss_parser_provider = StubParserProvider()

    gnss_service = GnssService(
        inbound_queue=gnss_inbound_queue,
        outbound_queue=gnss_outbound_queue,
        gnss_client=gnss_client,
        classifier=gnss_protocol_classifier,
        parser_provider=gnss_parser_provider)

    await gnss_service.run()

def gnss_serial_provider(config):
    if config.mock_gnss:
        rx = open(config.gnss_mock_input, mode='rb')
        tx = open(config.gnss_mock_output, mode='+wb')
        return StubSerial(rx, tx)

main()
