""" GNSS client """

import asyncio

from .gnss_client import IGnssClient
from .proto_classifier import IProtocolClassifier
from .proto_reader import IProtocolReaderProvider
from .proto_parser import IProtocolParserProvider
from .message import Message

class GnssService():
    """ Gnss service facade """

    def __init__(
        self,
        inbound_queue: asyncio.queues.Queue,
        outbound_queue: asyncio.queues.Queue,
        gnss_client: IGnssClient,
        classifier: IProtocolClassifier,
        reader_provider: IProtocolReaderProvider,
        parser_provider: IProtocolParserProvider
        ): # pylint: disable=too-many-arguments
        self.__inbound_queue = inbound_queue
        self.__outbound_queue = outbound_queue
        self.__gnss_client = gnss_client
        self.__classifier = classifier
        self.__reader_provider = reader_provider
        self.__parser_provider = parser_provider

    async def run(self):
        """ Coroutine that runs the inbound and outbound queue processing loops """
        await asyncio.gather(self.outbound_loop(), self.inbound_loop(), return_exceptions=True)

    async def inbound_loop(self):
        """ Reads messages from the GNSS client
        and writes them to the outbound queue """
        while True:
            await self.read_message()

    async def outbound_loop(self):
        """ Reads messages from the outbound queue
        and writes the raw bytes to the GNSS client """
        while True:
            await self.write_message()

    async def read_message(self):
        """ Reads, classifies, and parses input from the GNSS client stream """
        (header, protocol) = self.__classifier.classify(self.__gnss_client)
        reader = self.__reader_provider.get_reader(protocol)
        parser = self.__parser_provider.get_parser(protocol)
        frame = reader.read_frame(header, self.__gnss_client)
        msg = parser.parse(frame)
        message = Message(proto=protocol, header=header, frame=frame, msg=msg)
        await self.__inbound_queue.put(message)

    async def write_message(self):
        """ Writes messages as byte strings to the GNSS client input """
        message = await self.__outbound_queue.get()
        self.__gnss_client.write(message.frame)
