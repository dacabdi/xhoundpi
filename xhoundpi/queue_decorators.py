''' asyncio Queue decorators '''

import asyncio
from typing import Awaitable

from .monkey_patching import add_method

@add_method(asyncio.queues.Queue)
def with_transform(self, transform):
    ''' Provides decorated queue that applies transformations to dequeued items '''
    return AsyncQueueWithGetTransform(self, transform)

@add_method(asyncio.queues.Queue)
def with_callback(self, callback):
    ''' Provides decorated queue that passes the result to an async callback every time '''
    return AsyncQueueWithCallback(self, callback)

class AsyncQueueWithGetTransform(asyncio.queues.Queue):
    ''' Queue decorator that performs a transformation
    before returning the dequeued item '''

    # pylint: disable=super-init-not-called
    def __init__(self, inner, transform):
        self._inner = inner
        self._transform = transform

    async def get(self):
        ''' Get the item async, apply transform, and return '''
        item = await self._inner.get()
        result = self._transform(item)
        if isinstance(result, Awaitable):
            return await result
        return result

    def get_nowait(self):
        ''' Get the item sync, apply transform, and return '''
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

class AsyncQueueWithCallback(asyncio.queues.Queue):
    ''' Queue decorator that calls a method upon dequeueing each item '''

    # pylint: disable=super-init-not-called
    def __init__(self, inner, callback):
        # pylint : disable=super-init-not-called
        self._inner = inner
        self._callback = callback

    async def get(self):
        ''' Get the item async, pass to callback, and return '''
        item = await self._inner.get()
        self._callback(item)
        return item

    def get_nowait(self):
        ''' Get the item sync, pass to callback, and return '''
        item = self._inner.get_nowait()
        self._callback(item)
        return item

    # Iterability requires explicit dunder methods

    def __iter__(self):
        return self.__dict__['_inner'].__iter__()

    def __next__(self):
        return self.__dict__['_inner'].__next__()

    # Live intercept properties and methods access

    def __getattr__(self, name):
        return getattr(self.__dict__['_inner'], name)

    def __setattr__(self, name, value):
        if name in ('_inner', '_callback'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_inner'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_inner'], name)
