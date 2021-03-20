# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import io
import unittest
import uuid

from typing import Tuple

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor

from xhoundpi.status import Status
from xhoundpi.async_ext import run_sync
from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.gnss_service_iface import IGnssService

import xhoundpi.gnss_service_decorators # pylint: disable=unused-import

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
        return self.written

class test_GnssServiceWithEvents(unittest.TestCase):

    def test_read_success(self):
        self.assertEqual(True, True)

class test_GnssServiceWithTraces(unittest.TestCase):

    def test_tracing(self):
        # TODO find a better way to format and check the spans as we start adopting the telemetry
        msg = Message(proto=ProtocolClass.NMEA, payload=bytes(1), message_id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'))
        output = io.StringIO()
        formatter = lambda span: span.name
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(SimpleExportSpanProcessor(ConsoleSpanExporter(out=output, formatter=formatter)))

        tracer = trace.get_tracer("test_tracer")

        gnss_service = StubGnssService()
        gnss_service_with_traces = gnss_service.with_traces(tracer) # pylint: disable=no-member

        self.assertEqual(gnss_service.read, 0)
        self.assertEqual(gnss_service.write, 0)
        self.assertEqual(run_sync(gnss_service_with_traces.read_message()), (Status.OK(), msg))
        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 0)
        self.assertEqual(output.getvalue(), "read")
        self.assertEqual(run_sync(gnss_service_with_traces.write_message(msg)), (Status.OK(), 1))
        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 1)
        self.assertEqual(output.getvalue(), "readwrite")
