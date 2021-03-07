"""xHoundPi firmware execution module"""

import asyncio
from asyncio.queues import Queue
from os import read

# parsing libs
import pynmea2
import pyubx2

# local imports
from .config import setup_configparser
from .async_ext import loop_forever_async
from .serial import StubSerial
from .gnss_client import GnssClient
from .proto_class import ProtocolClass
from .proto_classifier import ProtocolClassifier
from .proto_reader import ProtocolReaderProvider,\
                          UBXProtocolReader,\
                          NMEAProtocolReader
from .proto_parser import ProtocolParserProvider,\
                          UBXProtocolParser,\
                          NMEAProtocolParser
from .gnss_service import GnssService,\
                          GnssServiceRunner
from .monkey_patching import add_method
from .queue_ext import get_forever_async

# NOTE patch NMEASentence to include byte
# serialization for uniform message API
@add_method(pynmea2.NMEASentence)
def serialize(self):
    """ Serialize NMEA message to bytes with trailing new line """
    return bytearray(self.render(newline=True), 'ascii')

async def main_async():
    """xHoundPi entry point"""

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse()
    parser.print_values()
    print(vars(config))

    gnss_inbound_queue = Queue(config.buffer_capacity)
    gnss_outbound_queue = Queue(config.buffer_capacity)
    gnss_serial = gnss_serial_provider(config)
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
        inbound=gnss_inbound_queue,
        outbound=gnss_outbound_queue)

    # run and wait for all tasks
    await asyncio.gather(gnss_service_runner.run())

    return 0

def gnss_serial_provider(config):
    """ Resolves the serial comm based on configuration """
    if config.mock_gnss:
        transport_rx = open(config.gnss_mock_input, mode='rb')
        transport_tx = open(config.gnss_mock_output, mode='+wb')
        return StubSerial(transport_rx, transport_tx)
    raise NotImplementedError("Currently only supporting GNSS input from file")

def main():
    """ Entry point and async main scheduler """
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    return exit_code

main()
