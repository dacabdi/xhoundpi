# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import io
import uuid
import unittest

from typing import Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch

import structlog
from structlog.testing import capture_logs

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from xhoundpi.status import Status
from xhoundpi.async_ext import run_sync
from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.gnss_service_iface import IGnssService
from xhoundpi.metric import LatencyMetric, SuccessCounterMetric

import xhoundpi.gnss_service_decorators # pylint: disable=unused-import

from .time_utils import FakeStopWatch
from .log_utils import setup_test_event_logger

def setUpModule():
    setup_test_event_logger()

class StubGnssService(IGnssService):

    def __init__(self):
        self.read = 0
        self.write = 0
        self.return_read = None
        self.return_written = None

    async def read_message(self) -> Tuple[Status, Message]:
        self.read += 1
        return self.return_read

    async def write_message(self, message: Message) -> Tuple[Status, int]:
        self.write += 1
        return self.return_written

class test_GnssServiceWithEvents(unittest.TestCase):

    def create_and_decorate(self):
        self.maxDiff = None
        logger = structlog.get_logger()
        service = StubGnssService()
        decorated = service.with_events(logger) # pylint: disable=no-member
        return service, decorated

    def test_read_success(self):
        service, decorated = self.create_and_decorate()
        service.return_read = (
            Status.OK(),
            Message(
                message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=None))
        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')

        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, message = run_sync(decorated.read_message())

        self.assertEqual(status, Status.OK())
        self.assertEqual(message, Message(
                message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=None))
        self.assertEqual(capture, [
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'GnssServiceAction',
                'opcode': 1,
                'opcode_name': 'BeginRead',
                'success': True,
                'message_id': '00000000-0000-0000-0000-000000000000',
                'protocol' : 0,
                'protocol_name' : 'NONE',
                'schema_ver' : 1
            },
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'GnssServiceAction',
                'opcode': 2,
                'opcode_name': 'EndRead',
                'success': True,
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

    def test_read_failed(self):
        service, decorated = self.create_and_decorate()
        service.return_read = (Status(RuntimeError('This parrot is gone to meet its maker')), None)
        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')

        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, message = run_sync(decorated.read_message())

        # NOTE the event should collect the exception
        self.assertEqual(status, Status(RuntimeError('This parrot is gone to meet its maker')))
        self.assertEqual(message, None)
        self.assertEqual(capture, [
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'GnssServiceAction',
                'opcode': 1,
                'opcode_name': 'BeginRead',
                'success': True,
                'message_id': '00000000-0000-0000-0000-000000000000',
                'protocol' : 0,
                'protocol_name' : 'NONE',
                'schema_ver' : 1
            },
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'error',
                'details': 'This parrot is gone to meet its maker',
                'event': 'GnssServiceAction',
                'opcode': 2,
                'opcode_name': 'EndRead',
                'success': False,
                'message_id': '00000000-0000-0000-0000-000000000000',
                'protocol' : 0,
                'protocol_name' : 'NONE',
                'schema_ver' : 1,
                'exc_info': True
            }
        ])

    def test_write_success(self):
        service, decorated = self.create_and_decorate()
        service.return_written = (Status.OK(), 10)
        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')
        msg = Message(
                message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=None)

        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, cbytes = run_sync(decorated.write_message(msg))

        self.assertEqual(status, Status.OK())
        self.assertEqual(cbytes, 10)
        self.assertEqual(capture, [
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'GnssServiceAction',
                'opcode': 3,
                'opcode_name': 'BeginWrite',
                'success': True,
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '10 bytes',
                'event': 'GnssServiceAction',
                'opcode': 4,
                'opcode_name': 'EndWrite',
                'success': True,
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

    def test_write_failed(self):
        service, decorated = self.create_and_decorate()
        service.return_written = (Status(RuntimeError('This parrot is gone to meet its maker')), 0)
        activity_id = uuid.UUID('{11111111-2222-3333-4444-555555555555}')
        msg = Message(
                message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
                proto=ProtocolClass.UBX,
                payload=None)

        with patch('uuid.uuid4', return_value=activity_id), capture_logs() as capture:
            status, cbytes = run_sync(decorated.write_message(msg))

        self.assertEqual(status, Status(RuntimeError('This parrot is gone to meet its maker')))
        self.assertEqual(cbytes, 0)
        self.assertEqual(capture, [
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'info',
                'details': '',
                'event': 'GnssServiceAction',
                'opcode': 3,
                'opcode_name': 'BeginWrite',
                'success': True,
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            },
            {
                'activity_id': '11111111-2222-3333-4444-555555555555',
                'log_level': 'error',
                'details': 'This parrot is gone to meet its maker',
                'event': 'GnssServiceAction',
                'opcode': 4,
                'opcode_name': 'EndWrite',
                'success': False,
                'message_id': '12345678-1234-5678-1234-567812345678',
                'protocol' : 1,
                'protocol_name' : 'UBX',
                'schema_ver' : 1
            }
        ])

@dataclass
class TestData: # pylint: disable=too-many-instance-attributes
    service: StubGnssService
    decorated: IGnssService
    hook: Mock
    rcounter: SuccessCounterMetric
    wcounter: SuccessCounterMetric
    stopwatch: FakeStopWatch
    rlatency: LatencyMetric
    wlatency: LatencyMetric

class test_GnssServiceWithMetrics(unittest.TestCase):

    def create_and_decorate(self):
        self.maxDiff = None
        service = StubGnssService()
        hook = Mock()
        rcounter = SuccessCounterMetric('gnss_read_counter', [hook])
        wcounter = SuccessCounterMetric('gnss_write_counter', [hook])
        stopwatch = FakeStopWatch()
        stopwatch.elapsed = 0.5
        rlatency = LatencyMetric('gnss_read_latency', stopwatch, [hook])
        wlatency = LatencyMetric('gnss_write_latency', stopwatch, [hook])
        decorated = service.with_metrics( # pylint: disable=no-member
            rcounter,
            wcounter,
            rlatency,
            wlatency)
        return TestData(
            service=service,
            decorated=decorated,
            hook=hook,
            rcounter=rcounter,
            wcounter=wcounter,
            stopwatch=stopwatch,
            rlatency=rlatency,
            wlatency=wlatency)

    def make_read_result(self, is_ok: bool): # pylint: disable=no-self-use
        return (Status(None if is_ok else RuntimeError('That\'s all folks')),
                Message(message_id=None, proto=None, payload=None))

    def make_write_result(self, is_ok: bool): # pylint: disable=no-self-use
        return (Status(None if is_ok else RuntimeError('That\'s all folks')), 1)

    # pylint: disable=too-many-arguments
    def assertCounters(self, tdata: TestData, rsuccess, rfailure, wsuccess, wfailure):
        self.assertEqual(tdata.rcounter.success, rsuccess)
        self.assertEqual(tdata.rcounter.failure, rfailure)
        self.assertEqual(tdata.wcounter.success, wsuccess)
        self.assertEqual(tdata.wcounter.failure, wfailure)
        tdata.hook.assert_any_call(f'{tdata.rcounter.dimension}_success', rsuccess)
        tdata.hook.assert_any_call(f'{tdata.rcounter.dimension}_failure', rfailure)
        tdata.hook.assert_any_call(f'{tdata.wcounter.dimension}_success', wsuccess)
        tdata.hook.assert_any_call(f'{tdata.wcounter.dimension}_failure', wfailure)

    def test_read_success(self):
        tdata = self.create_and_decorate()
        tdata.service.return_read = self.make_read_result(is_ok=True)

        self.assertCounters(tdata, 0, 0, 0, 0)
        self.assertEqual(tdata.rlatency.value, float('inf'))
        status, message = run_sync(tdata.decorated.read_message())
        self.assertEqual((status, message), self.make_read_result(is_ok=True))
        self.assertCounters(tdata, 1, 0, 0, 0)
        self.assertEqual(tdata.rlatency.value, 0.5)
        tdata.hook.assert_any_call('gnss_read_latency', 0.5)

    def test_read_failure(self):
        tdata = self.create_and_decorate()
        tdata.service.return_read = self.make_read_result(is_ok=False)

        self.assertCounters(tdata, 0, 0, 0, 0)
        self.assertEqual(tdata.rlatency.value, float('inf'))
        status, message = run_sync(tdata.decorated.read_message())
        self.assertEqual((status, message), self.make_read_result(is_ok=False))
        self.assertCounters(tdata, 0, 1, 0, 0)
        self.assertEqual(tdata.rlatency.value, 0.5)
        tdata.hook.assert_any_call('gnss_read_latency', 0.5)

    def test_write_success(self):
        tdata = self.create_and_decorate()
        tdata.service.return_written = self.make_write_result(is_ok=True)

        self.assertCounters(tdata, 0, 0, 0, 0)
        self.assertEqual(tdata.wlatency.value, float('inf'))
        status, cbytes = run_sync(tdata.decorated.write_message(Message(None, None, None)))
        self.assertEqual((status, cbytes), self.make_write_result(is_ok=True))
        self.assertCounters(tdata, 0, 0, 1, 0)
        self.assertEqual(tdata.wlatency.value, 0.5)
        tdata.hook.assert_any_call('gnss_write_latency', 0.5)

    def test_write_failure(self):
        tdata = self.create_and_decorate()
        tdata.service.return_written = self.make_write_result(is_ok=False)

        self.assertCounters(tdata, 0, 0, 0, 0)
        self.assertEqual(tdata.wlatency.value, float('inf'))
        status, cbytes = run_sync(tdata.decorated.write_message(Message(None, None, None)))
        self.assertEqual((status, cbytes), self.make_write_result(is_ok=False))
        self.assertCounters(tdata, 0, 0, 0, 1)
        self.assertEqual(tdata.wlatency.value, 0.5)
        tdata.hook.assert_any_call('gnss_write_latency', 0.5)

class test_GnssServiceWithTraces(unittest.TestCase):

    def test_tracing(self):
        # TODO find a better way to format and check the spans as we start adopting the telemetry
        msg = Message(proto=ProtocolClass.NMEA, payload=bytes(1), message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        output = io.StringIO()
        formatter = lambda span: span.name
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter(out=output, formatter=formatter)))

        tracer = trace.get_tracer("test_tracer")

        gnss_service = StubGnssService()
        gnss_service.return_read = (Status.OK(), Message(proto=ProtocolClass.NMEA, payload=bytes(1), message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}')))
        gnss_service.return_written = (Status.OK(), 10)
        gnss_service_with_traces = gnss_service.with_traces(tracer) # pylint: disable=no-member

        self.assertEqual(gnss_service.read, 0)
        self.assertEqual(gnss_service.write, 0)
        self.assertEqual(run_sync(gnss_service_with_traces.read_message()), (Status.OK(), msg))
        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 0)
        self.assertEqual(output.getvalue(), "read")
        self.assertEqual(run_sync(gnss_service_with_traces.write_message(msg)), (Status.OK(), 10))
        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 1)
        self.assertEqual(output.getvalue(), "readwrite")
