""" Runner module for GNSS service implementations """
import asyncio

from structlog import get_logger

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
        self.__logger = get_logger(module=__class__.__name__)

    async def run(self):
        """ Run inbound and outbound data flows in a loop """
        self.__logger.info('gnss_service_run')
        return await asyncio.gather(
            loop_forever_async(self.__inbound),
            loop_forever_async(self.__outbound),
            return_exceptions=True)

    async def __inbound(self):
        self.__logger.debug('gnss_service_inbound_wait')
        try:
            message = await self.__gnss_service.read_message()
            await self.__inbound_qeue.put(message)
            self.__logger.debug('gnss_service_inbound_end')
            # TODO use better exception filtering
        except Exception: # pylint: disable=broad-except
            self.__logger.exception('gnss_service_inbound_end')
        finally:
            # workaround to force the queue to give up the loop to the getters
            # see https://github.com/aio-libs/janus/issues/82
            await asyncio.sleep(0)

    async def __outbound(self):
        message = await self.__outbound_queue.get()
        await self.__gnss_service.write_message(message)
