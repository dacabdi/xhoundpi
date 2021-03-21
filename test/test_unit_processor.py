# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import unittest
import uuid

from xhoundpi.proto_class import ProtocolClass
from xhoundpi.message import Message
from xhoundpi.status import Status
from xhoundpi.async_ext import run_sync
from xhoundpi.processor import NullProcessor

class test_NullProcessor(unittest.TestCase):

    def test_process_should_passthrough(self):
        processor = NullProcessor()
        message = Message(
            message_id=uuid.UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
            proto=ProtocolClass.NONE,
            payload=None)

        status, transformed_msg = run_sync(processor.process(message))

        self.assertEqual(status, Status.OK())
        self.assertEqual(transformed_msg, message)
