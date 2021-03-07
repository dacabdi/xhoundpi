import asyncio
from asyncio.tasks import wait_for
from tests.async_utils import wait_for_condition
import unittest

from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.async_ext import run_sync
from xhoundpi.gnss_service_iface import IGnssService
from xhoundpi.gnss_service_runner import GnssServiceRunner

from tests.async_utils import wait_for_condition, notify_condition

class StubGnssService(IGnssService):

    def __init__(self, read_condition):
        self.read = 0
        self.write = 0
        self.last_written = None
        self.last_read = None
        self.condition = read_condition

    async def read_message(self) -> Message:
        await wait_for_condition(self.condition)
        self.read += 1
        message = Message(proto=ProtocolClass.NMEA, payload=bytes(self.read))
        self.last_read = message
        return message

    async def write_message(self, message: Message) -> int:
        self.write += 1
        self.last_written = message
        return 1

class test_GnssServiceRunner(unittest.TestCase):

    def test_run(self):
        condition = asyncio.Condition()
        gnss_service = StubGnssService(condition)
        inbound_queue = asyncio.queues.Queue(3)
        outbound_queue = asyncio.queues.Queue(3)
        gnss_runner = GnssServiceRunner(gnss_service, inbound_queue, outbound_queue)

        loop = asyncio.get_event_loop()
        task = loop.create_task(gnss_runner.run())

        self.assertFalse(task.done())

        self.assertEqual(gnss_service.read, 0)
        self.assertEqual(gnss_service.write, 0)

        self.assertTrue(inbound_queue.empty())
        run_sync(notify_condition(condition))
        self.assertEqual(run_sync(inbound_queue.get()), Message(proto=ProtocolClass.NMEA, payload=bytes(1)))

        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 0)

        self.assertTrue(inbound_queue.empty())
        run_sync(notify_condition(condition))
        self.assertEqual(run_sync(inbound_queue.get()), Message(proto=ProtocolClass.NMEA, payload=bytes(2)))

        self.assertEqual(gnss_service.read, 2)
        self.assertEqual(gnss_service.write, 0)

        run_sync(outbound_queue.put(Message(proto=ProtocolClass.UBX, payload=b'\x01\x02')))
        self.assertEqual(gnss_service.read, 2)
        self.assertEqual(gnss_service.write, 1)
        self.assertTrue(outbound_queue.empty())

        run_sync(outbound_queue.put(Message(proto=ProtocolClass.UBX, payload=b'\x01\x02')))
        self.assertEqual(gnss_service.read, 2)
        self.assertEqual(gnss_service.write, 2)
        self.assertTrue(outbound_queue.empty())

        self.assertTrue(inbound_queue.empty())
        run_sync(notify_condition(condition))
        self.assertEqual(run_sync(inbound_queue.get()), Message(proto=ProtocolClass.NMEA, payload=bytes(3)))

        self.assertEqual(gnss_service.read, 3)
        self.assertEqual(gnss_service.write, 2)

        task.cancel()
        with self.assertRaises(asyncio.exceptions.CancelledError):
            run_sync(wait_for(task, 1))