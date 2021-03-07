import io
import unittest

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor

from xhoundpi.async_ext import run_sync
from xhoundpi.message import Message
from xhoundpi.proto_class import ProtocolClass
from xhoundpi.gnss_service_iface import IGnssService

import xhoundpi.gnss_service_decorators # pylint: disable=unused-import

class StubGnssService(IGnssService):

    def __init__(self):
        self.read = 0
        self.write = 0

    async def read_message(self) -> Message:
        self.read += 1
        return Message(proto=ProtocolClass.NMEA, payload=bytes(self.read))

    async def write_message(self, message: Message) -> int:
        self.write += 1
        return self.write

class test_GnssServiceWithTraces(unittest.TestCase):

    def test_tracing(self):
        # TODO find a better way to format and check the spans as we start adopting the telemetry
        output = io.StringIO()
        formatter = lambda span: span.name
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(SimpleExportSpanProcessor(ConsoleSpanExporter(out=output, formatter=formatter)))

        tracer = trace.get_tracer("test_tracer")

        gnss_service = StubGnssService()
        gnss_service_with_traces = gnss_service.with_traces(tracer)

        self.assertEqual(gnss_service.read, 0)
        self.assertEqual(gnss_service.write, 0)

        self.assertEqual(run_sync(gnss_service_with_traces.read_message()), Message(proto=ProtocolClass.NMEA, payload=bytes(1)))

        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 0)
        self.assertEqual(output.getvalue(), "read")

        self.assertEqual(run_sync(gnss_service_with_traces.write_message(Message(proto=ProtocolClass.NMEA))), 1)

        self.assertEqual(gnss_service.read, 1)
        self.assertEqual(gnss_service.write, 1)
        self.assertEqual(output.getvalue(), "readwrite")
