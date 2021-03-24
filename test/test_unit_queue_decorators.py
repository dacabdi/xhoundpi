# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import unittest.mock
import asyncio
from asyncio.tasks import wait_for

import asynctest

import xhoundpi.queue_decorators # pylint: disable=unused-import
from xhoundpi.async_ext import run_sync

class test_AsyncQueueWithGetTransform(unittest.TestCase):

    def test_get_with_non_awaitable_transform(self):

        transform = unittest.mock.MagicMock(return_value='transformed')
        queue = asyncio.queues.Queue()
        queue_with_transform = queue.with_transform(transform) # pylint: disable=no-member

        # pulling the item through decorated should affect the result
        queue_with_transform.put_nowait('item1')
        item1 = run_sync(queue_with_transform.get())

        # pulling the item through NON-decorated should NOT affect the result
        queue.put_nowait('item2')
        item2 = run_sync(queue.get())

        self.assertEqual(item1, 'transformed')
        self.assertEqual(item2, 'item2')
        self.assertEqual(queue_with_transform.qsize(), 0)
        transform.assert_called_once_with('item1')

    def test_get_with_awaitable_transform(self):
        async def callback(_):
            return 'transformed'
        queue = asyncio.queues.Queue()
        queue_with_transform = queue.with_transform(callback) # pylint: disable=no-member

        # pulling the item through decorated should affect the result
        queue_with_transform.put_nowait('item1')
        item1 = run_sync(queue_with_transform.get())

        # pulling the item through NON-decorated should NOT affect the result
        queue.put_nowait('item2')
        item2 = run_sync(queue.get())

        self.assertEqual(item1, 'transformed')
        self.assertEqual(item2, 'item2')
        self.assertEqual(queue_with_transform.qsize(), 0)

class test_AsyncQueueWithGetCallback(unittest.TestCase):

    def test_get(self):

        callback = unittest.mock.MagicMock()
        queue = asyncio.queues.Queue()
        queue_with_callback = queue.with_callback(callback) # pylint: disable=no-member

        queue_with_callback.put_nowait('item1')
        item1 = run_sync(queue_with_callback.get())

        queue.put_nowait('item2')
        item2 = run_sync(queue.get())

        self.assertEqual(item1, 'item1')
        self.assertEqual(item2, 'item2')
        self.assertEqual(queue_with_callback.qsize(), 0)
        callback.assert_called_once_with('item1')

    def test_get_with_coroutine(self):

        callback = asynctest.CoroutineMock()
        queue = asyncio.queues.Queue()
        queue_with_callback = queue.with_callback(callback) # pylint: disable=no-member

        self.assertTrue(asyncio.iscoroutinefunction(callback))

        queue_with_callback.put_nowait('item1')
        item1 = run_sync(queue_with_callback.get())

        queue.put_nowait('item2')
        item2 = run_sync(queue.get())

        self.assertEqual(item1, 'item1')
        self.assertEqual(item2, 'item2')
        self.assertEqual(queue_with_callback.qsize(), 0)
        callback.assert_called_once_with('item1')

    def test_get_forever_until_cancelled(self):
        callback = asynctest.CoroutineMock()
        queue = asyncio.queues.Queue()
        queue_with_callback = queue.with_callback(callback) # pylint: disable=no-member

        loop = asyncio.get_event_loop()
        task = loop.create_task(queue_with_callback.get_forever_async())
        self.assertFalse(task.done())

        run_sync(queue_with_callback.put('item1'))
        self.assertFalse(task.done())
        callback.assert_called_once_with('item1')

        run_sync(queue_with_callback.put('item2'))
        self.assertFalse(task.done())
        callback.assert_called_with('item2')

        task.cancel()
        with self.assertRaises(asyncio.exceptions.CancelledError):
            run_sync(wait_for(task, 1))
