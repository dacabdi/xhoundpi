import unittest
import unittest.mock
import asyncio

import xhoundpi.queue_decorators
from xhoundpi.async_ext import run_sync

class test_AsyncQueueWithGetTransform(unittest.TestCase):

    def test_get(self):

        transform = unittest.mock.MagicMock(return_value='transformed')
        queue = asyncio.queues.Queue()
        queue_with_transform = queue.with_transform(transform)

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
