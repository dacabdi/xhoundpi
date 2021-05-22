''' Event bus module based on RxPY library '''

import asyncio
from dataclasses import dataclass
import functools
from typing import Any, Callable, Union
import uuid
from datetime import datetime as dt

import rx
import rx.core.typing as rxtyping
from rx.subject.subject import Subject
from rx.disposable.disposable import Disposable

from .queue_decorators import with_callback # pylint: disable=unused-import
from .queue_ext import get_forever_async # pylint: disable=unused-import

@dataclass
class Event:
    '''
    Event payload with metadata
    '''
    id: uuid.UUID # pylint: disable=invalid-name
    topic: str
    timestamp: dt
    offset: int
    payload: Any

class EventTopic(rxtyping.Observable):
    '''
    Represents a producer/subscriber named channel
    '''

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name: str, timestamp: Callable[[], dt]):
        self.__name = name
        self.__timestamp = timestamp
        self.__offset = -1
        self.__lock = asyncio.Lock()
        self.__queue = asyncio.Queue()
        self.__loop = asyncio.get_event_loop()
        self.__observable = rx.create(self.__on_subscribe)
        self.__subject = Subject()
        self.__subject_token = self.__observable.subscribe(self.__subject)

    @property
    def name(self):
        '''
        Topic identifier
        '''
        return self.__name

    @property
    def offset(self):
        '''
        Current topic offset
        '''
        return self.__offset

    async def publish(self, item: Any) -> None:
        '''
        Publish a message to the topic
        '''
        async with self.__lock:
            self.__offset += 1
            await self.__queue.put(Event(
                id=uuid.uuid4(),
                topic=self.name,
                timestamp=self.__timestamp(),
                offset=self.__offset,
                payload=item))

    # pylint: disable=arguments-differ
    def subscribe(self,
            observer: Union[rxtyping.Observer, rxtyping.OnNext, None] = None,
            on_error: Union[rxtyping.OnError, None] = None,
            on_completed: Union[rxtyping.OnCompleted, None] = None,
            on_next: Union[rxtyping.OnNext, None] = None,
            *, scheduler: Union[rxtyping.Scheduler, None] = None) \
            -> rxtyping.Disposable:
        # pylint: disable=too-many-function-args
        return self.__subject.subscribe(observer,
            on_error, on_completed, on_next,
            scheduler=scheduler)

    def __del__(self):
        # unsubcribe to kill the task
        self.__subject_token.dispose()

    # from https://blog.oakbits.com/rxpy-and-asyncio.html
    def __on_subscribe(self,
            observer: Union[rxtyping.Observer, rxtyping.OnNext, None], _)\
            -> rxtyping.Disposable:
        # pylint: disable=no-member
        queue = self.__queue.with_callback(observer.on_next) # type: ignore
        async def _aio_sub():
            try:
                while True:
                    await queue.get_forever_async()
            except Exception as exception: # pylint: disable=broad-except
                self.__loop.call_soon(functools.partial(observer.on_error, exception))
        task = asyncio.ensure_future(_aio_sub(), loop=self.__loop)
        task.set_name(self.__name)
        return Disposable(task.cancel) # type: ignore
