import unittest
import asyncio

from xhoundpi.queue_pump import AsyncPump
from xhoundpi.async_ext import run_sync

class test_AsyncPump(unittest.TestCase):

    def test_run(self):
        in_queue = asyncio.queues.Queue()
        out_queue = asyncio.queues.Queue()
        pump = AsyncPump(input=in_queue, output=out_queue)

        loop = asyncio.get_event_loop()
        task = loop.create_task(pump.run())

        self.assertTrue(out_queue.empty())
        run_sync(in_queue.put("first item"))
        self.assertEqual(run_sync(out_queue.get()), "first item")
        run_sync(in_queue.put("second item"))
        self.assertEqual(run_sync(out_queue.get()), "second item")

        self.assertTrue(out_queue.empty())
        self.assertFalse(task.done())
