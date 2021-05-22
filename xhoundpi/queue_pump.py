''' Async pump for asyncio queues '''

from abc import ABC, abstractmethod

class IAsyncPump(ABC):
    ''' Interface for async pump implementations '''

    @abstractmethod
    async def run(self):
        ''' Runs the pump '''

class AsyncPump(IAsyncPump):
    ''' Async pump between two queues '''

    def __init__(self, input_queue, output_queue):
        self.__input = input_queue
        self.__output = output_queue

    async def run(self):
        ''' Passes over every item from input queue to output queue '''
        while True:
            item = await self.__input.get()
            await self.__output.put(item)
