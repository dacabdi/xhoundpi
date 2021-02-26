""" GNSS client """

import asyncio
from .proto_parser import IProtocolClassifier, IProtocolParserProvider
from .gnss_client import IGnssClient
from .message import Message

class GnssService():
    """ Gnss service facade """

    def __init__(
        self,
        inbound_queue: asyncio.queues.Queue,
        outbound_queue: asyncio.queues.Queue,
        gnss_client: IGnssClient,
        classifier: IProtocolClassifier,
        parser_provider: IProtocolParserProvider
        ): # pylint: disable=too-many-arguments
        self.inbound_queue = inbound_queue
        self.outbound_queue = outbound_queue
        self.gnss_client = gnss_client
        self.classifier = classifier
        self.parser_provider = parser_provider

    async def run(self):
        """ Coroutine that runs the inbound and outbound queue processing loops """
        return asyncio.gather(self.inbound_loop(), self.outbound_loop())

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
        (header, protocol) = self.classifier.classify(self.gnss_client)
        (raw_payload, payload) = self.parser_provider.get_parser(protocol).parse(self.gnss_client)
        message = Message(proto=protocol, header=header, raw=raw_payload, msg=payload)
        await self.inbound_queue.put(message)

    async def write_message(self):
        """ Writes messages as byte strings to the GNSS client input """
        message = await self.outbound_queue.get()
        payload = message.header + message.raw
        self.gnss_client.write(payload)
