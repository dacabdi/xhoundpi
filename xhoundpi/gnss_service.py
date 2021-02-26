""" GNSS client """

import asyncio
from asyncio.coroutines import coroutine
from .proto_parser import IProtocolClassifier, IProtocolParserProvider
from .gnss_client import IGnssClient
from .message import Message

class GnssService():
    """ Gnss service """

    def __init__(
        self,
        inbound_queue: asyncio.queues.Queue,
        outbound_queue: asyncio.queues.Queue,
        gnss_client: IGnssClient,
        classifier: IProtocolClassifier,
        parser_provider: IProtocolParserProvider
        ):
        self.inbound_queue = inbound_queue
        self.outbound_queue = outbound_queue
        self.gnss_client = gnss_client
        self.classifier = classifier
        self.parser_provider = parser_provider

    async def run(self):
        return asyncio.gather(self.inbound_loop(), self.outbound_loop())

    async def inbound_loop(self):
        while True:
            await self.read_message()

    async def outbound_loop(self):
        while True:
            await self.write_message()

    async def read_message(self):
        (header, protocol) = self.classifier.classify(self.gnss_client)
        (raw_payload, payload) = self.parser_provider.get_parser(protocol).parse(self.gnss_client)
        message = Message(proto=protocol, header=header, raw=raw_payload, msg=payload)
        await self.inbound_queue.put(message)

    async def write_message(self):
        message = await self.outbound_queue.get()
        payload = message.header + message.raw
        self.gnss_client.write(payload)