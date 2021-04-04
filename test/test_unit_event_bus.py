# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import asyncio
import unittest

from unittest.mock import Mock, patch

from xhoundpi.event_bus import EventBus
from xhoundpi.async_ext import run_sync

class test_EventBus(unittest.TestCase):

    def test_from_queue(self): # pylint: disable=no-self-use
        subscriber = Mock()
        queue = asyncio.queues.Queue()
        event_bus = EventBus.from_async_queue(queue)
        disposable = event_bus.subscribe(on_next=subscriber)
        subscriber.assert_not_called()
        run_sync(queue.put("first"))
        subscriber.assert_called_once_with("first")
        run_sync(queue.put("second"))
        subscriber.assert_called_with("second")
        disposable.dispose()

    def test_exception(self): # pylint: disable=no-self-use
        on_next = Mock()
        on_error = Mock()
        queue = asyncio.queues.Queue()
        event_bus = EventBus.from_async_queue(queue)
        disposable = event_bus.subscribe(on_next=on_next, on_error=on_error)

        with patch('asyncio.queues.Queue.get', side_effect=Exception('Oops!')):
            run_sync(queue.put("first"))

        on_next.assert_not_called()
        self.assertEqual(["call(Exception('Oops!'))"],
            [str(arg) for arg in on_error.call_args_list])
        # ^ on_error.assert_called_once_with(Exception('Oops!'))
        disposable.dispose()
