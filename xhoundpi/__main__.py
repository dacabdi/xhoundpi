"""xHoundPi firmware execution module"""

from asyncio.queues import Queue
from xhoundpi.serial import StubSerial

# local imports
from .config import setup_configparser
from .gnss_client import GnssClient
from .gnss_protocol_classifier import StubProtocolClassifier

def main():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    # tasks
    tasks = []

    # create and run gnss service
    gnss_inbound_queue = Queue(config.buffer_capacity)
    gnss_outbound_queue = Queue(config.buffer_capacity)
    gnss_serial = gnss_serial_provider(config)
    gnss_client = GnssClient(gnss_serial)
    gnss_protocol_classifier = StubProtocolClassifier()

    gnss_service = GnssService(
        inbound_queue=gnss_inbound_queue,
        outbound_queue=gnss_outbound_queue,
        gnss_client=gnss_client,
        classifier=gnss_protocol_classifier)

    tasks.append(gnss_service.run())

def gnss_serial_provider(config):
    if config.mock_gnss:
        with open(config.gnss_mock_input, mode='rb') as input,\
             open(config.gnss_mock_output, mode='+wb') as output:
            rx = input.read()
            tx = output
        return StubSerial()


main()
