""" Runner module for GNSS service implementations """

import asyncio

from .gnss_service import IGnssService
from .async_ext import loop_forever_async

class GnssServiceRunner:
    """ Gnss service runner reads/writes from in/out-bound queues"""

    def __init__(
        self,
        gnss_service: IGnssService,
        inbound_queue: asyncio.queues.Queue,
        outbound_queue: asyncio.queues.Queue):
        self.__gnss_service = gnss_service
        self.__inbound_qeue = inbound_queue
        self.__outbound_queue = outbound_queue

    async def run(self):
        """ Run inbound and outbound data flows in a loop """
        await asyncio.gather(
            loop_forever_async(self.__inbound),
            loop_forever_async(self.__outbound))

    async def __inbound(self):
        message = await self.__gnss_service.read_message()
        await self.__inbound_qeue.put(message)

    async def __outbound(self):
        message = await self.__outbound_queue.get()
        await self.__gnss_service.write_message(message)
