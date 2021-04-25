""" Event bus module based on RxPY library """

import asyncio
import functools

import rx
from rx.subject.subject import Subject
from rx.disposable import Disposable

from .queue_decorators import with_callback # pylint: disable=unused-import
from .queue_ext import get_forever_async # pylint: disable=unused-import

class EventBus:
    """ EventBus types """

    # from https://blog.oakbits.com/rxpy-and-asyncio.html
    @staticmethod
    def from_async_queue(queue, loop = None) -> rx.core.typing.Observable :
        """ Creates an observable from dequeueing an async queue """
        # pylint: disable=broad-except
        if loop is None:
            loop = asyncio.get_event_loop()

        def on_subscribe(observer, scheduler):
            # pylint: disable=unused-argument
            queue_with_callback = queue.with_callback(observer.on_next)

            async def _aio_sub():
                try:
                    while True:
                        await queue_with_callback.get_forever_async()
                except Exception as exception:
                    loop.call_soon(functools.partial(observer.on_error, exception))

            task = asyncio.ensure_future(_aio_sub(), loop=loop)

            def on_subscriber_disposed():
                task.cancel()
            return Disposable(on_subscriber_disposed)

        subject = Subject()
        rx.create(on_subscribe).subscribe(subject)
        return subject
