""" asyncio Queue decorators """

import asyncio

from .monkey_patching import add_method

@add_method(asyncio.queues.Queue)
def with_transform(self, transform):
    """ Provides decorated queue that applies transformations to dequeued items """
    return AsyncQueueWithGetTransform(self, transform)

class AsyncQueueWithGetTransform():
    """ Queue decorator that performs a transformation
    before returning the dequeued item """

    def __init__(self, inner, transform):
        self._inner = inner
        self._transform = transform

    async def get(self):
        """ Get the item async, apply transform, and return """
        item = await self._inner.get()
        return self._transform(item)

    def get_nowait(self):
        """ Get the item sync, apply transform, and return """
        item = self._inner.get_nowait()
        return self._transform(item)

    # Iterability requires explicit dunder methods

    def __iter__(self):
        return self.__dict__['_inner'].__iter__()

    def __next__(self):
        return self.__dict__['_inner'].__next__()

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_transform'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
