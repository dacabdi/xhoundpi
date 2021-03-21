# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest

from unittest.mock import Mock

from xhoundpi.gnss_client import IGnssClient
from xhoundpi.metric import ValueMetric
import xhoundpi.gnss_client_decorators # pylint: disable=unused-import

class StubGnssClient(IGnssClient):

    def __init__(self, data: bytes):
        self.on_read_data = data
        self.last_written = None

    def read(self, size) -> bytes:
        return self.on_read_data

    def write(self, data: bytes) -> int:
        self.last_written = data
        return len(data)

class test_GnssClientWithMetrics(unittest.TestCase):

    def test_count_read_write_bytes(self):
        client = StubGnssClient(b'\xff')
        hook = Mock()
        read = ValueMetric('GnssClientReadBytes', [hook])
        written = ValueMetric('GnssClientWrittenBytes', [hook])
        decorated = client.with_metrics(cbytes_read=read, cbytes_written=written) # pylint: disable=no-member

        self.assertEqual(read.value, 0)
        self.assertEqual(written.value, 0)

        # NOTE the decorator should measure the actual size read;
        # we cannot guarantee that the underlying transport implementation
        # will block if there are less bytes available than demanded

        self.assertEqual(decorated.read(10), b'\xff')
        self.assertEqual(read.value, 1)
        hook.assert_called_with('GnssClientReadBytes', 1)

        client.on_read_data = b'\x01\x02\x03'
        self.assertEqual(decorated.read(10), b'\x01\x02\x03')
        self.assertEqual(read.value, 4)
        hook.assert_called_with('GnssClientReadBytes', 4)

        self.assertEqual(decorated.write(b'\xff'), 1)
        self.assertEqual(client.last_written, b'\xff')
        self.assertEqual(written.value, 1)
        hook.assert_called_with('GnssClientWrittenBytes', 1)

        self.assertEqual(decorated.write(b'\x01\x02\x03'), 3)
        self.assertEqual(client.last_written, b'\x01\x02\x03')
        self.assertEqual(written.value, 4)
        hook.assert_called_with('GnssClientWrittenBytes', 4)
