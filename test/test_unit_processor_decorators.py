# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import unittest
import uuid
from typing import Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch

import structlog
from structlog.testing import capture_logs

import xhoundpi.processor_decorators # pylint: disable=unused-import
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.status import Status
from xhoundpi.async_ext import run_sync
from xhoundpi.processor import IProcessor
from xhoundpi.metric import LatencyMetric, SuccessCounterMetric

from .time_utils import FakeStopWatch
from .log_utils import setup_test_event_logger

def setUpModule():
    setup_test_event_logger()

class StubProcessor(IProcessor):

    def __init__(self, result: Tuple[Status, Message]):
        self.result = result

    async def process(self, message: Message) -> Tuple[Status, Message]:
        return self.result

class test_ProcessorWithEvents(unittest.TestCase):

    def test_process_success(self):
        processor = StubProcessor((Status.OK(), Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None)))
        logger = structlog.get_logger()
        decorated = processor.with_events(logger) # pylint: disable=no-member

        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')
        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, transformed_msg = run_sync(decorated.process(Message(
                message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                proto=ProtocolClass.UBX,
                payload=None)))

        self.assertEqual(status, Status.OK())
        self.assertEqual(transformed_msg, Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None))
        self.assertEqual(capture, [
            {
                'opcode': 1,
                'opcode_name': 'BeginProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'opcode': 2,
                'opcode_name': 'EndProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

    def test_process_double_decorated_processor_id(self):
        processor = StubProcessor((Status.OK(), Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None)))
        logger = structlog.get_logger()
        decorated = processor.with_events(logger).with_events(logger) # pylint: disable=no-member

        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')
        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, transformed_msg = run_sync(decorated.process(Message(
                message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                proto=ProtocolClass.UBX,
                payload=None)))

        self.assertEqual(status, Status.OK())
        self.assertEqual(transformed_msg, Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None))
        self.assertEqual(capture, [
            {
                'opcode': 1,
                'opcode_name': 'BeginProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'opcode': 1,
                'opcode_name': 'BeginProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'opcode': 2,
                'opcode_name': 'EndProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'opcode': 2,
                'opcode_name': 'EndProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

    def test_process_failed(self):
        processor = StubProcessor((
            Status(RuntimeError('Something happened in the way of heaven')),
            Message(
                message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                proto=ProtocolClass.UBX,
                payload=None)))
        logger = structlog.get_logger()
        decorated = processor.with_events(logger) # pylint: disable=no-member

        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')
        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, transformed_msg = run_sync(decorated.process(Message(
                message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
                proto=ProtocolClass.UBX,
                payload=None)))

        self.assertEqual(status, Status(RuntimeError('Something happened in the way of heaven')))
        self.assertEqual(transformed_msg, Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None))
        self.assertEqual(capture, [
            {
                'opcode': 1,
                'opcode_name': 'BeginProcess',
                'success': True,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'opcode': 2,
                'opcode_name': 'EndProcess',
                'success': False,
                'processor_id' : 'StubProcessor',
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'error',
                'details': 'Something happened in the way of heaven',
                'event': 'ProcessorAction',
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

@dataclass
class TestData:
    service: StubProcessor
    decorated: IProcessor
    hook: Mock
    stopwatch: FakeStopWatch
    counter: SuccessCounterMetric
    latency: LatencyMetric

class test_ProcessorWithMetrics(unittest.TestCase):

    def create_and_decorate(self, result: Tuple[Status, Message]):
        self.maxDiff = None
        service = StubProcessor(result)
        hook = Mock()
        stopwatch = FakeStopWatch()
        counter = SuccessCounterMetric('counter', [hook])
        latency = LatencyMetric('latency', stopwatch, [hook])
        stopwatch.elapsed = 0.5
        decorated = service.with_metrics(counter, latency) # pylint: disable=no-member
        return TestData(
            service=service,
            decorated=decorated,
            hook=hook,
            stopwatch=stopwatch,
            counter=counter,
            latency=latency,)

    def make_result(self, status: Status): # pylint: disable=no-self-use
        return (status, Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None))

    def assertMetrics(self, tdata: TestData, success, failure, latency):
        self.assertEqual(tdata.counter.success, success)
        self.assertEqual(tdata.counter.failure, failure)
        self.assertEqual(tdata.latency.value, latency)
        tdata.hook.assert_any_call(f'{tdata.counter.dimension}_success', success)
        tdata.hook.assert_any_call(f'{tdata.counter.dimension}_failure', failure)
        tdata.hook.assert_any_call(f'{tdata.latency.dimension}', latency)

    def test_process_success(self):
        tdata = self.create_and_decorate(self.make_result(Status.OK()))

        self.assertEqual(tdata.latency.value, float('inf'))
        status, message = run_sync(tdata.decorated.process(Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None)))
        self.assertEqual((status, message), self.make_result(Status.OK()))
        self.assertMetrics(tdata, 1, 0, 0.5)

        tdata.stopwatch.elapsed = 10.5
        status, message = run_sync(tdata.decorated.process(Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None)))
        self.assertEqual((status, message), self.make_result(Status.OK()))
        self.assertMetrics(tdata, 2, 0, 10.5)

    def test_process_failed(self):
        tdata = self.create_and_decorate(self.make_result(Status(RuntimeError('Whoops!'))))

        self.assertEqual(tdata.latency.value, float('inf'))
        status, message = run_sync(tdata.decorated.process(Message(
            message_id=uuid.UUID('12345678-1234-5678-1234-567812345678'),
            proto=ProtocolClass.UBX,
            payload=None)))
        self.assertEqual((status, message), self.make_result(Status(RuntimeError('Whoops!'))))
        self.assertMetrics(tdata, 0, 1, 0.5)
