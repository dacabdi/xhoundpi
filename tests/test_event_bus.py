import unittest
import unittest.mock
import asyncio

from rx import return_value

from xhoundpi.event_bus import EventBus
from xhoundpi.async_ext import run_sync

class test_EventBus(unittest.TestCase):

    def test_from_queue(self):
        subscriber = unittest.mock.MagicMock()
        queue = asyncio.queues.Queue()
        event_bus = EventBus.from_async_queue(queue)

        disposable = event_bus.subscribe(
            on_next=subscriber
        )

        subscriber.assert_not_called()

        run_sync(queue.put("first"))
        subscriber.assert_called_once_with("first")

        run_sync(queue.put("second"))
        subscriber.assert_called_with("second")

        disposable.dispose()
