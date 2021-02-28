""" asyncio Queue extensions """

from asyncio.queues import Queue
from typing import Coroutine

async def read_forever_async(queue: Queue, on_item: Coroutine):
    """ Reads the queue forever and passes items to the on_item callback """
    while True:
        item = await queue.get()
        await on_item(item)
