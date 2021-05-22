''' asyncio Queue extensions '''

from asyncio.queues import Queue

from .monkey_patching import add_method

@add_method(Queue)
async def get_forever_async(self):
    ''' Reads the queue forever and passes items to the on_item callback '''
    while True:
        await self.get()
